"""
스냅샷 생성 모듈
===
스냅샷을 생성합니다.
필수 인자 값은 config와 disk_snapshot_list입니다.

필수 인자 값에 대한 설명은 config 파일의 README.md를 참고하시면 됩니다.

"""
import os
import sys
from datetime import datetime
import logging
import time
import threading

import yaml
from requests import HTTPError

from api import GPlatformApi
from base import BaseManager

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_LOGGER = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
JOB_FILE_PATH = os.path.join(CURRENT_DIR, "result", "create_job_list")  # ./result/create_job_list
WAIT_TIME = 60 * 5  # API 호출 주기


class CreateSnapshotManager(BaseManager):
    def __init__(self, config_file: str, disk_snapshot_list: str, **arg):
        super().__init__()
        self.config = self.load_file(config_file, yaml.safe_load)  # 설정 파일 로드

        self.api_key = self.config["kt_cloud"]["api_key"]
        self.secret_key = self.config["kt_cloud"]["secret_key"]
        self.g_platform_api = GPlatformApi(api_key=self.api_key, secret_key=self.secret_key)

        self.disk_list_path = disk_snapshot_list

    def create_snapshot(self) -> None:
        """
        디스크 스냅샷 생성
        """
        today = datetime.now().strftime("%Y-%m-%d")

        _LOGGER.info(f"{today} 스냅샷 생성 시작")

        # disk 정보 가져옴
        # e.g. disk_info = {"disk_name1":"disk_id1", "disk_name2":"disk_id2"}
        disk_info = self.get_disk_info()

        # 디스크 스냅샷 생성할 디스크 이름 파일 로드
        disk_name_list = self.load_file(self.disk_list_path, lambda f: [line.strip() for line in f])

        # job file clear
        with open(JOB_FILE_PATH, "w") as f:
            f.truncate(0)

        for disk_name in disk_name_list:
            if disk_name in disk_info:
                try:
                    disk_id = disk_info[disk_name]
                    snapshot_name = f"{disk_name}-{today}"
                    res = self.g_platform_api.create_disk_snapshot(disk_id, snapshot_name)  # 스냅샷 생성 API 호출

                    job_id = res["createsnapshotresponse"]["jobid"]
                    # self.write_job_file(job_id)
                    threading.Thread(target=self.write_job_file, args=(job_id, JOB_FILE_PATH,)).start()

                    _LOGGER.info(f"{disk_name} 스냅샷 생성 API 호출 완료")

                    time.sleep(WAIT_TIME)  # wait_time만큼 대기 후 다시 스냅샷 생성

                except HTTPError as e:  # API 응답이 200이 아닐 시 API 에러 발생
                    _LOGGER.error(f"{disk_name} 스냅샷 생성 API 오류 발생 \n {e}")

                except Exception as e:
                    _LOGGER.error(f"{disk_name} 스냅샷 생성 중 오류 발생 \n {e}")
            else:
                _LOGGER.error(f"디스크 이름: {disk_name}은 존재하지 않는 디스크입니다.")

        _LOGGER.info(f"{today} 스냅샷 생성 완료")

    def get_disk_info(self) -> dict:
        """
        disk 리스트 API 호출 후 이름, 아이디 정보 딕셔너리로 반환

        :return disk_info: key가 디스크 이름, value가 디스크 아이디인 딕셔너리 반환
        """

        _LOGGER.info("디스크 리스트 API 호출")

        try:
            res = self.g_platform_api.list_disk()
            disk_list = res["listvolumesresponse"]["volume"]

            disk_info = {}
            for disk in disk_list:
                disk_info[disk["name"]] = disk["id"]

            return disk_info

        except HTTPError as e:
            _LOGGER.error("디스크 스냅샷 API 응답 코드가 200이 아닙니다.")
            sys.exit()

        except KeyError as e:
            _LOGGER.error(f"디스크 리스트 API 응답에 해당하는 key 값이 없습니다: {e}")
            sys.exit()


if __name__ == "__main__":
    # config_path = "./config/config.yml"
    # create_snapshot_manager = CreateSnapshotManager(config_path)
    # create_snapshot_manager.create_snapshot()

    required_arg_list = ["config", "disk_snapshot_list"]  # 필수 인자
    arg_dict = BaseManager.check_arg(required_arg_list, sys.argv[1:])

    create_snapshot_manager = CreateSnapshotManager(arg_dict["config"], arg_dict["disk_snapshot_list"])
    create_snapshot_manager.create_snapshot()
