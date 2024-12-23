import logging
import sys

import schedule
import time
from datetime import datetime

import yaml

from src.common.base import BaseManager
from src.common.config import CONFIG_PATH
from src.manager.create_snapshot import CreateSnapshotManager
from src.manager.delete_snapshot import DeleteSnapshotManager

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_LOGGER = logging.getLogger(__name__)

CYCLE = 0
START_DATE = None
CREATE_TIME = None
DELETE_TIME = None


class ConfigError(Exception):
    pass


def init(config_path=CONFIG_PATH):
    global CYCLE, START_DATE, CREATE_TIME, DELETE_TIME

    config = BaseManager.load_file(config_path, yaml.safe_load)

    cycle = str(config["time"]["cycle"])
    del_cycle = str(config["time"]["del_cycle"])
    start_date = str(config["time"]["start_date"])
    create_time = str(config["time"]["create_time"])
    delete_time = str(config["time"]["delete_time"])

    try:

        if cycle[-1] == "d" and del_cycle[-1] == "d":
            CYCLE = int(cycle[:-1])
        else:
            raise ConfigError(f"config 파일의 time._cycle 포맷이 숫자d 형태가 아닙니다. (e.g. 3d) cycle: {cycle}")

        START_DATE = datetime.strptime(start_date, "%Y-%m-%d")

        if datetime.strptime(create_time, "%H:%M") and datetime.strptime(delete_time, "%H:%M"):
            CREATE_TIME = create_time
            DELETE_TIME = delete_time
        else:
            raise ConfigError(f"config 파일의 time._time 포맷이 HH:MM 형태가 아닙니다. (e.g. 09:30) "
                              f"create_time: {create_time}, delete_time: {delete_time}")

    except ConfigError as e:
        _LOGGER.error(e)
        sys.exit()
    except ValueError as e:
        _LOGGER.error(f"config 파일의 time.start_date 포맷이 YYYY-MM-DD형태가 아닙니다. (e.g. 2024-10-21) start_date: {start_date}")
        sys.exit()


def wait_until_start_date(start_date):
    _LOGGER.info(f"{start_date}에 스냅샷 생성을 시작합니다.")
    now = datetime.now()
    while now < start_date:
        time_to_wait = (start_date - now).total_seconds()
        time.sleep(min(time_to_wait, 3600))  # 남은 시간 혹은 1시간 단위로 대기
        now = datetime.now()


if __name__ == "__main__":
    init()

    wait_until_start_date(START_DATE)

    schedule.every(CYCLE).days.at(CREATE_TIME).do(lambda: CreateSnapshotManager().create_snapshot())
    schedule.every(CYCLE).days.at(DELETE_TIME).do(lambda: DeleteSnapshotManager().delete_snapshot())

    CreateSnapshotManager().create_snapshot()
    DeleteSnapshotManager().delete_snapshot()

    while True:
        schedule.run_pending()
        time.sleep(1)
