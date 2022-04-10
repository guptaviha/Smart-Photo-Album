import boto3
import json
import logging
import urllib
from opensearchpy import OpenSearch, RequestsHttpConnection
import time

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
rekognition = boto3.client('rekognition')
s3Client = boto3.client('s3')

os = OpenSearch(
				hosts=[{'host': 'search-test-photos-rofhj7l33zqhkmcmgvm4fraqqe.us-east-1.es.amazonaws.com','port': 443}], 
				http_auth=('admin', 'Admin@123'), 
				use_ssl = True, 
				verify_certs=True, 
				connection_class=RequestsHttpConnection
		)

def get_bucket_and_key(event):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    return bucket, key
    
def get_label_string(all_labels):
    labels = ''
    for label in all_labels:
        labels += label + ', '
    labels = labels[:len(labels)-2]
    return labels

def save_to_es(bucket, key, labels):
    print('NLPA -- Saving', key, 'from', bucket, 'to ES')
    body = {
      'bucket': bucket,
      'key': key,
      'createdTimestamp': str(int(time.time())),
      'labels': labels
    }
    ret = os.index(index="tests", id=key, body=body, refresh = True)
    print('NLPA -- ES Push response:', ret)
    return

def lambda_handler(event, context):
    logger.debug('NLPA -- index-photos-lf1 in invoked')
    
    bucket, key = get_bucket_and_key(event)
    print('SEARCHING FOR', key, 'in', bucket)
    response = rekognition.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        }    
    )
    metadata = s3Client.head_object(Bucket=bucket, Key=key)
    all_labels = metadata['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels'].split(',')
    
    rek_labels = response['Labels']
    if len(rek_labels) > 0:
        for label in rek_labels:
            all_labels.append(label['Name'])
        save_to_es(bucket, key, all_labels)
        labels = get_label_string(all_labels)
        msg = 'All labels associated with your image are: ' + labels 
        print(msg)
        return {
            'headers': {
            'Access-Control-Allow-Headers' : '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }, 
            'statusCode': 200,
            'body': json.dumps(msg)
        }
    else:
        return {
            'headers': {
            'Access-Control-Allow-Headers' : '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }, 
            'statusCode': 400,
            'body': json.dumps('No labels received from REKOGNITION')
        }
