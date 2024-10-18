"""
스냅샷 삭제
===
스냅샷을 삭제합니다.
필수 인자 값은 config, del_day입니다.

- config: kt cloud api key 값과 telegram 값을 작성한 설정 파일입니다.
파일 형식은 README.md를 참고하시면 됩니다.

- del_day: del_day 전에 생성한 스냅샷을 삭제합니다.
예를 들어, del_day=7d라면, 일주일 전에 생성한 스냅샷을 삭제합니다.

"""
import os
import sys
from datetime import datetime, timedelta
import logging
import time

from requests import HTTPError

from src.common.config import CONFIG_PATH, KT_CLOUD_API_KEY, KT_CLOUD_SECRET_KEY, TIME_CYCLE
from src.manager.api import GPlatformApi
from src.common.base import BaseManager

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_LOGGER = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
JOB_FILE_PATH = os.path.join(CURRENT_DIR, "result", "delete_job_list")  # ./result/delete_job_list
WAIT_TIME = 60 * 5  # API 호출 주기


class DeleteSnapshotManager(BaseManager):
    def __init__(self, config_file=CONFIG_PATH, **arg):
        super().__init__()

        self.api_key = KT_CLOUD_API_KEY
        self.secret_key = KT_CLOUD_SECRET_KEY
        self.g_platform_api = GPlatformApi(api_key=self.api_key, secret_key=self.secret_key)

        self.del_date = self.calculate_del_date(TIME_CYCLE)

    @staticmethod
    def calculate_del_date(del_cycle: str) -> str:
        """
        del_day 인자 체크

        :param del_cycle: 오늘부터 며칠 전의 스냅샷을 삭제할지 지정

        :return del_date: 삭제 진행할 날짜
        """
        try:
            if del_cycle[-1] == "d":
                del_day = int(del_cycle[:-1])
                return (datetime.now() - timedelta(days=del_day)).strftime("%Y-%m-%d")
            else:
                raise ValueError

        except ValueError as e:
            _LOGGER.error(f"config파일의 time.delete_cycle 형식이 잘못되었습니다. 13d와 같이 숫자+d로 작성해주세요: {del_cycle}")

    def delete_snapshot(self) -> None:
        """
        디스크 스냅샷 삭제
        
        :return: X 
        """

        _LOGGER.info(f"==={self.del_date} 스냅샷 삭제 시작===")

        # 삭제할 디스크 스냅샷 리스트 가져옴
        del_snapshot_list = self.get_del_snapshot_list(self.del_date)

        # job file clear
        with open(JOB_FILE_PATH, "w") as f:
            f.truncate(0)

        for snapshot_name, snapshot_id in del_snapshot_list:
            try:
                res = self.g_platform_api.delete_disk_snapshot(snapshot_id)

                job_id = res["deletesnapshotresponse"]["jobid"]
                content = job_id + ", " + snapshot_name
                self.write_job_file(content, JOB_FILE_PATH)

                _LOGGER.info(f"{snapshot_name} 스냅샷 삭제 API 호출 완료")

                time.sleep(WAIT_TIME)  # wait_time만큼 대기 후 다시 스냅샷 삭제

            except HTTPError as e:  # API 응답이 200이 아닐 시 API 에러 발생
                _LOGGER.error(f"{snapshot_name} 스냅샷 생성 API 오류 발생 \n {e}")

            except KeyError as e:
                _LOGGER.error(f"API 응답에 deletesnapshotresponse 또는 jobid가 없습니다: {e}")

        _LOGGER.info(f"==={self.del_date} 스냅샷 삭제 완료===")

    def get_del_snapshot_list(self, del_date) -> list:
        """
        삭제할 스냅샷 아이디 리스트 반환

        :param del_date: 삭제 기준 날짜

        :return del_snapshot_list: (디스크이름, 스냅샷명)을 원소로 가지는 리스트
        """
        
        _LOGGER.info("스냅샷 리스트 호출")

        try:
            res = self.g_platform_api.list_disk_snapshot()
            snapshot_list = res["listsnapshotsresponse"]["snapshot"]

        except HTTPError as e:
            _LOGGER.error("디스크 스냅샷 API 응답 코드가 200이 아닙니다.")
            sys.exit()

        except KeyError as e:
            _LOGGER.error(f"디스크 스냅샷 API 응답에 listsnapshotsresponse 또는 snapshot이 없습니다. \n {e}")
            sys.exit()

        del_snapshot_list = []
        for snapshot in snapshot_list:
            try:
                snapshot_name_date = snapshot["name"].split("_")[-1]

                if snapshot_name_date.startswith(del_date.replace("-", "")):
                    del_snapshot_list.append((snapshot["name"], snapshot["id"]))

            except KeyError as e:
                _LOGGER.error(f"디스크 스냅샷 리스트 API 응답에 name 또는 id가 없습니다. \n {e}")
                sys.exit()

        return del_snapshot_list
