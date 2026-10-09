from pathlib import Path, PurePosixPath
from threading import RLock
from time import monotonic, sleep, time
from typing import Dict, List, Optional, Set, Tuple

from httpx import stream, RequestError
from p115client import P115Client, check_response
from p115client.exception import P115NotADirectoryError
from p115client.tool.attr import normalize_attr, get_id_to_path, get_attr
from p115client.tool.fs_files import fs_files_iter
from p115client.tool.iterdir import iter_files_with_path_skim

from app.chain.storage import StorageChain
from app.modules.filemanager.storages import transfer_process
from app.schemas import FileItem, StorageUsage
from app.schemas.exception import StorageQueryError
from app.sdk.config import global_vars, settings
from app.sdk.logging import logger

from .cache import IdPathCache, ItemIdCache
from .tools import RateLimiter, get_ios_ua_app


def _build_download_path(fileitem: FileItem, base_path: Path) -> Optional[Path]:
    """
    构造限制在目标目录内的下载路径
    """
    safe_name = PurePosixPath(str(fileitem.name or "").replace("\\", "/")).name
    if safe_name in ("", ".", ".."):
        return None
    local_path = base_path / safe_name
    try:
        local_path.resolve().relative_to(base_path.resolve())
    except ValueError:
        return None
    return local_path


