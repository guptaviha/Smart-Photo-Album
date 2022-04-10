import json
import random
import logging
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection

client = boto3.client('lex-runtime')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

os = OpenSearch(
				hosts=[{'host': 'search-test-photos-rofhj7l33zqhkmcmgvm4fraqqe.us-east-1.es.amazonaws.com','port': 443}], 
				http_auth=('admin', 'Admin@123'), 
				use_ssl = True, 
				verify_certs=True, 
				connection_class=RequestsHttpConnection
		)

def get_restaurant_ids_from_es(query):
    url = "https://search-yelp-restaurant-data-idw5yplh7blonn57r3fi3prbv4.us-east-1.es.amazonaws.com/restaurants/_search?q=" + cuisine + "&pretty"
    response = http.request('GET', url, headers = {'Authorization': 'Basic eWVscDpZZWxwQDEyMw=='})
    resp = json.loads(response.data.decode('utf-8'))
    # ids = []
    print('hello:', resp)
    # for hit in resp['hits']['hits']:
    #     ids.append(hit['_id'])
    # return ids
    
def valid_string(string):
    if string is None:
        return False
    if string == '' or string == ' ':
        return False
    return True
    
def get_labels_from_lex_output(lex_output):
    labels = []
    keys = lex_output.keys()
    if 'Oone' in keys and valid_string(lex_output['Oone']):
        labels.append(lex_output['Oone'])
    if 'Otwo' in keys and valid_string(lex_output['Otwo']):
        labels.append(lex_output['Otwo'])
    if 'Othree' in keys and valid_string(lex_output['Othree']):
        labels.append(lex_output['Othree'])
    return labels
    
def get_images_from_es(labels):
    response = []
    for label in labels:
        ret = os.search({"query": {"match": {"labels": label}}})
        images = ret['hits']['hits']
        for image in images:
            response.append(image['_source'])
    return response

def lambda_handler(event, context):
    
    print('NLPA -- input from client context', context)
    logger.debug('NLPA -- input from client context={}'.format(context))
    
    print('NLPA -- input from client event', event)
    logger.debug('NLPA -- input from client event={}'.format(event))

    client_input = event['message']
    print('NLPA -- input from client', client_input)
    logger.debug('NLPA -- input from client={}'.format(client_input))
    

    lex_response = client.post_text(
        botName='ExtractKeywords',
        botAlias='ExtractKeywordsAlias',
        userId="001",
        sessionAttributes={},
        requestAttributes={},
        inputText= client_input
    )
    
    print('NLPA -- lex response', lex_response)
    # logger.debug('NLPA -- lex response={}'.format(lex_response))
    
    lex_output = lex_response["slots"]
    print('NLPA -- lex output', lex_output)
    labels = get_labels_from_lex_output(lex_output)
    print('labels:', labels)
    response = get_images_from_es(labels)
    print('\t\tmyresponse:', response)
    return {
        'headers': {
            'Access-Control-Allow-Headers' : '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }, 
        'statusCode': 200,
        'body': json.dumps(response)
    }
    logger.debug('NLPA -- lex output={}'.format(lex_output))
    

    print('NLPA -- lex output Oone', lex_output["Oone"])
    logger.debug('NLPA -- lex_output["Oone"]={}'.format(lex_output["Oone"]))
        
    # get_restaurant_ids_from_es(lex_output["Oone"])  
    # get_from_es(lex_output["Oone"])
        
        
    ##LEX RET
    # return {
    #     'headers': {
    #         'Access-Control-Allow-Headers' : '*',
    #         'Access-Control-Allow-Origin': '*',
    #         'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    #         },           
    #     'statusCode': 200,
    #     'messages':[{
    #         "type":'unstructured',
    #         "unstructured":{
    #                 # 'text': "I’m still under development, Viha. Please come back later."
    #                 'text': lex_output
    #             }
    #         }]
    #     }
