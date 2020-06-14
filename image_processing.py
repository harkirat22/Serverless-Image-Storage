import os
import json
import cv2
import io
import boto3
import time
import numpy as np
from PIL import Image

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('image_detection')

def get_labels(labels_path):
    LABELS = open(labels_path).read().strip().split("\n")
    return LABELS
    
def load_model(configpath,weightspath):
    net = cv2.dnn.readNetFromDarknet(configpath, weightspath)
    return net
    
def get_prediction(image,net,LABELS):
    (H, W) = image.shape[:2]

    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
                                 swapRB=True, crop=False)
    net.setInput(blob)
    start=time.time()
    layerOutputs = net.forward(ln)
    print(layerOutputs)
    end = time.time()

    print("[INFO] YOLO took {:.6f} seconds".format(end - start))

    confidences = []
    classIDs = []
    boxes = []
    labels_list =[]
    final_list1 = []
    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > 0.5:
                confidences.append(float(confidence)*100)
                confidences=[str(x) for x in confidences]
                classIDs.append(classID)
                
    for i in range(len(classIDs)):
        labels_list.append(LABELS[classIDs[i]])
        
    for i in range(len(labels_list)):
        # final_list1.append({"label":labels_list[i],"accuracy":confidences[i]})
        final_list1.append(labels_list[i])
    
    print(final_list1)
    # res_dict = {"Objects": final_list1 }
    # to_json = json.dumps(res_dict,indent=1,)
    # return to_json
    return list(dict.fromkeys(final_list1))

strBucket= 'image-object-detection'
wgtkey = 'darknet/yolov3.weights'
wgtfile = '/tmp/yolov3.weights1'
cfgkey = 'darknet/yolov3.cfg'
cfgfile = '/tmp/yolov3.cfg'
namekey = 'darknet/coco.names'
namefile = '/tmp/coco.names'

s3_client.download_file(strBucket, wgtkey, wgtfile)
s3_client.download_file(strBucket, cfgkey, cfgfile)
s3_client.download_file(strBucket, namekey, namefile)

Lables=get_labels(namefile)
nets=load_model(cfgfile,wgtfile)

def create_table_entry(strKey, url, res):
    put_name={"image_id":strKey}
    put_url={"url":url}
    put_res={"tags":res}
    
    put_db={
        "image_id":strKey, 
        "url":url, 
        "tags":res
    }
    print(put_db)
    
    return put_db
    
def lambda_handler(event, context):
    imgfilepath = '/tmp/inputimage.jpg'
    strBucket= event['Records'][0]['s3']['bucket']['name']
    print(strBucket)
    strKey = event['Records'][0]['s3']['object']['key']
    print(strKey)
    url = "https://image-object-detection.s3.amazonaws.com/%s" % (strKey)
    print(url)
    s3_client.download_file(strBucket, strKey, imgfilepath)
    imgfilepath = Image.open(imgfilepath)
    npimg=np.array(imgfilepath)
    image=npimg.copy()
    res=get_prediction(image,nets,Lables)
    print(res)
    entry=create_table_entry(strKey, url, res)
    table.put_item(Item=entry)
    return {
        'statusCode': 200,
        'body': "Image added successfully"
    }
