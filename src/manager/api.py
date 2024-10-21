"""
KT Cloud의 G 플랫폼 API 모듈
"""

import base64
import hashlib
import hmac
import logging
import warnings
from urllib.parse import quote_plus

import requests
import urllib3
from requests import HTTPError

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
_LOGGER = logging.getLogger(__name__)

warnings.simplefilter('ignore', urllib3.exceptions.InsecureRequestWarning)


class GPlatformApi:
    def __init__(self, api_key, secret_key, zone="v2"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.zone = zone

    def create_url(self, endpoint, path) -> str:
        """
        API 요청하기 위한 URL 조합

        :param endpoint:
        :param path:

        :return url:
        """

        # 파라미터 알파벳 순서대로 정렬
        query_list = sorted(path.replace("?", "").split("&"))

        # 원본 url 생성
        query = str('&'.join(query_list))

        # signature 생성
        signature = self.create_signature(query)
        url = endpoint + '?' + query + '&signature=' + signature

        return url

    def create_signature(self, query) -> str:
        """
        API 요청 시 필요한 signature 값 생성
        
        :param query: query string
         
        :return signature: API 요청 필수값 
        """
        query = query.lower()

        # HAMC SHA1 해싱
        signature = hmac.new(self.secret_key.encode(), query.encode(), hashlib.sha1)

        # 해싱 값 Base64인코딩 및 url인코딩
        signature = base64.b64encode(signature.digest())
        # signature = parse.quote(signature)
        signature = quote_plus(signature)

        return signature

    def _request(self, endpoint, path) -> str:
        """
        실제 API 호출 함수

        :param endpoint:
        :param path:

        :return res.json(): HTTP API 응답
        """
        url = self.create_url(endpoint, path)

        # _LOGGER.info(f"[HTTP Request] {url}")

        res = requests.get(url, verify=False)

        if res.status_code >= 400:
            _LOGGER.error(f"API 호출 에러 - URL: {url}, status code: {res.status_code}, body: {res.text}")
            raise HTTPError(f"Request Fail - {res.status_code} \n{res.json()}")

        return res.json()

    def list_disk(self):
        """ 디스크 리스트 API 호출 """
        endpoint = "https://api.ucloudbiz.olleh.com/server/v1/client/api"

        path = f"?apiKey={self.api_key}&command=listVolumes&response=json"

        return self._request(endpoint, path)

    def list_disk_snapshot(self):
        """ 디스크 스냅샷 리스트 API 호출 """
        endpoint = "https://api.ucloudbiz.olleh.com/server/v1/client/api"
        path = f"?apiKey={self.api_key}&command=listSnapshots&response=json"

        return self._request(endpoint, path)

    def create_disk_snapshot(self, disk_id, snapshot_name):
        """ 디스크 스냅샷 생성 API 호출 """
        endpoint = "https://api.ucloudbiz.olleh.com/server/v1/client/api"
        path = (f"?apiKey={self.api_key}"
                f"&command=createSnapshot"
                f"&volumeid={disk_id}"
                f"&name={snapshot_name}"
                f"&response=json")

        return self._request(endpoint, path)

    def delete_disk_snapshot(self, snapshot_id):
        """ 디스크 스냅샷 삭제 API 호출 """
        endpoint = "https://api.ucloudbiz.olleh.com/server/v1/client/api"
        path = (f"?apiKey={self.api_key}"
                f"&command=deleteSnapshot"
                f"&id={snapshot_id}"
                f"&response=json")

        return self._request(endpoint, path)

    def check_job(self, job_id):
        """ job 성공 확인 API 호출 """
        endpoint = "https://api.ucloudbiz.olleh.com/server/v1/client/api"
        path = (f"?apiKey={self.api_key}"
                f"&command=queryAsyncJobResult"
                f"&jobid={job_id}"
                f"&response=json")

        return self._request(endpoint, path)
