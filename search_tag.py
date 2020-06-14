import boto3
import json

def lambda_handler(event, context):
    print(event)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('image_detection')
    search_tags = event['usertags']
    print(search_tags)
    list_url = []
    
    table_metadata = table.scan()
    print(table_metadata)
    
    table_data = table_metadata["Items"]
    print(table_data)
    
    for entry in table_data:
        flag = 0
        print(entry)
        for tag in entry["tags"]:
            print(tag)
            for tag_search in search_tags:
                if tag == tag_search:
                    flag += 1
        if flag == len(search_tags):
            list_url.append(entry["url"])
    
    url_json = {}
    url_json["links"] = list(dict.fromkeys(list_url))
    return {'statusCode': 200, 'body': json.dumps(url_json), 'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}}