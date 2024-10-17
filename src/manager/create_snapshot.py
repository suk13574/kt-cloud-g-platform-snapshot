"""
스냅샷 생성 모듈
===
스냅샷을 생성합니다.
필수 인자 값은 config와 disk_snapshot_list입니다.

- config: kt cloud api key 값과 telegram 값을 작성한 설정 파일입니다.
파일 형식은 README.md를 참고하시면 됩니다.

- disk_sanpshot_list는 디스크명, 서버명의 리스트입니다.
해당 디스크의 스냅샷을 생성합니다.

"""
import os
import sys
from datetime import datetime
import logging
import time

import yaml
from requests import HTTPError

from src.manager.api import GPlatformApi
from src.common.base import BaseManager

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_LOGGER = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
JOB_FILE_PATH = os.path.join(CURRENT_DIR, "result", "create_job_list")  # ./result/create_job_list
WAIT_TIME = 60 * 5  # API 호출 주기


class CreateSnapshotManager(BaseManager):
    def __init__(self, config_file="/etc/snapshot/config/config.yml", disk_snapshot_list="/etc/snapshot/config/disk_list", **arg):
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

        _LOGGER.info(f"==={today} 스냅샷 생성 시작===")

        # disk 정보 가져옴
        # e.g. disk_info = {"disk_name1":{"server_name1":"disk_id1"}", "disk_name2":{"server_name":"disk_id2"}}
        disk_info = self.get_disk_info()

        # 디스크 스냅샷 생성할 디스크 이름 파일 읽은 후 (디스크 이름, 서버 이름) 튜플 리스트 반환
        # e.g. disk_list = [("disk_name1", "server_name"), ("disk_name2", "server_name")]
        disk_list = self.read_disk_list()

        # job file clear
        with open(JOB_FILE_PATH, "w") as f:
            f.truncate(0)

        for disk_name, server_name in disk_list:
            if disk_name in disk_info:
                try:
                    disk_id = disk_info[disk_name][server_name]

                    # sanpshot 이름 규칙: 디스크 이름-날짜
                    if len(disk_info[disk_name]) > 1:  # 중복 디스크 이름이 있을 경우 디스크 이름-서버이름-날짜
                        snapshot_name = f"{disk_name}-{server_name}-{today}"
                    else:
                        snapshot_name = f"{disk_name}-{today}"

                    res = self.g_platform_api.create_disk_snapshot(disk_id, snapshot_name)  # 스냅샷 생성 API 호출

                    job_id = res["createsnapshotresponse"]["jobid"]
                    content = job_id + ", " + disk_name
                    self.write_job_file(content, JOB_FILE_PATH)

                    _LOGGER.info(f"{disk_name} 스냅샷 생성 API 호출 완료")

                    time.sleep(WAIT_TIME)  # wait_time만큼 대기 후 다시 스냅샷 생성

                except HTTPError as e:  # API 응답이 200이 아닐 시 API 에러 발생
                    _LOGGER.error(f"{disk_name} 스냅샷 생성 API 오류 발생 \n {e}")
                except Exception as e:
                    _LOGGER.error(f"{disk_name} 스냅샷 생성 중 오류 발생 \n {e}")
                except KeyError as e:
                    _LOGGER.error(f"disk_info에 해당하는 key 값이 없습니다. disk_name: {disk_name}, server_name: {server_name}")
            else:
                _LOGGER.error(f"디스크 이름: {disk_name}은 존재하지 않는 디스크입니다.")

        _LOGGER.info(f"==={today} 스냅샷 생성 완료===")

    def read_disk_list(self):
        """
        --disk_snapshot_list의 인자로 받은 파일로부터 디스크 정보를 읽어 특정 형태로 반환
        
        :return disk_list: key가 디스크 이름, value가 서버명: 디스크 아이디인 딕셔너리 반환 
        """
        
        disk_name_list = self.load_file(self.disk_list_path, lambda f: [line.strip() for line in f])
        return [tuple(map(str.strip, item.split(','))) for item in disk_name_list]

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
                if disk.get("vmdisplayname", None):
                    disk_info.setdefault(disk["name"], {})[disk["vmdisplayname"]] = disk["id"]

            return disk_info

        except HTTPError as e:
            _LOGGER.error("디스크 스냅샷 API 응답 코드가 200이 아닙니다.")
            sys.exit()

        except KeyError as e:
            _LOGGER.error(f"디스크 리스트 API 응답에 해당하는 key 값이 없습니다: {e}")
            sys.exit()


if __name__ == "__main__":
    create_snapshot_manager = CreateSnapshotManager("../../test/key/config.yml", "../../test/key/disk_list")
    create_snapshot_manager.create_snapshot()