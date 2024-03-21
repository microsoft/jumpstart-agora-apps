#!/bin/sh
echo "Starting model pulling"

echo "Pulling head-pose-estimation"
mkdir -p /models/head-pose-estimation/1
cd /models/head-pose-estimation-adas-0001/1
wget https://jsfiles.blob.core.windows.net/ai-models/head-pose-estimation-adas-0001.bin
wget https://jsfiles.blob.core.windows.net/ai-models/head-pose-estimation-adas-0001.xml

echo "Pulling Yolo8"
mkdir -p /models/yolov8n/1
cd /models/yolov8n/1
wget https://jsfiles.blob.core.windows.net/ai-models/yolov8n.bin
wget https://jsfiles.blob.core.windows.net/ai-models/yolov8n.xml

echo "Pulling weld-porosity-detection"
mkdir -p /models/weld-porosity-detection/1
cd /models/weld-porosity-detection/1
wget https://jsfiles.blob.core.windows.net/ai-models/weld-porosity-detection-0001.bin
wget https://jsfiles.blob.core.windows.net/ai-models/weld-porosity-detection-0001.xml

echo "Pulling human-pose-estimation"
mkdir -p /models/human-pose-estimation/1
cd /models/human-pose-estimation/1
wget https://jsfiles.blob.core.windows.net/ai-models/human-pose-estimation-0007.bin
wget https://jsfiles.blob.core.windows.net/ai-models/human-pose-estimation-0007.xml

echo "Pulling safety-yolo8"
mkdir -p /models/safety-yolo8/1
cd /models/safety-yolo8/1
wget https://jsfiles.blob.core.windows.net/ai-models/safety-yolo8.bin
wget https://jsfiles.blob.core.windows.net/ai-models/safety-yolo8.xml

echo "Finished pulling models"

echo "Create config.json"
cd /models
echo '{
   "model_config_list": [
        {
           "config": {
               "name": "yolov8n",
               "base_path": "/models/yolov8n",
               "batch_size": "auto"
           }
        },
        {
           "config": {
               "name": "human-pose-estimation",
               "base_path": "/models/human-pose-estimation",
               "batch_size": "auto"
           }
       },
       {
           "config": {
               "name": "weld-porosity-detection",
               "base_path": "/models/weld-porosity-detection",
               "batch_size": "auto"
           }
       },
       {
           "config": {
               "name": "head-pose-estimation",
               "base_path": "/models/head-pose-estimation",
               "batch_size": "auto"
           }
       },
       {
           "config": {
               "name": "safety-yolo8",
               "base_path": "/models/safety-yolo8",
               "batch_size": "auto"
           }
       }
   ],
   "monitoring": {
       "metrics": {
           "enable": true
       }
   }
}' > config.json
echo "Finish configuration"