import logging
import sys

import schedule
import time
from datetime import datetime

import yaml

from src.common.base import BaseManager
from src.manager.create_snapshot import CreateSnapshotManager
from src.manager.delete_snapshot import DeleteSnapshotManager
from src.manager.telegram import TelegramManager

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_LOGGER = logging.getLogger(__name__)

CYCLE = 0
START_DATE = None
API_KEY = None
SECRET_KEY = None


def init(config_path="/etc/snapshot/config"):
    global START_DATE, CYCLE, API_KEY, SECRET_KEY

    config = BaseManager.load_file(config_path,  yaml.safe_load)
    # config = BaseManager.load_file(config_path, yaml.safe_load)
    cycle = str(config["time"]["cycle"])
    try:
        if cycle[-1] == "d":
            CYCLE = int(cycle[:-1])
        else:
            raise ValueError("config 파일의 time.cycle 포맷이 숫자d 형태가 아닙니다. (e.g. 3d)")
    except ValueError as e:
        _LOGGER.error(e)
        sys.exit()

    start_date = str(config["time"]["start"])
    try:
        # 날짜가 'YYYY-MM-DD' 형식인지 확인하고 datetime 객체로 변환
        START_DATE = datetime.strptime(start_date, "%Y-%m-%d")

    except ValueError as e:
        _LOGGER.error("config 파일의 time.start 포맷이 YYYY-MM-DD형태가 아닙니다.")
        sys.exit()
    except Exception as e:
        _LOGGER.error("config 파일의 time.start 초기화에 문제가 발생했습니다.", e)
        sys.exit()

    API_KEY = config["kt_cloud"]["api_key"]
    SECRET_KEY = config["kt_cloud"]["secret_key"]


def wait_until_start_date(start_date):
    now = datetime.now()
    while now < start_date:
        time_to_wait = (start_date - now).total_seconds()
        time.sleep(min(time_to_wait, 3600))  # 남은 시간 혹은 1시간 단위로 대기
        now = datetime.now()


if __name__ == "__main__":
    init("../test/key/config.yml")

    wait_until_start_date(START_DATE)

    schedule.every(CYCLE).days.at("00:00").do(lambda: CreateSnapshotManager().create_snapshot())
    schedule.every(CYCLE).days.at("12:00").do(lambda: DeleteSnapshotManager().delete_snapshot())
    schedule.every(CYCLE).days.at("23:00").do(lambda: TelegramManager("../test/key/config.yml").telegram())

    CreateSnapshotManager().create_snapshot()

    while True:
        schedule.run_pending()
        time.sleep(1)
