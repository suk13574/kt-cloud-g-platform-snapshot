"""
Manager 클래스의 베이스 클래스 (=부모 클래스)
===

해당 클래스는 Manager 클래스에서 사용하는 공통 함수들을 묶어 놓았습니다.
"""

import sys
import logging

from filelock import FileLock, Timeout

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_LOGGER = logging.getLogger(__name__)


class BaseManager:
    def __init__(self):
        pass

    @staticmethod
    def load_file(file_path: str, loader_func) -> str:
        """
        파일 읽기 & 예외 처리
        
        :param file_path: 읽을 파일 경로
        :param loader_func: 파일 읽을 때 실행하는 함수 (예: yaml.safe_load)
                
        :return: 읽은 파일의 내용
        """

        try:
            with open(file_path, 'r') as file:
                return loader_func(file)

        except FileNotFoundError:
            _LOGGER.error(f"파일을 찾을 수 없습니다: {file_path}")
            sys.exit()

        except Exception as e:
            _LOGGER.error(f"파일을 로드하는 중 오류가 발생했습니다: {e}")
            sys.exit()

    @staticmethod
    def write_job_file(content, job_file_path) -> None:
        """ 
        job file 작성 함수
        
        :param content: 파일에 작성할 job_id
        :param job_file_path: 기록할 job file 위치

        :return: X
        """

        try:
            with open(job_file_path, "a") as f:
                f.write(f"{content}\n")
                f.flush()

        except Exception as e:
            _LOGGER.error(f"Job ID({content}) 파일 쓰기 중 오류 발생: {e}")

    @classmethod
    def check_arg(cls, required_arg_list, arg_list) -> dict:
        """
        python 실행 인자 확인 후 딕셔너리로 반환
        
        :param required_arg_list: 필수로 요구하는 인자 리스트
        :param arg_list: 입력받은 인자 리스트
        
        :return arg_dict: 인자들이 담긴 딕셔너리 e.g. {"config": "/root/config.yml"} 
        """
        arg_dict = {}

        try:
            for arg in arg_list:
                if not arg.startswith("--"):
                    continue

                command = arg.split("=")[0].replace("--", "")
                value = arg.split("=")[1]

                if command in required_arg_list:
                    arg_dict[command] = value
                    required_arg_list.remove(command)

            if required_arg_list:
                raise SyntaxError

        except (IndexError, SyntaxError) as e:
            _LOGGER.error(f"{required_arg_list} 옵션이 잘못되었습니다.    "
                          f"e.g.) python3 ./src/delete_snapshot.py --config=/root/config.yml")
            sys.exit()

        return arg_dict
