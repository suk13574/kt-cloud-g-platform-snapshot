import logging
import sys

import schedule
import time
from datetime import datetime

from src.common.config import TIME_CYCLE, TIME_START_DATE, TIME_CREATE_TIME, TIME_DELETE_TIME
from src.manager.create_snapshot import CreateSnapshotManager
from src.manager.delete_snapshot import DeleteSnapshotManager
from src.manager.telegram import TelegramManager

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_LOGGER = logging.getLogger(__name__)


class ConfigError(Exception):
    pass


def init():
    try:

        if not isinstance(TIME_CYCLE, int):
            raise ConfigError(f"time.cycle 포맷이 숫자가 아닙니다. (e.g. 3) cycle: {TIME_CYCLE}")

        start_date = datetime.strptime(TIME_START_DATE, "%Y-%m-%d")

        if not datetime.strptime(TIME_CREATE_TIME, "%H:%M") and datetime.strptime(TIME_DELETE_TIME, "%H:%M"):
            raise ConfigError(f"time._time 포맷이 HH:MM 형태가 아닙니다. (e.g. 09:30) "
                              f"create_time: {TIME_CREATE_TIME}, delete_time: {TIME_DELETE_TIME}")

        return start_date

    except ConfigError as e:
        _LOGGER.error(e)
        sys.exit()
    except ValueError as e:
        _LOGGER.error(f"time.start_date 포맷이 YYYY-MM-DD형태가 아닙니다. start_date: {TIME_START_DATE}")
        sys.exit()


def wait_until_start_date(start_date):
    now = datetime.now()
    while now < start_date:
        time_to_wait = (start_date - now).total_seconds()
        time.sleep(min(time_to_wait, 3600))  # 남은 시간 혹은 1시간 단위로 대기
        now = datetime.now()


if __name__ == "__main__":
    start_date = init()

    wait_until_start_date(start_date)

    schedule.every(TIME_CYCLE).days.at(TIME_CREATE_TIME).do(lambda: CreateSnapshotManager().create_snapshot())
    schedule.every(TIME_CYCLE).days.at(TIME_DELETE_TIME).do(lambda: DeleteSnapshotManager().delete_snapshot())
    schedule.every(TIME_CYCLE+1).days.at("09:30").do(lambda: TelegramManager().telegram())

    CreateSnapshotManager().create_snapshot()

    while True:
        schedule.run_pending()
        time.sleep(1)
