from dataclasses import dataclass, field
from pathlib import Path
from threading import Event, Lock
from typing import Any, Callable, List, Optional, Tuple

from app.sdk.media import MediaInfo
from app.sdk.media import MetaBase
from app.schemas import FileItem, TransferInfo


@dataclass
class RelatedFile:
    """
    关联文件信息（字幕、音轨）
    """

    fileitem: FileItem
    target_path: Path
    file_type: str


@dataclass
class TransferTask:
    """
    整理任务
    """

    fileitem: FileItem
    target_path: Path
    mediainfo: MediaInfo
    meta: MetaBase
    transfer_type: str
    overwrite_mode: Optional[str] = None  # 覆盖模式: always, size, latest, never

    need_rename: bool = True
    need_notify: Optional[bool] = None  # 是否需要通知（与 MP 目录 notify 一致）
    need_scrape: bool = False  # 是否与 MP transfer_media 的 need_scrape 一致
    scrape: Optional[bool] = None  # MP TransferTask.scrape 原始值（可选）
    manual: Optional[bool] = None  # 是否手动整理
    background: Optional[bool] = None  # 是否后台运行
    username: Optional[str] = None  # 用户名
    downloader: Optional[str] = None  # 下载器
    download_hash: Optional[str] = None  # 下载记录hash

    transfer_batch_id: Optional[str] = None
    related_files: List["RelatedFile"] = field(default_factory=list)

    # MoviePilot V3 durable 终态结算上下文。接管任务必须在批处理真正结束后
    # 调用宿主回调，并让原整理线程等待结果，不能入队后立即返回成功。
    host_task: Any = field(default=None, repr=False)
    settlement_callback: Optional[Callable] = field(default=None, repr=False)
    completion_event: Event = field(default_factory=Event, repr=False)
    settlement_result: Optional[Tuple[bool, str]] = field(default=None, repr=False)
    _settlement_lock: Lock = field(default_factory=Lock, repr=False)

    def settle(self, transferinfo: TransferInfo) -> Tuple[bool, str]:
        """只执行一次宿主终态回调，并唤醒等待中的整理线程。"""
        with self._settlement_lock:
            if self.settlement_result is not None:
                return self.settlement_result
            try:
                if self.settlement_callback and self.host_task is not None:
                    result = self.settlement_callback(self.host_task, transferinfo)
                    self.settlement_result = (
                        bool(result[0]),
                        str(result[1] or ""),
                    )
                else:
                    self.settlement_result = (
                        bool(transferinfo.success),
                        str(transferinfo.message or ""),
                    )
            except Exception as error:
                self.settlement_result = (False, f"整理终态结算失败: {error}")
            finally:
                self.completion_event.set()
            return self.settlement_result

    @property
    def all_files(self) -> List[Tuple[FileItem, Path]]:
        """
        返回所有需要处理的文件（主视频+关联文件）
        """
        files: List[Tuple[FileItem, Path]] = [(self.fileitem, self.target_path)]
        for rf in self.related_files:
            files.append((rf.fileitem, rf.target_path))
        return files

    @property
    def target_dir(self) -> Path:
        """
        获取目标目录
        """
        return self.target_path.parent

    @property
    def target_name(self) -> str:
        """
        获取目标文件名
        """
        return self.target_path.name
