import json
import pprint
import os
try:
    from botocore.vendored import requests
except:
    import requests

token  = os.environ.get('v2_token')

def optimizely_request(http_verb, resource='/', qs_params={}, payload={}):  
    http_verb = http_verb.lower()
    session   = requests.Session()
    url       = 'https://api.optimizely.com/{version}{resource}'.format(version='v2', resource=resource)
    headers   = {"Authorization":"Bearer {}".format(token)}
    if http_verb in ['post', 'patch']:
        headers['Content-Type'] = 'application/json'
    req      = requests.Request(http_verb.lower(), url, json=payload, headers=headers, params=qs_params)
    prepped  = session.prepare_request(req)
    response = session.send(prepped)
    if response.status_code > 299:
        raise Exception('Unable to make request: \n{}'.format(response.text))
    try:
        return response.json()
    except Exception as e:
        return []

def enable_feature(feature_id, environment_key):
    update_payload = optimizely_request('get', '/features/{}'.format(feature_id))
    update_payload['environments'][environment_key]['rollout_rules'][0]['enabled'] = True
    update_payload['environments'][environment_key]['rollout_rules'][0]['percentage_included'] = 10000
    response = optimizely_request('patch', '/features/{}'.format(feature_id), payload=update_payload)
    return response  

def disable_feature(feature_id, environment_key):
    update_payload = optimizely_request('get', '/features/{}'.format(feature_id))
    update_payload['environments'][environment_key]['rollout_rules'][0]['enabled'] = False
    update_payload['environments'][environment_key]['rollout_rules'][0]['percentage_included'] = 10000
    response = optimizely_request('patch', '/features/{}'.format(feature_id), payload=update_payload)
    return response      

def lambda_handler(event, context):
    """
    The feature_id, state & environment will be passed in the CloudWatch Event
    The Optimizely v2_token should be set as an environment variable in the Lambda function
    """
    print('Debug::: ', event, os.environ.get('v2_token'))    
    if(event.get('state', None) == 'on'):
        enable_feature(event.get('feature_id'), event.get('environment'))
    else:
        disable_feature(event.get('feature_id'), event.get('environment'))
    return {
        'statusCode': 200,
        'body': json.dumps('Enabled feature')
    }
