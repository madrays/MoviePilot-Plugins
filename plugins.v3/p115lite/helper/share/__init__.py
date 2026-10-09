from pathlib import Path
from queue import Empty, Queue
from threading import Lock, Thread
from time import sleep
from typing import Optional

from p115client import P115Client
from p115client.tool.iterdir import share_iterdir
from p115client.util import share_extract_payload

from app.chain.media import MediaChain
from app.sdk.media import MediaInfo
from app.sdk.media import MetaInfo
from app.sdk.logging import logger
from app.sdk.utilities import StringUtils

from ...core.config import configer
from ...core.i18n import i18n
from ...core.message import post_message
from ...core.p115 import get_pid_by_path
from ...utils.sentry import sentry_manager


@sentry_manager.capture_all_class_exceptions
class ShareTransferHelper:
    """
    分享链接转存
    """

    def __init__(self, client: P115Client):
        self.client = client
        self._add_share_queue = Queue()
        self._add_share_worker_thread = None
        self._add_share_worker_lock = Lock()

    def _ensure_add_share_worker_running(self):
        """
        确保工作线程正在运行
        """
        with self._add_share_worker_lock:
            if (
                self._add_share_worker_thread is None
                or not self._add_share_worker_thread.is_alive()
            ):
                self._add_share_worker_thread = Thread(
                    target=self._process_add_share_queue, daemon=True
                )
                self._add_share_worker_thread.start()

    def _process_add_share_queue(self):
        """
        处理队列中的任务
        """
        while True:
            try:
                task = self._add_share_queue.get(timeout=60)
            except Empty:
                logger.debug("【分享转存】释放分享转存队列任务")
                break

            url, channel, source, userid, pan_path = task
            try:
                self.__add_share(url, channel, source, userid, pan_path)
            except Exception as e:
                logger.error(f"【分享转存】任务处理异常: {e}", exc_info=True)
            finally:
                self._add_share_queue.task_done()
                sleep(3)

    @staticmethod
    def send_notify(
        title: str,
        text: Optional[str] = None,
        image: Optional[str] = None,
        channel: Optional[str | int] = None,
        source: Optional[str] = None,
        userid: Optional[str] = None,
    ):
        """
        统一消息发送接口，自动选择全局或者指定用户发送
        """
        if channel and userid:
            post_message(
                channel=channel,  # noqa
                source=source,
                title=title,
                image=image,
                text=text,
                userid=userid,
            )

    def add_share_recognize_mediainfo(
        self, share_code: str, receive_code: str
    ) -> Optional[MediaInfo]:
        """
        分享转存识别媒体信息

        :param share_code (str): 分享码
        :param receive_code (str): 接收码

        :return MediaInfo: 识别成功返回媒体信息，失败返回 None
        """
        file_num = 0
        file_mediainfo = None
        item_name = None
        try:
            for item in share_iterdir(
                self.client,
                receive_code=receive_code,
                share_code=share_code,
                cid=0,
                app="web",
                max_workers=0,
                **configer.get_ios_ua_app(app=False),
            ):
                if file_num == 1:
                    file_num = 2
                    break
                item_name = item["name"]
                file_num += 1
            if file_num == 1:
                mediachain = MediaChain()
                file_meta = MetaInfo(title=item_name)
                file_mediainfo = mediachain.recognize_by_meta(file_meta)
        except Exception as e:
            logger.warning(
                f"【分享转存】识别媒体信息失败，继续转存: {e}",
                exc_info=True,
            )
            return None
        return file_mediainfo

    @staticmethod
    def share_url_extract(url: str):
        """
        解析分享链接
        """
        return share_extract_payload(url)

    def add_share_115(
        self,
        url,
        channel: Optional[str | int] = None,
        source: Optional[str] = None,
        userid: Optional[str] = None,
        notify: bool = True,
        pan_path: Optional[str | Path] = None,
    ):
        """
        添加115分享任务
        """
        data = self.share_url_extract(url)
        share_code = data["share_code"]
        receive_code = data["receive_code"]
        logger.info(
            f"【分享转存】解析分享链接 share_code={share_code} receive_code={receive_code}"
        )
        if not share_code or not receive_code:
            logger.error(f"【分享转存】解析分享链接失败：{url}")
            if notify:
                self.send_notify(
                    channel=channel,
                    source=source,
                    title=f"{i18n.translate('share_url_extract_error', url=url)}",
                    userid=userid,
                )
            return False, "解析分享链接失败"

        if not pan_path:
            parent_path = configer.share_recieve_paths[0]
        else:
            parent_path = pan_path
        parent_id = get_pid_by_path(
            client=self.client,
            path=parent_path,
            mkdir=True,
            update_cache=True,
            by_cache=True,
        )
        logger.info(f"【分享转存】获取到转存目录 {parent_path} ID：{parent_id}")

        # 尝试识别媒体信息
        file_mediainfo = self.add_share_recognize_mediainfo(
            share_code=share_code, receive_code=receive_code
        )

        # 获取文件大小
        sleep(2)
        payload = {
            "share_code": share_code,
            "receive_code": receive_code,
            "limit": 1,
            "offset": 0,
            "cid": 0,
        }
        size = "未知"
        try:
            resp = self.client.share_snap(payload, **configer.get_ios_ua_app(app=False))
            if resp["state"]:
                size = StringUtils.str_filesize(resp["data"]["shareinfo"]["file_size"])
        except Exception as e:
            logger.warning(
                f"【分享转存】获取分享大小失败，继续转存: {e}", exc_info=True
            )

        payload = {
            "share_code": share_code,
            "receive_code": receive_code,
            "file_id": ",".join(
                [
                    str(f["id"])
                    for f in share_iterdir(
                        self.client,
                        receive_code=receive_code,
                        share_code=share_code,
                        cid=0,
                        app="web",
                        max_workers=0,
                        **configer.get_ios_ua_app(app=False),
                    )
                ]
            ),
            "cid": int(parent_id),
            "is_check": 0,
        }
        resp = self.client.share_receive(payload, **configer.get_ios_ua_app(app=False))
        if resp["state"]:
            logger.info(f"【分享转存】转存 {share_code} 到 {parent_path} 成功！")
            if not file_mediainfo:
                if notify:
                    self.send_notify(
                        channel=channel,
                        source=source,
                        title=i18n.translate("share_add_success"),
                        text=f"""
分享链接：https://115cdn.com/s/{share_code}?password={receive_code}
转存目录：{parent_path}
文件大小: {size}
""",
                        userid=userid,
                    )
            else:
                if notify:
                    self.send_notify(
                        channel=channel,
                        source=source,
                        title=i18n.translate(
                            "share_add_success_2",
                            title=file_mediainfo.title,
                            year=file_mediainfo.year,
                        ),
                        text=f"""
链接：https://115cdn.com/s/{share_code}?password={receive_code}
大小: {size}
简介：{file_mediainfo.overview}
""",
                        image=file_mediainfo.poster_path,
                        userid=userid,
                    )
            return True, file_mediainfo, parent_path, parent_id

        logger.info(f"【分享转存】转存 {share_code} 失败：{resp['error']}")
        if notify:
            self.send_notify(
                channel=channel,
                source=source,
                title=i18n.translate("share_add_fail"),
                text=f"""
分享链接：https://115cdn.com/s/{share_code}?password={receive_code}
转存目录：{parent_path}
失败原因：{resp["error"]}
""",
                userid=userid,
            )
        return False, "转存失败", resp["error"]

    def __add_share(self, url, channel, source, userid, pan_path):
        """
        分享转存
        """
        if not configer.share_recieve_paths:
            self.send_notify(
                channel=channel,
                source=source,
                title=i18n.translate("add_share_config_error"),
                userid=userid,
            )
            return
        try:
            self.add_share_115(url, channel, source, userid, True, pan_path)
        except Exception as e:
            logger.error(f"【分享转存】运行失败: {e}", exc_info=True)
            self.send_notify(
                channel=channel,
                source=source,
                title=i18n.translate("share_add_fail_2", e=e),
                userid=userid,
            )
            return

    def add_share(
        self, url, channel, userid, pan_path=None, source: Optional[str] = None
    ):
        """
        将分享任务加入队列
        """
        self._add_share_queue.put((url, channel, source, userid, pan_path))
        logger.info(
            f"【分享转存】{url} 任务已加入分享转存队列，当前队列大小：{self._add_share_queue.qsize()}"
        )
        self._ensure_add_share_worker_running()
