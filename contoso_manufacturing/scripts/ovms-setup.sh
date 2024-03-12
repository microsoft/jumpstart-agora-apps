echo "Apply Kubernetes local-storage class"
kubectl apply -f https://raw.githubusercontent.com/Azure/AKS-Edge/main/samples/storage/local-path-provisioner/local-path-storage.yaml

echo "Creating models repository"
mkdir -p /var/lib/rancher/k3s/storage
mkdir -p /var/lib/rancher/k3s/storage/models 
chmod -R 777 /var/lib/rancher/k3s/storage/models

echo "Downloading Model 1 - horizontal-text-detection"
cd /var/lib/rancher/k3s/storage//models
mkdir -p horizontal-text-detection/1
cd horizontal-text-detection/1
wget https://storage.openvinotoolkit.org/repositories/open_model_zoo/2022.3/models_bin/1/horizontal-text-detection-0001/FP32/horizontal-text-detection-0001.xml
wget https://storage.openvinotoolkit.org/repositories/open_model_zoo/2022.3/models_bin/1/horizontal-text-detection-0001/FP32/horizontal-text-detection-0001.bin

echo "Downloading Model 2 - weld-porosity-detection"
cd /var/lib/rancher/k3s/storage//models
mkdir -p weld-porosity-detection/1
cd weld-porosity-detection/1
wget https://raw.githubusercontent.com/Azure/AKS-Edge-Labs/main/Samples/Welding-Demo/modules/modules/pipeline/models/weld_porosity/FP32/weld-porosity-detection-0001.bin
wget https://raw.githubusercontent.com/Azure/AKS-Edge-Labs/main/Samples/Welding-Demo/modules/modules/pipeline/models/weld_porosity/FP32/weld-porosity-detection-0001.xml

echo "Downloading Model 3 - resnet-50"
cd /var/lib/rancher/k3s/storage/models
mkdir -p resnet-50/1
wget https://storage.googleapis.com/tfhub-modules/tensorflow/faster_rcnn/resnet50_v1_640x640/1.tar.gz
tar xzf 1.tar.gz -C resnet-50/1 && chmod -R 755 resnet-50/1
rm 1.tar.gz

echo "Finish downloading models"
echo "Setting permissions 0755"
cd /var/lib/rancher/k3s/storage/models
chmod -R 0755 ./*

echo "Installing OpenVino Toolkit Operator"
curl -sL https://github.com/operator-framework/operator-lifecycle-manager/releases/download/v0.27.0/install.sh | bash -s v0.27.0
kubectl create -f https://operatorhub.io/install/ovms-operator.yaml