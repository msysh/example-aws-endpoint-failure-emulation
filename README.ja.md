# AWS API エラーをシミュレートするサンプルアプリ

カスタムの AWS エンドポイントを利用して、ローカルマシン上で AWS のエラー発生をシミュレートするサンプルアプリです。

## 概要

この Python アプリでは AWS SDKを利用し DynamoDB テーブルに接続します。DynamoDB クライアント構築時に接続先としてカスタムエンドポイントを指定してエラーを擬似的に発生させます。

具体的には以下のコードでエンドポイントを指定します。

```
dynamodb = boto3.resource('dynamodb', endpoint_url = endpoint_url)
```

`endpoint_url` が None の時、SDK は AWS のエンドポイントに接続しようとします。

**このサンプルのエンドポイントが返すエラーは実際のものとは異なります**

### AWS 上でシミュレートしたい場合...

AWS 上でシミュレートしたい場合は、カスタムエンドポイントを API Gateway の Mock レスポンスで利用するとよいでしょう。

## 事前要件

* docker (Nginx コンテナを使って カスタムエンドポイント サーバを起動します)
* AWS 上の DynamoDB テーブル :
    * 正常系の動作確認のために作成します。不要であれば作成しなくても構いません（手順 3-a もスキップ）
    * テーブル名は "test" もしくは環境変数 `TABLE_NAME` で指定
    * パーティションキーのカラム名で文字列型の `pk` が利用されます。変えたい場合は [app.py]を変更してください
    * パーティションキー（`pk`）に文字列 "1" を指定したアイテムを作成しておく 
* 上記の DynamoDB テーブルに対して `get item` ができる権限のある AWS クレデンシャルがローカルマシン上に必要です

## サンプルの実行方法

### 1. boto3 のインストール

必要であれば boto3 をインストールします。

```bash
pip install
```

### 2. カスタムエンドポイント用サーバの起動

Nginx コンテナを起動します。

```bash
docker run \
  -it \
  --rm \
  --name ddb-endpoint \
  -p 8080:80 \
  -v ${PWD}/endpoint/400.json:/usr/share/nginx/html/400.json \
  -v ${PWD}/endpoint/500.json:/usr/share/nginx/html/500.json \
  -v ${PWD}/endpoint/nginx.conf:/etc/nginx/nginx.conf \
  nginx:latest
```

もしくは、上記のコマンドが記載されている `./run-endpoint.sh` を実行してもよいです。

Nginx が起動し、  
`http://localhost:8080/4xx/` にアクセスすると 400エラーが取得されます。  
`http://localhost:8080/5xc/` にアクセスすると 500エラーが取得されます。

### 3-a. 正常系でのアプリ実行

AWS のエンドポイントを利用して、正常系の動作を確認します。

```bash
TABLE_NAME=test \
python app.py
```

テーブル作成や権限に問題がなければ、テーブル上のパーティションキーが「1」のアイテムを取得できます

```
2022-01-28T00:53:10+0900 __main__:44 [INFO] <module> : Endpoint URL : None
2022-01-28T00:53:10+0900 __main__.App:18 [DEBUG] __init__ : Constructor invoked.
2022-01-28T00:53:11+0900 __main__.App:31 [INFO] test_get_item : {'pk': '1', 'value': '...'}
```

### 3-b. 400系エラーが出るケースでのアプリ実行

このケースではカスタムエンドポイントを指定します。

```bash
TABLE_NAME=test \
ENDPOINT_URL=http://localhost:8080/4xx/ \
python app.py
```

下記のような 400 エラーが取得できます。

```
2022-01-28T00:58:37+0900 __main__:44 [INFO] <module> : Endpoint URL : http://localhost:8080/4xx/
2022-01-28T00:58:37+0900 __main__.App:18 [DEBUG] __init__ : Constructor invoked.
2022-01-28T00:58:38+0900 __main__.App:27 [ERROR] test_get_item : 400 Error
2022-01-28T00:58:38+0900 __main__.App:28 [ERROR] test_get_item : Error Code: 400
2022-01-28T00:58:38+0900 __main__.App:29 [ERROR] test_get_item : An error occurred (400) when calling the GetItem operation: {
    "Error": {
        "Code": "SomeServiceException",
        "Message": "Details/context around the exception or error"
    },
    "ResponseMetadata": {
        "RequestId": "1234567890ABCDEF",
        "HostId": "host ID data will appear here as a hash",
        "HTTPStatusCode": 400,
        "HTTPHeaders": {"header metadata key/values will appear here"},
        "RetryAttempts": 1
    }
}
```

### 3-c. 500系エラーが出るケースでのアプリ実行

このケースではカスタムエンドポイントを指定します。

```bash
TABLE_NAME=test \
ENDPOINT_URL=http://localhost:8080/5xx/ \
python app.py
```

下記のような 500 エラーが取得できます。
_500 エラーにより、AWS SDK が内部でリトライを行うため実行完了までに少し時間を要します。Nginx コンテナのアクセスログでもリトライされているのがわかるかと思います。_

```
2022-01-28T00:59:57+0900 __main__:44 [INFO] <module> : Endpoint URL : http://localhost:8080/5xx/
2022-01-28T00:59:57+0900 __main__.App:18 [DEBUG] __init__ : Constructor invoked.
2022-01-28T01:00:22+0900 __main__.App:27 [ERROR] test_get_item : 500 Error
2022-01-28T01:00:22+0900 __main__.App:28 [ERROR] test_get_item : Error Code: 500
2022-01-28T01:00:22+0900 __main__.App:29 [ERROR] test_get_item : An error occurred (500) when calling the GetItem operation (reached max retries: 9):
```

## ライセンス

MIT