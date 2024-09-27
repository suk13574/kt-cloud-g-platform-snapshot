## 1. 초기 설정

src 디렉토리와 requirements.txt 파일을 서버에 옮깁니다.

```
.
|-- requirements.txt
`-- src
    |-- __init__.py
    |-- __pycache__
    |-- api.py
    |-- base.py
    |-- config
    |-- create_snapshot.py
    |-- delete_snapshot.py
    |-- result
    `-- telegram.py
```

<br>

requirements.txt 파일에 있는 모듈을 설치합니다.


```bash
pip install --no-cache-dir -r requirements.txt
```

<br>

## 2. 설정 파일
설정 파일 예시는 src/config 아래에 있습니다.

<br>

1. config.yml

모든 파일을 실행시킬 때 필요한 파일이며, `--config` 옵션과 함께 사용됩니다.

yaml 확장자로 아래 형식에 맞추어 작성해야 합니다.

```yaml
kt_cloud:
  account_name: TEST  # KT Cloud 계정명 (이후 텔레그램 방에 전송될 때 사용)
  api_key: YI***************************************  # KT Cloud API Key
  secret_key: fg************************************  # KT Cloud Secret Key

telegram:
  bot_token: 61*******:AA************************  # 텔레그램 봇 토큰
  chat_id: -9******  # 보낼 텔레그램 채팅방 ID
```

<br>

2. disk_snapshot_list

디스크 스냅샷 생성할 디스크 이름을 적는 파일이며, `--disk_snapshot_list` 옵션과 함께 사용됩니다.

아래 예시와 같이 스냅샷 생성할 디스크 이름을 줄바꿈으로 구분지어 작성합니다.

```
ROOT-558704
hsyunDATA01
```

<br>


## 실행 방법

실행할 수 있는 파일은 총 3개입니다.

실행 시 src 아래에 있는 파일은 모두 필요합니다.

1. create_snapshot.py

disk_snapshot_list에 적힌 디스크의 스냅샷을 생성합니다. (생성 API 호출 텀은 5분입니다. 연속하여 호출하면 kt cloud에서 누락되는 경우가 있어 텀을 두었습니다.)

스냅샷 네이밍 규칙은 디스크명-YYYY-mm-dd입니다.

파일 실행 필수 옵션은 다음과 같습니다.

- `--config`
- `--disk_snapshot_list`

파일 실행 예시입니다.

```bash
python ./src/create_snapshot.py --config=./src/config/config.yml --disk_snapshot_list=./src/config/disk_snapshot_list
```

<br>

스냅샷 생성이 성공적으로 마쳤다면, 아래와 같은 로그가 보입니다.
``` commandline
[2024-09-26 17:16:16] [INFO] 2024-09-26 스냅샷 생성 시작
[2024-09-26 17:16:16] [INFO] 디스크 리스트 API 호출
[2024-09-26 17:16:19] [INFO] ROOT-558704 스냅샷 생성 API 호출 완료
[2024-09-26 17:21:21] [INFO] hsyunDATA01 스냅샷 생성 API 호출 완료
[2024-09-26 17:26:21] [INFO] 2024-09-26 스냅샷 생성 완료
```

<br>

또한 src/result/create_job_list에 다음과 같이 job id와 디스크 명이 기록됩니다.

job id는 API 호출 시 얻는 값으로, 이후 job id로 작업 성공/실패 여부를 알 수 있습니다.

```bash
6cca13d5-599e-438b-b512-753edf85e293, ROOT-558704
d0a39a3e-6469-44ae-a9f3-ea0a8aa8d156, hsyunDATA01
```

<br>

2. delete_snapshot.py

디스크의 스냅샷을 삭제합니다. (삭제 API 호출 텀은 5분입니다. 연속하여 호출하면 kt cloud에서 누락되는 경우가 있어 텀을 두었습니다.)

파일 실행 필수 옵션은 다음과 같습니다.

- `--config`
- `--del_day` : 오늘로부터 n일 전에 생성된 스냅샷을 삭제합니다. **숫자d 형식으로 작성**해야 합니다.

<br>

파일 실행 예시입니다.

