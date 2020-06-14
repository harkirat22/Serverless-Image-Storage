import json
import boto3
import base64
s3 = boto3.client('s3')
def lambda_handler(event, context):
    print event
    if event['httpMethod'] == 'POST' : 
        print event['body']
        data = json.loads(event['body'])
        name = data['name']
        image = data['file']
        image = image[image.find(",")+1:]
        dec = base64.b64decode(image + "===")
        s3.put_object(Bucket='image-object-detection', Key=name, Body=dec)
        return {'statusCode': 200, 'body': json.dumps({'message': 'Image Uploaded Successfully!.'}), 'headers': {'Access-Control-Allow-Origin': '*'}}