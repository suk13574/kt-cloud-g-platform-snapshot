## kt-cloud-g-platform-snapshot

이 프로젝트는 **kt cloud(G 플랫폼)의 스냅샷 백업 자동화**를 위해 만들었습니다. </br>
kt cloud G 플랫폼에 있는 Disk 대상으로 주기별로 스냅샷을 생성, 삭제를 할 수 있으며, 텔레그램 방으로 결과를 확인할 수 있습니다.</br>

해당 코드는 다음 기능을 가지고 있습니다.

- 백업을 위한 지정된 디스크 스냅샷 주기적인 생성, 삭제
- 스냅샷 생성, 삭제 다음 날 9시 30분 결과를 텔레그램 방으로 전송

 </br>

## 🔶 Requirement
- kt cloud @G 플랫폼에서 사용 가능
- kt cloud API key와 텔레그램 메신저 봇 필요
- docker와 같은 컨테이너 런타임 모듈이 설치 필요

</br>

## 🚀 Install

1. **이미지 빌드**

```bash
docker build -t kt-cloud-g-platform-snapshot .
```

2. **config 파일 작성**

config 파일 2개를 모두 작성해줍니다.
config 파일 작성 방법은 아래에 자세하게 나와있습니다.

e.g. /opt/snapshot에 config 파일 작성

```bash
ls /opt/snapshot/
config.yml  disk_list
```

3. **컨테이너 실행**

config 파일 작성한 경로를 컨테이너 내부에 마운트해준다.

컨테이너 내부 경로는 `/etc/snapshot/config/` 로 고정되어 있다.

```bash
docker run -d -v <config 디렉토리 경로>:/etc/snapshot/config/ --name <컨테이너이름> kt-cloud-g-platform-snapshot
```

e.g. /opt.snapshot에 config 파일이 있고, 컨테이너 이름이 snaphost_test인 경우

```bash
docker run -d -v /opt/snapshot/:/etc/snapshot/config/ --name snapshot_test kt-cloud-g-platform-snapshot
```

4. 실행 확인

```bash
docker ps -a

docker logs <컨테이너 이름>
```

</br>

## ⚙️ Configuration
설정 파일은 아래 2가지가 있으며, 형식을 지키지 않으면 오류 발생 및 종료됩니다.
1. config.yml
2. disk_list


### 1. config.yml
해당 설정 파일은 kt cloud 정보, 스냅샷 생성할 주기를 기입합니다.

``` yaml
kt_cloud:
  account_name: <account name>
  api_key: <kt cloud api key>
  secret_key: <kt cloud api secret key>

telegram:
  bot_token: <telegram bot token>
  chat_id: <telegram chat id>

time:
  start_date: YYYY-MM-dd
  cycle: <number>d
  del_cycle: <number>d
  create_time: "HH:MM"
  delete_time: "HH:MM"
```

**kt cloud**

- account_name: 계정명, 임의 지정 가능
- api_key: kt cloud의 api key
- secret_key: kt cloud의 api secret key

**telegram**

- bot_token: 텔레그램 봇 토큰
- chat_id: 봇이 들어가있는 채팅방

**time**

- start_date: 스냅샷 생성 날짜
    - 형식: `YYYY-MM-dd`
    - start_date에 스냅샷 생성을 시작하며, 이미 지난 날짜의 경우 바로 스냅샷 생성을 시작한다.
- cycle: 스냅샷 생성, 삭제 주기
    - 형식: `숫자d`
    - e.g. `7d` - start_date 이후 7일 주기로 스냅샷 생성, 삭제 프로세스를 반복한다.
- del_cycle: 스냅샷 삭제 주기
    - 형식: `숫자d`
    - e.g. `14d` - 14일전 생성된 스냅샷을 삭제한다.
      - cycle과 합쳐 보았을 때, 7일마다 14일전에 생성된 스냅샷을 삭제한다.
- create_time: 스냅샷 생성 시간
    - 형식: `“HH:MM”`
    - 주기적으로 스냅샷 생성 시간을 지정한다.
    - e.g. `“01:00”` - 새벽 1시에 스냅샷 생성을 시작한다.
- delete_time: 스냅샷 삭제 시간
    - 형식: `“HH:MM”`
    - 주기적으로 스냅샷 삭제 시간을 지정한다.
    - e.g. `“12:00”` - 12시에 스냅샷 삭제를 시작한다.


