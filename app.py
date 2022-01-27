import logging
import os
import boto3
from botocore.exceptions import ClientError

ENDPOINT_URL_AWS = None # Connect to AWS Endpoint
ENDPOINT_URL_4xx = 'http://localhost:8080/4xx/' # Connect to local mock, return 400
ENDPOINT_URL_5xx = 'http://localhost:8080/5xx/' # Connect to local mock, return 500

ENDPOINT_URL = os.getenv('ENDPOINT_URL', None)

TABLE_NAME = os.getenv('TABLE_NAME', 'test')

class TestApp():

    def __init__(self, endpoint_url = None):
        self.logger = logger.getChild('App')
        self.logger.debug('Constructor invoked.')
        self.dynamodb = boto3.resource('dynamodb', endpoint_url = endpoint_url)

    def test_get_item(self, pk):
        table = self.dynamodb.Table(TABLE_NAME)

        try:
            response = table.get_item(Key = {'pk': pk})
        except ClientError as e:
            self.logger.error(f"{e.response['ResponseMetadata']['HTTPStatusCode']} Error")
            self.logger.error(f"Error Code: {e.response['Error']['Code']}")
            self.logger.error(e)
        else:
            self.logger.info(response['Item'])
        
def init_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(os.getenv('LOG_LEVEL', 'DEBUG'))
    formatter = logging.Formatter("%(asctime)s %(name)s:%(lineno)s [%(levelname)s] %(funcName)s : %(message)s", "%Y-%m-%dT%H:%M:%S%z")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

if __name__ == '__main__':
    logger = init_logger()
    logger.info(f"Endpoint URL : {ENDPOINT_URL}")

    app = TestApp(endpoint_url = ENDPOINT_URL)
    app.test_get_item(pk = '1')
