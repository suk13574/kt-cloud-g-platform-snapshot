## config file

> 아래 파일들은 config 파일에 대한 설명입니다.

<br>

1. config.yml

모든 파일을 실행시킬 때 필요한 파일이며, `--config` 옵션과 함께 사용됩니다.

yaml 확장자로 아래 형식에 맞추어 작성해야 합니다.

```yaml
kt_cloud:
  account_name: TEST  # KT Cloud 계정명 (이후 텔레그램 방에 전송될 때 사용)
  api_key: YI***************************************  # KT Cloud API Key
  secret_key: fg******************************************************************************  # KT Cloud Secret Key

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