class P115Api:
    """
    115 网盘基础操作类
    """

    def __init__(self, client: P115Client, disk_name: str):
        """
        初始化 115 网盘 API

        :param client: 115 网盘客户端实例
        :param disk_name: 网盘名称
        """
        self.client = client
        self._disk_name = disk_name
        self._id_cache: IdPathCache = IdPathCache(maxsize=4096)
        self._id_item_cache: ItemIdCache = ItemIdCache(maxsize=4096)
        self._folder_lock = RLock()
        self.transtype = {"move": "移动", "copy": "复制"}

        self._rename_call_counter = 0
        self._copy_call_counter = 0
        self._move_call_counter = 0
        self._delete_call_counter = 0
        self._get_pid_by_path_call_counter = 0

        self._get_item_rate_limiter = RateLimiter(
            max_calls=2, time_window=2.0, name="get_item"
        )
        self._delete_rate_limiter = RateLimiter(
            max_calls=1, time_window=2.0, name="delete"
        )
        self._get_pid_by_path_rate_limiter = RateLimiter(
            max_calls=1, time_window=1.0, name="get_pid_by_path"
        )
        self._rename_rate_limiter = RateLimiter(
            max_calls=1, time_window=2.0, name="rename"
        )
        self._move_rate_limiter = RateLimiter(max_calls=1, time_window=2.0, name="move")
        self._copy_rate_limiter = RateLimiter(max_calls=1, time_window=2.0, name="copy")
        self._list_rate_limiter = RateLimiter(max_calls=1, time_window=2.0, name="list")

        self._get_item_fail_records: Dict[str, Dict[str, float]] = {}
        self._get_item_blacklist: Dict[str, float] = {}

    def get_pid_by_path(self, path: Path) -> int:
        """
        通过文件夹路径获取文件夹 ID

        :param path (Path): 文件夹路径

        :return int: 目录 ID
        """
        try:
            if path.as_posix() == "/":
                return 0
            pid = self._id_cache.get_id_by_dir(directory=path.as_posix())
            if pid:
                return pid
            self._get_pid_by_path_rate_limiter.acquire()
            self._get_pid_by_path_call_counter = (
                self._get_pid_by_path_call_counter + 1
            ) % 2
            if self._get_pid_by_path_call_counter == 0:
                resp = self.client.fs_dir_getid(
                    path.as_posix(), **get_ios_ua_app(app=False)
                )
            else:
                resp = self.client.fs_dir_getid_app(path.as_posix(), **get_ios_ua_app())
            check_response(resp)
            pid = resp.get("id", -1)
            if pid == 0:
                resp = self.client.fs_makedirs_app(
                    path.as_posix(), pid=0, **get_ios_ua_app()
                )
                check_response(resp)
                pid = resp["cid"]
                self._id_cache.add_cache(id=int(pid), directory=path.as_posix())
                return pid
            if pid != 0:
                return pid
            return -1
        except Exception as e:
            logger.warn(f"【115Lite】获取文件夹ID失败: {str(e)}")
            file_item = self.get_item(path)
            if file_item:
                return int(file_item.fileid)
            return -1

    def iter_files(self, fileitem: FileItem) -> Optional[List[FileItem]]:
        """
        递归遍历文件夹

        :param fileitem (FileItem): 文件项，可以是文件或目录

        :return List: 文件项列表
        """
        if fileitem.type == "file":
            item = self.detail(fileitem)
            if item:
                return [item]
            return []
        if fileitem.path == "/":
            file_id = "0"
        else:
            file_id = fileitem.fileid
            if not file_id:
                file_id = self.get_pid_by_path(Path(fileitem.path))
            if file_id == -1:
                return None

        items = []
        try:
            for item in iter_files_with_path_skim(
                client=self.client,
                cid=file_id,
                with_ancestors=False,
                **get_ios_ua_app(),
            ):
                file_path = item["path"] + ("/" if item["is_dir"] else "")
                self._id_cache.add_cache(id=item["id"], directory=item["path"])
                self._id_item_cache.add_cache(
                    id=item["id"],
                    item={
                        "path": file_path,
                        "id": item["id"],
                        "size": item["size"],
                        "modify_time": None,
                        "pickcode": item["pickcode"],
                        "is_dir": item["is_dir"],
                    },
                )
                items.append(
                    FileItem(
                        storage=self._disk_name,
                        fileid=str(item["id"]),
                        parent_fileid=str(item["parent_id"]),
                        name=item["name"],
                        basename=Path(item["name"]).stem,
                        extension=Path(item["name"]).suffix[1:]
                        if not item["is_dir"]
                        else None,
                        type="dir" if item["is_dir"] else "file",
                        path=file_path,
                        size=item["size"] if not item["is_dir"] else None,
                        modify_time=None,
                        pickcode=item["pickcode"],
                    )
                )
        except Exception as e:
            logger.warn(f"【115Lite】递归遍历文件夹失败: {str(e)}")
            return None
        return items

    def list(self, fileitem: FileItem) -> Optional[List[FileItem]]:
        """
        浏览文件或目录

        :param fileitem (FileItem): 文件项，可以是文件或目录

        :return List: 文件项列表，如果是文件则返回包含该文件的列表，如果是目录则返回目录下的所有文件和子目录
        """
        self._list_rate_limiter.acquire()
        if fileitem.type == "file":
            item = self.detail(fileitem)
            if item:
                return [item]
            return []
        if fileitem.path == "/":
            file_id = "0"
        else:
            file_id = fileitem.fileid
            if not file_id:
                file_id = self.get_pid_by_path(Path(fileitem.path))
            if file_id == -1:
                return None

        items = []
        try:
            for data in fs_files_iter(
                self.client, file_id, cooldown=1.5, **get_ios_ua_app(app=False)
            ):
                logger.debug(f"【115Lite】浏览目录 {data}")
                for item in data.get("data", []):
                    item = normalize_attr(item)
                    path = f"{fileitem.path}{item['name']}"
                    file_path = path + ("/" if item["is_dir"] else "")
                    self._id_cache.add_cache(id=item["id"], directory=path)
                    self._id_item_cache.add_cache(
                        id=item["id"],
                        item={
                            "path": file_path,
                            "id": item["id"],
                            "size": item["size"],
                            "modify_time": item["ctime"],
                            "pickcode": item["pickcode"],
                            "is_dir": item["is_dir"],
                        },
                    )
                    items.append(
                        FileItem(
                            storage=self._disk_name,
                            fileid=str(item["id"]),
                            parent_fileid=str(item["parent_id"]),
                            name=item["name"],
                            basename=Path(item["name"]).stem,
                            extension=Path(item["name"]).suffix[1:]
                            if not item["is_dir"]
                            else None,
                            type="dir" if item["is_dir"] else "file",
                            path=file_path,
                            size=item["size"] if not item["is_dir"] else None,
                            modify_time=item["ctime"],
                            pickcode=item["pickcode"],
                        )
                    )
        except Exception as e:
            logger.warn(f"【115Lite】获取信息失败: {str(e)}")
            if isinstance(e, P115NotADirectoryError) and file_id and file_id != "0":
                try:
                    self._id_cache.remove(id=int(file_id))
                    self._id_item_cache.remove(id=int(file_id))
                except Exception:
                    pass
            try:
                storage_chain = StorageChain()
                fallback_dict = fileitem.model_dump(exclude={"storage"})
                if isinstance(e, P115NotADirectoryError):
                    fallback_dict["fileid"] = None
                fileitem = FileItem(
                    storage="u115",
                    **fallback_dict,
                )
                fallback_items = storage_chain.list_files(
                    fileitem=fileitem, recursion=False
                )
                if fallback_items:
                    result_items = []
                    for item in fallback_items:
                        if item.fileid:
                            self._id_cache.add_cache(
                                id=int(item.fileid), directory=item.path.rstrip("/")
                            )
                            self._id_item_cache.add_cache(
                                id=int(item.fileid),
                                item={
                                    "path": item.path,
                                    "id": int(item.fileid),
                                    "size": item.size,
                                    "modify_time": item.modify_time,
                                    "pickcode": item.pickcode,
                                    "is_dir": bool(item.type == "dir"),
                                },
                            )
                        result_item = FileItem(
                            storage=self._disk_name,
                            **item.model_dump(exclude={"storage"}),
                        )
                        result_items.append(result_item)
                    return result_items
            except Exception as e:
                logger.error(f"【115Lite】获取信息失败（原版）: {str(e)}")
            return None
        return items

    def create_folder(self, fileitem: FileItem, name: str) -> Optional[FileItem]:
        """
        创建目录

        :param fileitem (FileItem): 父目录文件项
        :param name (str): 要创建的目录名称

        :return FileItem: 创建成功返回目录文件项，失败返回 None
        """
        try:
            new_path = Path(fileitem.path) / name
            parent_id = self.get_pid_by_path(Path(fileitem.path))
            if parent_id == -1:
                return None
            payload = {
                "cname": name,
                "pid": parent_id,
            }
            resp = self.client.fs_mkdir(payload, **get_ios_ua_app(app=False))
            check_response(resp)
            logger.info(f"【115Lite】创建目录: {resp}")
            data = resp.get("cid", resp.get("file_id", None))
            if not data:
                logger.error(f"【115Lite】创建目录失败: {resp}")
                return None
            self._id_cache.add_cache(id=data, directory=new_path.as_posix())
            modify_time = int(time())
            self._id_item_cache.add_cache(
                id=data,
                item={
                    "path": new_path.as_posix(),
                    "id": data,
                    "size": None,
                    "modify_time": modify_time,
                    "pickcode": self.client.to_pickcode(data),
                    "is_dir": True,
                },
            )
            return FileItem(
                storage=self._disk_name,
                fileid=str(data),
                path=new_path.as_posix() + "/",
                name=name,
                basename=name,
                type="dir",
                modify_time=modify_time,
                pickcode=self.client.to_pickcode(data),
            )
        except Exception as e:
            logger.error(f"【115Lite】创建目录失败: {str(e)}")
            return None

    def get_folder(self, path: Path) -> Optional[FileItem]:
        """
        获取目录，如目录不存在则创建

        :param path (Path): 目录路径

        :return FileItem: 目录文件项，如果创建失败则返回 None
        """
        with self._folder_lock:
            return self._get_folder_unlocked(path)

    def _get_folder_unlocked(self, path: Path) -> Optional[FileItem]:
        path = path if path.is_absolute() else Path("/") / path
        try:
            folder = self.get_item_strict(path)
        except StorageQueryError as e:
            logger.error(f"【115Lite】查询目录失败: {path} - {e}")
            return None
        if folder:
            if folder.type == "dir":
                return folder
            logger.error(f"【115Lite】目标路径不是目录: {path}")
            return None
        if path.as_posix() == "/":
            return FileItem(
                storage=self._disk_name,
                fileid="0",
                path="/",
                name="",
                basename="",
                type="dir",
            )

        try:
            resp = self.client.fs_makedirs_app(
                path.as_posix(), pid=0, **get_ios_ua_app()
            )
            check_response(resp)
            logger.info(f"【115Lite】创建目录: {resp}")
            self._id_cache.add_cache(id=int(resp["cid"]), directory=path.as_posix())
            modify_time = int(time())
            self._id_item_cache.add_cache(
                id=resp["cid"],
                item={
                    "path": path.as_posix(),
                    "id": resp["cid"],
                    "size": None,
                    "modify_time": modify_time,
                    "pickcode": self.client.to_pickcode(resp["cid"]),
                    "is_dir": True,
                },
            )
            return FileItem(
                storage=self._disk_name,
                fileid=str(resp["cid"]),
                path=path.as_posix() + "/",
                name=path.name,
                basename=path.name,
                type="dir",
                modify_time=modify_time,
                pickcode=self.client.to_pickcode(resp["cid"]),
            )
        except Exception as e:
            logger.error(f"【115Lite】{path} 目录创建出现未知错误：{e}")
            return None

    def get_item(self, path: Path) -> Optional[FileItem]:
        """
        获取文件或目录，不存在返回 None
        如果连续三次调用都是同一个目录且 API 都返回不存在，则接下来的 15 秒内直接返回 None

        :param path (Path): 文件或目录路径

        :return FileItem: 文件项，如果不存在则返回 None
        """
        path_str = path.as_posix()
        now = monotonic()

        if path_str in self._get_item_blacklist:
            if now < self._get_item_blacklist[path_str]:
                return None
            else:
                del self._get_item_blacklist[path_str]

        cached_item = self._get_cached_item(path)
        if cached_item:
            return cached_item

        self._get_item_rate_limiter.acquire()

        try:
            return self._query_item(path)
        except FileNotFoundError:
            self._record_get_item_failure(path_str, now)
            return None
        except Exception:
            file_item = self._get_u115_item(path)
            if not file_item:
                self._record_get_item_failure(path_str, now)
                return None
            return file_item

    def get_item_strict(self, path: Path) -> Optional[FileItem]:
        """
        严格获取文件或目录，无法确认状态时抛出存储查询异常

        :param path (Path): 文件或目录路径

        :return FileItem: 文件项，确认不存在时返回 None

        :raises StorageQueryError: 网络、限流或接口异常导致无法确认文件状态
        """
        try:
            cached_item = self._get_cached_item(path)
            if cached_item:
                return cached_item

            self._get_item_rate_limiter.acquire()
            return self._query_item(path)
        except (FileNotFoundError, NotADirectoryError):
            return None
        except Exception as e:
            try:
                file_item = self._get_u115_item(path)
            except Exception as fallback_error:
                raise StorageQueryError(
                    f"【115Lite】查询文件信息失败: {path} - {e}; "
                    f"u115 降级查询失败: {fallback_error}"
                ) from fallback_error
            if file_item:
                logger.warning(
                    f"【115Lite】Web API 查询失败，已通过 u115 获取: {path}"
                )
                return file_item
            raise StorageQueryError(
                f"【115Lite】查询文件信息失败: {path} - {e}"
            ) from e

    def _get_u115_item(self, path: Path) -> Optional[FileItem]:
        """
        通过 u115 存储降级查询文件项并更新正缓存

        :param path (Path): 文件或目录路径

        :return FileItem: 文件项，未查询到时返回 None
        """
        file_item = StorageChain().get_file_item(storage="u115", path=path)
        if not file_item:
            return None

        path_str = path.as_posix()
        self._get_item_fail_records.pop(path_str, None)
        self._id_cache.add_cache(id=int(file_item.fileid), directory=path_str)
        self._id_item_cache.add_cache(
            id=int(file_item.fileid),
            item={
                "path": path_str,
                "id": int(file_item.fileid),
                "size": file_item.size,
                "modify_time": file_item.modify_time,
                "pickcode": file_item.pickcode,
                "is_dir": bool(file_item.type == "dir"),
            },
        )
        return FileItem(
            storage=self._disk_name,
            **file_item.model_dump(exclude={"storage"}),
        )

    def _get_cached_item(self, path: Path) -> Optional[FileItem]:
        """
        从正缓存获取文件项

        :param path (Path): 文件或目录路径

        :return FileItem: 缓存文件项，缓存未命中时返回 None
        """
        path_str = path.as_posix()
        file_id = self._id_cache.get_id_by_dir(path_str)
        if not file_id:
            return None

        item = self._id_item_cache.get_item(file_id)
        if not item:
            return None

        self._get_item_fail_records.pop(path_str, None)
        logger.debug(f"【115Lite】缓存获取: {item}")
        item_path = Path(item["path"])
        if item["is_dir"]:
            return FileItem(
                storage=self._disk_name,
                fileid=str(item["id"]),
                path=item_path.as_posix() + "/",
                name=item_path.name,
                basename=item_path.name,
                type="dir",
                modify_time=item["modify_time"],
                pickcode=item["pickcode"],
            )
        return FileItem(
            storage=self._disk_name,
            fileid=str(item["id"]),
            parent_fileid=None,
            name=item_path.name,
            basename=item_path.stem,
            extension=item_path.suffix[1:],
            type="file",
            path=item_path.as_posix(),
            size=item["size"],
            modify_time=item["modify_time"],
            pickcode=item["pickcode"],
        )

    def _query_item(self, path: Path) -> FileItem:
        """
        查询远端文件项并更新正缓存

        :param path (Path): 文件或目录路径

        :return FileItem: 查询到的文件项

        :raises FileNotFoundError: 文件或目录确认不存在
        """
        path_str = path.as_posix()
        try:
            file_id = get_id_to_path(
                client=self.client, path=path_str, **get_ios_ua_app(app=False)
            )
        except KeyError:
            file_id = get_id_to_path(
                client=self.client,
                path=path_str,
                refresh=True,
                **get_ios_ua_app(app=False),
            )
        file_item = get_attr(
            client=self.client, id=file_id, **get_ios_ua_app(app=False)
        )

        logger.debug(f"【115Lite】文件信息: {file_item}")
        self._get_item_fail_records.pop(path_str, None)
        self._id_cache.add_cache(id=file_item["id"], directory=path_str)
        self._id_item_cache.add_cache(
            id=file_item["id"],
            item={
                "path": path_str,
                "id": file_item["id"],
                "size": file_item["size"],
                "modify_time": file_item["mtime"],
                "pickcode": file_item["pickcode"],
                "is_dir": file_item["is_dir"],
            },
        )
        if file_item["is_dir"]:
            return FileItem(
                storage=self._disk_name,
                fileid=str(file_item["id"]),
                parent_fileid=str(file_item["parent_id"]),
                path=path_str + "/",
                name=file_item["name"],
                basename=file_item["name"],
                type="dir",
                modify_time=file_item["mtime"],
                pickcode=file_item["pickcode"],
            )
        return FileItem(
            storage=self._disk_name,
            fileid=str(file_item["id"]),
            parent_fileid=str(file_item["parent_id"]),
            name=file_item["name"],
            basename=path.stem,
            extension=path.suffix[1:],
            type="file",
            path=path_str,
            size=file_item["size"],
            modify_time=file_item["mtime"],
            pickcode=file_item["pickcode"],
        )

    def _record_get_item_failure(self, path_str: str, now: float):
        """
        记录 get_item 失败，如果连续失败3次则加入黑名单15秒

        :param path_str (str): 目录路径
        :param now (float): 当前时间戳
        """
        if path_str not in self._get_item_fail_records:
            self._get_item_fail_records[path_str] = {"count": 0, "first_fail_time": now}

        record = self._get_item_fail_records[path_str]
        if now - record["first_fail_time"] > 10:
            record["count"] = 0
            record["first_fail_time"] = now

        record["count"] += 1

        if record["count"] >= 3:
            self._get_item_blacklist[path_str] = now + 15.0
            del self._get_item_fail_records[path_str]

    def get_parent(self, fileitem: FileItem) -> Optional[FileItem]:
        """
        获取父目录

        :param fileitem (FileItem): 文件项

        :return FileItem: 父目录文件项，如果不存在则返回 None
        """
        return self.get_item(Path(fileitem.path).parent)

    def delete(self, fileitem: FileItem) -> bool:
        """
        删除文件或目录
        此操作将文件移动到回收站，不会永久删除

        :param fileitem (FileItem): 要删除的文件项

        :return bool: 删除成功返回 True，失败返回 False
        """
        self._delete_rate_limiter.acquire()

        try:
            self._delete_call_counter = (self._delete_call_counter + 1) % 2
            if self._delete_call_counter == 0:
                resp = self.client.fs_delete(
                    fileitem.fileid, **get_ios_ua_app(app=False)
                )
            else:
                resp = self.client.fs_delete_app(fileitem.fileid, **get_ios_ua_app())
            check_response(resp)
            logger.info(f"【115Lite】删除文件: {resp}")
            if fileitem.type == "dir":
                self._id_cache.clear()
                self._id_item_cache.clear()
            else:
                self._id_cache.remove(id=int(fileitem.fileid))
                self._id_item_cache.remove(int(fileitem.fileid))
            return True
        except Exception as e:
            logger.warn(f"【115Lite】删除文件错误: {e}")
            storage_chain = StorageChain()
            fileitem = FileItem(
                storage="u115",
                **fileitem.model_dump(exclude={"storage"}),
            )
            resp = storage_chain.delete_file(fileitem=fileitem)
            if resp:
                if fileitem.type == "dir":
                    self._id_cache.clear()
                    self._id_item_cache.clear()
                else:
                    self._id_cache.remove(id=int(fileitem.fileid))
                    self._id_item_cache.remove(int(fileitem.fileid))
            return resp

    def rename(self, fileitem: FileItem, name: str) -> bool:
        """
        重命名文件或目录

        :param fileitem (FileItem): 要重命名的文件项
        :param name (str): 新名称

        :return bool: 重命名成功返回 True，失败返回 False
        """
        self._rename_rate_limiter.acquire()
        try:
            self._rename_call_counter = (self._rename_call_counter + 1) % 2
            if self._rename_call_counter == 0:
                resp = self.client.fs_rename(
                    (int(fileitem.fileid), name), **get_ios_ua_app(app=False)
                )
            else:
                resp = self.client.fs_rename_app(
                    (int(fileitem.fileid), name), **get_ios_ua_app()
                )
            check_response(resp)

            if fileitem.type == "dir":
                self._id_cache.clear()
                self._id_item_cache.clear()
                return True

            old_cache_path = self._id_cache.get_dir_by_id(int(fileitem.fileid))
            if old_cache_path:
                self._id_cache.remove(id=int(fileitem.fileid))
                new_path = Path(old_cache_path).parent / name
                self._id_cache.add_cache(
                    id=int(fileitem.fileid),
                    directory=new_path.as_posix(),
                )
            old_cache_item = self._id_item_cache.get_item(int(fileitem.fileid))
            if old_cache_item:
                new_path = Path(old_cache_item["path"]).parent / name
                self._id_item_cache.add_cache(
                    id=int(fileitem.fileid),
                    item={
                        "path": new_path.as_posix(),
                        "id": old_cache_item["id"],
                        "size": old_cache_item["size"],
                        "modify_time": old_cache_item["modify_time"],
                        "pickcode": old_cache_item["pickcode"],
                        "is_dir": old_cache_item["is_dir"],
                    },
                )
            return True
        except Exception as e:
            logger.error(f"【115Lite】重命名文件错误: {e}")
            return False

    def download(self, fileitem: FileItem, path: Path = None) -> Optional[Path]:
        """
        下载文件，保存到本地，返回本地临时文件地址

        :param fileitem (FileItem): 要下载的文件项
        :param path (Path): 文件保存路径，如果为 None 则保存到临时目录

        :return Path: 下载成功返回本地文件路径，失败返回 None
        """
        try:
            detail = self.get_item(Path(fileitem.path))
            if not detail:
                logger.error(f"【115Lite】获取文件详情失败: {fileitem.name}")
                return None
            download_info = self.client.download_url(
                detail.pickcode, user_agent=settings.USER_AGENT
            )
            download_url = download_info.geturl() if download_info else None
            if not download_url:
                logger.error(f"【115Lite】下载链接为空: {fileitem.name}")
                return None
            local_path = _build_download_path(fileitem, path or settings.TEMP_PATH)
            if not local_path:
                logger.error(f"【115Lite】下载文件名无效: {fileitem.name}")
                return None
        except Exception as e:
            logger.error(f"【115Lite】获取下载链接失败: {fileitem.name} - {e}")
            return None

        # 获取文件大小
        file_size = detail.size

        # 初始化进度条
        logger.info(f"【115Lite】开始下载: {fileitem.name} -> {local_path}")
        progress_callback = transfer_process(Path(fileitem.path).as_posix())

        try:
            with stream(
                "GET", download_url, headers={"user-agent": settings.USER_AGENT}
            ) as r:
                r.raise_for_status()
                downloaded_size = 0

                with open(local_path, "wb") as f:
                    for chunk in r.iter_bytes(chunk_size=10 * 1024 * 1024):
                        if global_vars.is_transfer_stopped(fileitem.path):
                            logger.info(f"【115Lite】{fileitem.path} 下载已取消！")
                            r.close()
                            raise InterruptedError
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if file_size:
                            progress = (downloaded_size * 100) / file_size
                            progress_callback(progress)

                # 完成下载
                progress_callback(100)
                logger.info(f"【115Lite】下载完成: {fileitem.name}")
        except InterruptedError:
            if local_path.exists():
                local_path.unlink()
            return None
        except RequestError as e:
            logger.error(f"【115Lite】下载网络错误: {fileitem.name} - {str(e)}")
            if local_path.exists():
                local_path.unlink()
            return None
        except Exception as e:
            logger.error(f"【115Lite】下载失败: {fileitem.name} - {str(e)}")
            if local_path.exists():
                local_path.unlink()
            return None

        return local_path


    def detail(self, fileitem: FileItem) -> Optional[FileItem]:
        """
        获取文件详情

        :param fileitem (FileItem): 文件项

        :return FileItem: 包含详细信息的文件项，如果获取失败则返回 None
        """
        return self.get_item(Path(fileitem.path))

    def _find_copied_item(
        self,
        target_dir: FileItem,
        known_ids: Set[str],
        source_item: FileItem,
        max_attempts: int = 8,
    ) -> Optional[FileItem]:
        for attempt in range(max_attempts):
            children = self.list(target_dir)
            if children is not None:
                candidates = [
                    child
                    for child in children
                    if child.fileid
                    and child.fileid not in known_ids
                    and child.type == source_item.type
                ]
                same_name = [
                    child for child in candidates if child.name == source_item.name
                ]
                if len(same_name) == 1:
                    return same_name[0]
                if source_item.type == "file":
                    same_size = [
                        child for child in candidates if child.size == source_item.size
                    ]
                    if len(same_size) == 1:
                        return same_size[0]
                if len(candidates) == 1:
                    return candidates[0]
            if attempt < max_attempts - 1:
                sleep(0.5)
        return None

    def copy(self, fileitem: FileItem, path: Path, new_name: str) -> bool:
        """
        复制文件或目录到目标位置

        :param fileitem (FileItem): 要复制的文件项
        :param path (Path): 目标目录路径
        :param new_name (str): 复制后的新文件名

        :return bool: 复制成功返回 True，失败返回 False
        """
        self._copy_rate_limiter.acquire()
        try:
            parent_id = self.get_pid_by_path(path)
            if parent_id == -1:
                return False
            target_path = path.as_posix().rstrip("/") or "/"
            if target_path != "/":
                target_path = target_path + "/"
            target_dir = FileItem(
                storage=self._disk_name,
                fileid=str(parent_id),
                path=target_path,
                name=path.name if target_path != "/" else "",
                basename=path.name if target_path != "/" else "",
                type="dir",
            )
            existing_items = self.list(target_dir)
            if existing_items is None:
                return False
            known_ids = {item.fileid for item in existing_items if item.fileid}
            self._copy_call_counter = (self._copy_call_counter + 1) % 2
            if self._copy_call_counter == 0:
                resp = self.client.fs_copy(
                    fileitem.fileid, pid=parent_id, **get_ios_ua_app(app=False)
                )
            else:
                resp = self.client.fs_copy_app(
                    fileitem.fileid, pid=parent_id, **get_ios_ua_app()
                )
            check_response(resp)
            logger.debug(f"【115Lite】复制文件: {resp}")
            new_item = self._find_copied_item(
                target_dir=target_dir,
                known_ids=known_ids,
                source_item=fileitem,
            )
            if not new_item:
                logger.error(f"【115Lite】复制后未找到新增对象: {fileitem.path}")
                return False
            if new_item.name != new_name and not self.rename(new_item, new_name):
                return False
            return True
        except Exception as e:
            logger.error(f"【115Lite】复制文件出错: {e}")
            return False

    def move(self, fileitem: FileItem, path: Path, new_name: str) -> bool:
        """
        移动文件或目录到目标位置

        :param fileitem (FileItem): 要移动的文件项
        :param path (Path): 目标目录路径
        :param new_name (str): 移动后的新文件名

        :return bool: 移动成功返回 True，失败返回 False
        """
        self._move_rate_limiter.acquire()
        try:
            parent_id = self.get_pid_by_path(path)
            if parent_id == -1:
                return False
            self._move_call_counter = (self._move_call_counter + 1) % 2
            if self._move_call_counter == 0:
                resp = self.client.fs_move(
                    fileitem.fileid, pid=parent_id, **get_ios_ua_app(app=False)
                )
            else:
                resp = self.client.fs_move_app(
                    fileitem.fileid, pid=parent_id, **get_ios_ua_app()
                )
            check_response(resp)
            logger.debug(f"【115Lite】移动文件: {resp}")
            source_name = fileitem.name or Path(fileitem.path).name
            new_path = Path(path) / source_name

            if fileitem.type == "dir":
                self._id_cache.clear()
                self._id_item_cache.clear()
            else:
                old_cache_path = self._id_cache.get_dir_by_id(int(fileitem.fileid))
                if old_cache_path:
                    self._id_cache.remove(id=int(fileitem.fileid))
                    self._id_cache.add_cache(
                        id=int(fileitem.fileid),
                        directory=new_path.as_posix(),
                    )
                old_cache_item = self._id_item_cache.get_item(int(fileitem.fileid))
                if old_cache_item:
                    self._id_item_cache.add_cache(
                        id=int(fileitem.fileid),
                        item={
                            "path": new_path.as_posix(),
                            "id": old_cache_item["id"],
                            "size": old_cache_item["size"],
                            "modify_time": old_cache_item["modify_time"],
                            "pickcode": old_cache_item["pickcode"],
                            "is_dir": old_cache_item["is_dir"],
                        },
                    )

            new_item = self.get_item(new_path)
            if not new_item:
                return False
            if new_item.name != new_name and not self.rename(new_item, new_name):
                return False
            return True
        except Exception as e:
            logger.error(f"移动文件出错: {e}")
            return False

    def link(self, fileitem: FileItem, target_file: Path) -> bool:
        """
        硬链接文件
        云盘存储不支持硬链接操作

        :param fileitem (FileItem): 文件项
        :param target_file (Path): 目标文件路径

        :return bool: 始终返回 False，表示不支持此操作
        """
        return False

    def softlink(self, fileitem: FileItem, target_file: Path) -> bool:
        """
        软链接文件
        云盘存储不支持软链接操作

        :param fileitem (FileItem): 文件项
        :param target_file (Path): 目标文件路径

        :return bool: 始终返回 False，表示不支持此操作
        """
        return False

    def usage(self) -> Optional[StorageUsage]:
        """
        获取存储使用情况

        :return StorageUsage: 存储使用情况对象，包含总容量和可用容量，获取失败返回 None
        """
        try:
            resp = self.client.fs_index_info(0, **get_ios_ua_app(app=False))
            check_response(resp)
            return StorageUsage(
                total=resp["data"]["space_info"]["all_total"]["size"],
                available=int(resp["data"]["space_info"]["all_total"]["size"])
                - int(resp["data"]["space_info"]["all_use"]["size"]),
            )
        except Exception:
            return None

    def support_transtype(self) -> dict:
        """
        支持的整理方式

        :return Dict: 支持的整理方式字典
        """
        return self.transtype

    def is_support_transtype(self, transtype: str) -> bool:
        """
        是否支持整理方式

        :param transtype (str): 整理方式 (move/copy)

        :return bool: 是否支持
        """
        return transtype in self.transtype
