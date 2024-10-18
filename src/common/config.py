import os

import yaml

from src.common.base import BaseManager

base_path = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.normpath(os.path.join(base_path, "../config/config.yml"))

DISK_LIST_PATH = "/etc/snapshot/config/disk_list"


config = BaseManager.load_file(CONFIG_PATH, yaml.safe_load)

ACCOUNT_NAME = os.environ.get("KT_CLOUD_ACCOUNT_NAME", str(config["kt_cloud"]["account_name"]))
KT_CLOUD_API_KEY = os.environ.get("KT_CLOUD_API_KEY", str(config["kt_cloud"]["api_key"]))
KT_CLOUD_SECRET_KEY = os.environ.get("KT_CLOUD_SECRET_KEY", str(config["kt_cloud"]["secret_key"]))
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", str(config["telegram"]["bot_token"]))
TELEGRAM_CHAT_ID = os. environ.get("TELEGRAM_CHAT_ID", str(config["telegram"]["chat_id"]))

TIME_CYCLE = int(os.environ.get("TIME_CYCLE", str(config["time"]["cycle"])))
TIME_START_DATE = str(os.environ.get("TIME_START_DATE", config["time"]["start_date"]))
TIME_CREATE_TIME = str(os.environ.get("TIME_CREATE_TIME", config["time"]["create_time"]))
TIME_DELETE_TIME = str(os.environ.get("TIME_DELETE_TIME", config["time"]["delete_time"]))