아래에서는 `del_day`를 0d로 줌으로써, 오늘 날짜로 생성된 스냅샷을 삭제합니다.

```bash
python ./src/delete_snapshot.py --config=./src/config/config.yml  --del_day=0d
```

<br>

스냅샷 삭제가 성공적으로 마쳤다면, 아래와 같은 로그가 보입니다.

``` commandline
[2024-09-27 09:27:09] [INFO] 2024-09-26 스냅샷 삭제 시작
[2024-09-27 09:27:09] [INFO] 스냅샷 리스트 호출
[2024-09-27 09:27:10] [INFO] hsyun-test_hsyunDATA01_20240926082120 스냅샷 삭제 API 호출 완료
[2024-09-27 09:32:10] [INFO] hsyun-test_hsyunDATA01_20240926074118 스냅샷 삭제 API 호출 완료
[2024-09-27 09:37:10] [INFO] 2024-09-26 스냅샷 삭제 완료

```

<br>

3. telegram.py

스냅샷 생성, 삭제 API 요청 횟수와 성공 횟수를 반환합니다.

파일 실행 필수 옵션은 다음과 같습니다.

- `--config`
<br>

파일 실행 예시입니다.

```bash
python src/telegram.py --config=./src/config/config.yml
```

<br>

텔레그램은 다음과 같이 메세지가 옵니다.

** 아래 메세지에서 중괄호는 변수를 뜻합니다.

```
[{account명}] {오늘 날짜} 스냅샷 백업 동작 결과
생성 수량 비교: {생성 성공 개수} / {생성 API 호출 수}
삭제 수량 비교: {삭제 성공 개수} / {삭제 API 호출 수}
** 생성 진행 중({생성 중인 스냅샷 개수}), 삭제 진행 중({삭제 중인 스냅샷 개수})
```

<br>

API 호출 수와 작업 성공 개수 세는 로직은 다음과 같습니다.

- API 호출 수: src/result의 job_list 파일의 라인 수
- 작업 성공 개수: job을 확인하여 작업 성공 여부를 확인하여 성공 횟수를 카운트

** KT Cloud API는 비동기로 진행하며, API 성공은 API 호출 성공을 의미하며, 최종 스냅샷 생성 또는 삭제를 뜻하는 것이 아닙니다.

<br>

텔레그램 전송에 성공했다면 다음과 같이 로그 메세지가 남습니다.

- 스냅샷 API 작업 실패 기록 
- 텔레그램 메세지 전송에 성공 여부

```commandline
[2024-09-27 10:10:19] [ERROR] 스냅샷 API 실패 - 명령어: CreateSnapshotCmd, 디스크 또는 스냅샷 이름: ROOT-558704, 에러 메세지: Failed to create snapshot due to an internal error creating snapshot for volume 758003
[2024-09-27 10:10:21] [INFO] 텔레그램 메세지 전송 성공
```

<br>

## 활용 예시

위의 파일을 활용하여 2주 지난 스냅샷을 삭제하고 매주 스냅샷 생성하는 crontab을 작성할 수 있습니다.

```bash
vi /etc/crontab
```

```bash
# 매주 토요일 오전 2시 - 13일 전에 생성된 스냅샷 삭제
0 2 * * 6 user python3 /usr/local/mz/snapshot/src/delete_snapshot.py --config=/usr/local/mz/snapshot/config/config.yml  --del_day=14d > /usr/local/mz/snapshot/log/snapshot.log 2>&1

# 매주 일요일 오전 2시 - 스냅샷 생성
0 2 * * 7 user python3 /usr/local/mz/snapshot/src/create_snapshot.py --config=/usr/local/mz/snapshot/config/config.yml  --disk_snapshot_list=/usr/local/mz/snapshot/config/disk_list >> /usr/local/mz/snapshot/log/snapshot.log 2>&1

# 매주 월요일 오전 9시 30분 - 스냅샷 삭제&생성 결과 텔레그램 전송
30 9 * * 2 user python3 /usr/local/mz/snapshot/src/telegram.py --config=/usr/local/mz/snapshot/config/config.yml >> /usr/local/mz/snapshot/log/snapshot.log 2>&1
```