## 2. disk_list
해당 설정 파일은 스냅샷 생성할 디스크 리스트를 작성합니다. </br>
서버에 연결되지 않은 디스크는 스냅샷을 생성할 수 없으니 유의해서 작성하셔야 합니다.

정해진 파일 확장자는 없으며, `디스크이름,서버이름` 순서대로 리스트 형식으로 작성하면 됩니다.

e.g. 작성 예시

```bash
DATA_DISK01,server01
DATA_DISK02,server01
```

> 🚨 Trobleshooting
>
>컨테이너 실행 중 설정 파일로 인해 오류가 발생할 수 있습니다. </br>
아래와 같이 컨테이너 내부에 설정 파일이 존재하는지 확인하시기 바랍니다.
>
> - 컨테이너 내부 코드 경로: /app
> - 컨테이너 내부 설정 파일 경로: /etc/snapshot/config
> - 설정 파일에는 아래 2개의 파일이 존재해야 함
>   - config.yml
>   - disk_list
>
> 만약 설정 파일 경로나 config.yml의 형식이 틀렸다면 코드가 실행되지 않으니, 오류 발생 시 확인해주세요.

</br>

## ▶️ (참고) 텔레그램 메세지를 통한 개수 확인

config.yml에 입력한 cycle마다 스냅샷 생성, 삭제 작업이 자동으로 진행되며, 코드 동작 다음날 09:30(KTS) 텔레그램 채팅방에서 결과 메세지를 확인할 수 있습니다. </br>
메세지에 적힌 숫자의 정확한 의미는 다음과 같습니다.

```bash
생성 수량 비교: <성공 개수>/<job 개수>
삭제 수량 비교: <성공 개수>/<job 개수>
```
여기서 job은 API 호출 개수를 의미합니다. </br>

e.g. 텔레그램 메세지 예시 </br>

![image](https://github.com/user-attachments/assets/a8a5b594-4e8e-48e2-ae60-832d51591b6a)

아래 예시의 경우 생성 API는 총 2개 요청했지만 1개만 성공한 경우입니다. </br></br>

kt cloud api 특성상 api 호출에 성공하여도 실제 요청한 작업은 실패할 수 있습니다. </br>
컨테이너 로그 조회를 통해 실패 사유를 확인할 수 있으니, 실패한 것을 수동으로 생성해주어야 합니다. </br>

</br>

## ▶️ (참고) 이후 스냅샷 생성할 디스크 목록을 수정
컨테이너 동작 중에 스냅샷 생성할 디스크 목록을 수정해야 한다면, 다음과 같이 진행하면 됩니다. </br>

1. 컨테이너 안으로 접속
``` bash
docker exec -it <컨테이너이름> /bin/sh
```
  
2. disk_list 설정 파일 수정

```bash
cd /etc/snapshot/config
vi disk_list  # 수정 후 저장
```
이후 다음 생성 주기 때 자동으로 수정된 버전으로 생성됩니다. </br>
다만 삭제 대상 스냅샷은 이름의 날짜를 확인하여 삭제하므로, 삭제 대상은 변경되지 않습니다.

</br>

## ▶️ (참고) 코드 동작
### snapshot 생성
1. 디스크 리스트 api 호출 → 서버에 연결된 디스크만 정보 추출(디스크명, 서버명, 디스크id)
2. config의 disk_list 한 줄씩 읽음 → 해당되는 디스크id 찾아서 스냅샷 생성 api 호출
3. 스냅샷 생성 api 호출이 완료되면, job id를 create_job_list 파일에 기록

</br>

### snapshot 삭제
1. 삭제 날짜 계산 (오늘 - del_cycle)
2. 스냅샷 리스트 api 호출  → **스냅샷 이름에 삭제 날짜가 포함되어 있으면 삭제 대상**
3. 삭제 대상 스냅샷은 삭제 api 호출
4. 스냅샷 삭제 api 호출이 완료되면, job id를 delete_job_list 파일에 기록

</br>

### telegram 메세지 전송
1. snapshot 삭제 프로세스가 시작하면, 다음날 오전 9시 30분에 텔레그램 메세지가 전송하도록 예약
2. create_job_list와 delete_job_list에서 job이 성공했는지 check api 호출
3. 개수 확인하여 메세지 전송

</br>
