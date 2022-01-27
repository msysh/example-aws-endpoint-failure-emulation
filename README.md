# Example for Emulating AWS API errors

This is an example application that uses a custom AWS endpoint to emulate an AWS error occurrence on your local machine.

## Abstract

This Python application uses the AWS SDK to connect to a DynamoDB table. And when building the DynamoDB client, a custom endpoint is specified as the connection destination to simulate an error.

Specifically, specify the endpoint with the following code.

```
dynamodb = boto3.resource('dynamodb', endpoint_url = endpoint_url)
```

If `endpoint_url` is `None`, SDK connect AWS endpoint.

**The error message returned from this sample endpoint is different from the actual one.**

### If you want to emulate on AWS...

If you want to emulate this on AWS, you can use API Gateway's Mock response for your custom endpoint.

## Pre-Requirements

* docker (using Nginx for custom endpoint server)
* DynamoDB Table on AWS :  
  _For use case of successful access. If need not, you may not to create it and skip "3-a" too_
    * Table name is "test" or specified environment value `TABLE_NAME`
    * Partition key column name is `pk`, type is "String"
    * Create an item with the string "1" as the partition key (`pk`). 
* AWS Credential that is granted `get item` for the table above.

## How to run example

### 1. Install boto3

if needed, intall boto3

```bash
pip install
```

### 2. Run custom endpoint server

Run docker container.

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

or run `./run-endpoint.sh`

Nginx container is ready and...  
If access `http://localhost:8080/4xx/`, you can get 400 error.  
If access `http://localhost:8080/5xc/`, you can get 500 error.

### 3-a. Run app.py with successful access

In this case, using an endpoint on AWS.

```bash
TABLE_NAME=test \
python app.py
```

You can see like followint output:

```
2022-01-28T00:53:10+0900 __main__:44 [INFO] <module> : Endpoint URL : None
2022-01-28T00:53:10+0900 __main__.App:18 [DEBUG] __init__ : Constructor invoked.
2022-01-28T00:53:11+0900 __main__.App:31 [INFO] test_get_item : {'pk': '1', 'value': '...'}
```

### 3-b. Run app.py with 400 error.

In this case, using a custom endpoint.

```bash
TABLE_NAME=test \
ENDPOINT_URL=http://localhost:8080/4xx/ \
python app.py
```

You can see like following output:

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

### 3-c. Run app.py with 500 error.

In this case, using a custom endpoint.

```bash
TABLE_NAME=test \
ENDPOINT_URL=http://localhost:8080/5xx/ \
python app.py
```

You can see like following output:
_It will take some time to complete as the SDK will retry due to a 500 error. You can see the retries in the access log of the nginx container._

```
2022-01-28T00:59:57+0900 __main__:44 [INFO] <module> : Endpoint URL : http://localhost:8080/5xx/
2022-01-28T00:59:57+0900 __main__.App:18 [DEBUG] __init__ : Constructor invoked.
2022-01-28T01:00:22+0900 __main__.App:27 [ERROR] test_get_item : 500 Error
2022-01-28T01:00:22+0900 __main__.App:28 [ERROR] test_get_item : Error Code: 500
2022-01-28T01:00:22+0900 __main__.App:29 [ERROR] test_get_item : An error occurred (500) when calling the GetItem operation (reached max retries: 9):
```

## License

MIT