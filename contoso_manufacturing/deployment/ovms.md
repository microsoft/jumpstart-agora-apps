# Deployment of OpenVino Model Server (OVMS)

[OpenVino Model Server](https://docs.openvino.ai/2024/ovms_what_is_openvino_model_server.html) hosts models and makes them accessible to software components over standard network protocols: a client sends a request to the model server, which performs model inference and sends a response back to the client.

<img alt="OpenVino Model Server" src="https://docs.openvino.ai/2024/_images/ovms_diagram.png" width="800" />

## Node setup
These instructions are for configuring OVMS for AKS Edge Essentials. (Note that the Ubuntu + K3s deployment will be covered separately.) To set up the node correctly, you'll need to copy the [ovms-setup.sh](../scripts/ovms-setup.sh) script to the Linux node and then run it. This script performs the following actions:

To set the node, run the following steps:

1. Run the OpenVino Operator Toolkit

   If you are using AKS Ede Essentials, run the following from the host machine:
    ```powershell
    Invoke-AksEdgeNodeCommand -NodeType Linux -command "curl -sL https://github.com/operator-framework/operator-lifecycle-manager/releases/download/v0.27.0/install.sh | bash -s v0.27.0"
    ```

    If you are using Ubuntu/Linux, run the following inside the node:
   ```bash
   curl -sL https://github.com/operator-framework/operator-lifecycle-manager/releases/download/v0.27.0/install.sh | bash -s v0.27.0
   ```
    
1. Install prerequisites (ovms-operator and local-path-storage)

    If you are using AKS Ede Essentials, run the following from the host machine:
    ```powershell
    kubectl apply -f https://raw.githubusercontent.com/Azure/AKS-Edge/main/samples/storage/local-path-provisioner/local-path-storage.yaml
    kubectl create -f https://operatorhub.io/install/ovms-operator.yaml
    ```

   If you are using Ubuntu/Linux, run the following inside the node:
   ```bash
    kubectl create -f https://operatorhub.io/install/ovms-operator.yaml
   ```

## OVMS Deployment

The following instructions will do the following:

1. Create the ovms-config map using the **config.json** file to set up the models to be loaded and the path for each model 
1. Create the **ovms-pvc** Persistent Volume Claim (PVC)
1. Run the **model-downloader** to download all teh required models
1. Deploy OVMS using a Persistent Volume Claim (PVC) and mounts the models that were previously downloaded.

To deploy the solution, follow these steps:

1. Create the **ovms-config** configMap
    ```powershell
    kubectl create configmap ovms-config --from-file=.\configs\config.json
    ```

1. Apply the [ovms-models-setup.yaml](./yamls/ovms-models-setup.yaml)
    ```powershell
    kubectl apply -f .\yamls\ovms-models-setup.yaml
    ```
    
1. Wait until the **model-downloader-job** status changes from *Pending* to *Completed*.
    ```powershell
    PS C:\jumpstart-agora-apps\contoso_manufacturing\deployment> kubectl get pods -w
    NAME                         READY   STATUS      RESTARTS   AGE
    model-downloader-job-4n765   0/1     Completed   0          7s
    ```

1. Apply the [ovms-setup.yaml](./yamls/ovms-setup.yaml)
    ```powershell
    kubectl apply -f .\yamls\ovms-setup.yaml
    ```
    
1. If everything was correctly deployed, you should see the following
    ```powershell
    PS C:\jumpstart-agora-apps\contoso_manufacturing\deployment> kubectl get pods
    NAME                        READY   STATUS    RESTARTS   AGE
    model-downloader-job-pdjwj   0/1     Completed   0          8m5s
    ovms-6f4b579c7b-2rwl8        1/1     Running     0          2m5s
    ```
    
1. Check the **ovms-sample** service IP
    ```powershell
    PS C:\Users\jumpstart-agora-apps\contoso_manufacturing\deployment> kubectl get svc
    NAME         TYPE           CLUSTER-IP    EXTERNAL-IP   PORT(S)                         AGE
    kubernetes   ClusterIP      10.43.0.1     <none>        443/TCP                         26m
    ovms         LoadBalancer   10.43.75.87   192.168.0.4   8080:32060/TCP,8081:31634/TCP   2m36s
    ```
1. Check that models are being loaded correctly

    If you are using AKS Ede Essentials, run the following from the host machine:
    ```powershell
    Invoke-AksEdgeNodeCommand -NodeType Linux -command "curl http://<ovms-external-service-ip>:<extenral-service-port/v1/config"
    ```

    If you are using Ubuntu/Linux, run the following inside the node:
   ```bash
    curl http://<ovms-external-service-ip>:<extenral-service-port>/v1/config
   ```
    
    If all models are loaded correctly, you should see something similir to the following:
    ```powershell
    {
        "head-pose-estimation": {
            "model_version_status": [
                {
                    "version": "1",
                    "state": "AVAILABLE",
                    "status": {
                        "error_code": "OK",
                        "error_message": "OK"
                    }
                }
            ]
        },
        "human-pose-estimation": {
            "model_version_status": [
                {
                    "version": "1",
                    "state": "AVAILABLE",
                    "status": {
                        "error_code": "OK",
                        "error_message": "OK"
                    }
                }
            ]
        },
        "safety-yolo8": {
            "model_version_status": [
                {
                    "version": "1",
                    "state": "AVAILABLE",
                    "status": {
                        "error_code": "OK",
                        "error_message": "OK"
                    }
                }
            ]
        },
        "time-series-forecasting-electricity": {
            "model_version_status": [
                {
                    "version": "1",
                    "state": "AVAILABLE",
                    "status": {
                        "error_code": "OK",
                        "error_message": "OK"
                    }
                }
            ]
        },
        "weld-porosity-detection": {
            "model_version_status": [
                {
                    "version": "1",
                    "state": "AVAILABLE",
                    "status": {
                        "error_code": "OK",
                        "error_message": "OK"
                    }
                }
            ]
        },
        "yolov8n": {
            "model_version_status": [
                {
                    "version": "1",
                    "state": "AVAILABLE",
                    "status": {
                        "error_code": "OK",
                        "error_message": "OK"
                    }
                }
            ]
        },
        "yolov8-pose": {
            "model_version_status": [
                {
                    "version": "1",
                    "state": "AVAILABLE",
                    "status": {
                        "error_code": "OK",
                        "error_message": "OK"
                    }
                }
            ]
        }
    }
    ```

## Check OVMS inferencing

The final step in this guide is to verify the correct functionality of the OVMS inferencing server by sending an image to the OVMS REST API and examining the resulting inferencing output.

1. Create a new Pod deployment for running a Python sample app
    ```powershell
    kubectl create deployment client-test --image=python:3.8.13 -- sleep infinity
    ```
1. Wait until the Python Pod is running and then exec into it
    ```powershell
    kubectl exec -it $(kubectl get pod -o jsonpath="{.items[0].metadata.name}" -l app=client-test) -- /bin/sh
    ```

1. Install the Python dependencies and sample apps inside the Pod
    ```bash
    cd /tmp
    wget https://raw.githubusercontent.com/openvinotoolkit/model_server/releases/2024/0/demos/object_detection/python/object_detection.py
    wget https://raw.githubusercontent.com/openvinotoolkit/model_server/releases/2024/0/demos/object_detection/python/requirements.txt
    wget https://raw.githubusercontent.com/openvinotoolkit/open_model_zoo/master/data/dataset_classes/coco_91cl.txt
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
1. Download the image to test the inference
    ```bash
    wget https://storage.openvinotoolkit.org/repositories/openvino_notebooks/data/data/image/coco_bike.jpg
    ```
    <img alt="Dog test" src="https://storage.openvinotoolkit.org/repositories/openvino_notebooks/data/data/image/coco_bike.jpg" width="400" />

1. Create the `object_detection.py` sample app
    ```bash
    cat << EOF > object_detection.py
    from ovmsclient import make_grpc_client
    import cv2
    import numpy as np
    import argparse
    import random
    from typing import Optional, Dict

    parser = argparse.ArgumentParser(description='Make object detection prediction using images in binary format')
    parser.add_argument('--image', required=True, help='Path to a image in JPG or PNG format')
    parser.add_argument('--service_url', required=False, default='localhost:9000', help='Specify url to grpc service. default:localhost:9000', dest='service_url')
    parser.add_argument('--model_name', default='faster_rcnn', help='Model name to query. default: faster_rcnn')
    parser.add_argument('--labels', default="coco_91cl.txt", type=str, help='Path to COCO dataset labels with human readable class names')
    parser.add_argument('--input_name', default='input_tensor', help='Input name to query. default: input_tensor')
    parser.add_argument('--model_version', default=0, type=int, help='Model version to query. default: latest available')

    args = parser.parse_args()
    image = cv2.imread(filename=str(args.image))
    image = cv2.cvtColor(image, code=cv2.COLOR_BGR2RGB)
    resized_image = cv2.resize(src=image, dsize=(255, 255))
    network_input_image = np.expand_dims(resized_image, 0)

    client = make_grpc_client(args.service_url)
    inputs = { args.input_name: network_input_image }
    response = client.predict(inputs, args.model_name, args.model_version)

    with open(args.labels, "r") as file:
        coco_labels = file.read().strip().split("\n")
        coco_labels_map = dict(enumerate(coco_labels, 1))

    detection_boxes: np.ndarray = response["detection_boxes"]
    detection_classes: np.ndarray = response["detection_classes"]
    detection_scores: np.ndarray = response["detection_scores"]
    num_detections: np.ndarray = response["num_detections"]

    for i in range(100):
        detected_class_name = coco_labels_map[int(detection_classes[0, i])]
        score = detection_scores[0, i]
        label = f"{detected_class_name} {score:.2f}"
        if score > 0.5:
            print(label)
    EOF
    ```

1. Run the **object_detection.py** sample app
    ```bash
    python object_detection.py --image coco_bike.jpg --model_name resnet-50 --service_url ovms-sample:8080
    ```
1. If everything is working correctly, you should see the following
    ```bash
    # python object_detection.py --image coco_bike.jpg --model_name resnet-50 --service_url ovms-sample:8080
    dog 0.98
    bicycle 0.94
    bicycle 0.93
    car 0.88
    bicycle 0.84
    truck 0.59
    bicycle 0.56
    bicycle 0.54
    ```
