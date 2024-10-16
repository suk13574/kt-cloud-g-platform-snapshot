"""
텔레그램 전송
===
API 호출에 대한 결과를 텔레그램 메세지로 전송합니다.
필수 인자 값은 config입니다.

- config: kt cloud api key 값과 telegram 값을 작성한 설정 파일입니다.
파일 형식은 README.md를 참고하시면 됩니다.

"""
import os
import sys
from datetime import datetime
import logging

import requests
import yaml

from api import GPlatformApi
from base import BaseManager

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_LOGGER = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class TelegramManager(BaseManager):
    def __init__(self, config_file: str, **arg):
        super().__init__()
        self.config = self.load_file(config_file, yaml.safe_load)  # 설정 파일 로드

        self.bot_token = self.config["telegram"]["bot_token"]
        self.chat_id = self.config["telegram"]["chat_id"]

        self.api_key = self.config["kt_cloud"]["api_key"]
        self.secret_key = self.config["kt_cloud"]["secret_key"]
        self.g_platform_api = GPlatformApi(api_key=self.api_key, secret_key=self.secret_key)

    def telegram(self) -> None:
        """
        스냅샷 생성 API, 삭제 API 숫자 count하여 텔레그램 메세지 전송
        
        :return: X 
        """

        _LOGGER.info("===텔레그램 메세지 전송 시작===")

        create_success, create_total, create_processing = self.count_success_job("create_job_list")  # 스냅샷 생성
        delete_success, delete_total, delete_processing = self.count_success_job("delete_job_list")
        today = datetime.now().strftime("%Y-%m-%d")

        message = (f"[TEST] {today} 스냅샷 백업 동작 결과\n"
                   f"생성 수량 비교 : {create_success} / {create_total} \n"
                   f"삭제 수량 비교 : {delete_success} / {delete_total} \n"
                   f"** 생성 진행 중({create_processing}), 삭제 진행 중({delete_processing})"
                   )

        self.send_message(message)

    def count_success_job(self, file_name) -> (int, int):
        """
        job_file을 토대로 job이 얼마나 성공했는지 확인
        
        :param file_name: job file 경로
         
        :return success: job 성공 횟수
        :return len(job_ld_list): 총 job 개수  
        """

        success = 0
        processing = 0

        job_file_path = os.path.join(CURRENT_DIR, "result", file_name)  # ./result/{file_name}

        with open(job_file_path, 'r') as f:
            job_list = [line.strip() for line in f]

        for job in job_list:
            job_id = job.split(",")[0].strip()
            name = job.split(",")[1].strip()

            res = self.g_platform_api.check_job(job_id)
            job_status = res.get("queryasyncjobresultresponse", {}).get("jobstatus", 2)

            if job_status == 1:
                success += 1
            elif job_status == 0:
                processing += 1
            else:
                error_text = res.get("queryasyncjobresultresponse", {}).get("jobresult", {}).get("errortext", None)
                command = res.get("queryasyncjobresultresponse", {}).get("cmd", "").split(".")[-1]  # 스냅샷 생성, 삭제 command 확인

                _LOGGER.error(f"스냅샷 API 실패 - 명령어: {command}, 디스크 또는 스냅샷 이름: {name}, 에러 메세지: {error_text}")

        return success, len(job_list), processing

    def send_message(self, message) -> None:
        """
        텔레그램 메세지 전송
        
        :param message: 보낼 메세지 내용
        
        :return: X 
        """

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        headers = {
            'User-Agent': 'Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)',
            'accept': 'application/json',
            'content-type': 'application/json'
        }
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "disable_web_page_preview": False,
            "disable_notification": False,
            "reply_to_message_id": None
        }

        res = requests.post(url, headers=headers, json=data)

        if res.status_code == 200:
            _LOGGER.info("===텔레그램 메세지 전송 성공===")
        else:
            _LOGGER.error(f"텔레그램 메세지 전송 실패 (status code: {res.status_code}")


if __name__ == "__main__":
    required_arg_list = ["config"]  # 필수 인자
    arg_dict = BaseManager.check_arg(required_arg_list, sys.argv[1:])

    telegram_manager = TelegramManager(arg_dict["config"])
    telegram_manager.telegram()
