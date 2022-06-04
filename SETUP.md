### Setup Kubernetes Cluster

This notebook provides a relatively simple way to get your enviornment set up correctly to follow the examples.

You will need to make sure you have all the requirements highlighed in the `Requirements` section in the main page.

#### Install and setup Istio

We use istio for ingress routing: https://docs.seldon.io/projects/seldon-core/en/v1.13.1/ingress/istio.html


```python
!istioctl install -y
```

    [32m✔[0m Istio core installed                                                          
    [32m✔[0m Istiod installed                                                              
    [32m✔[0m Ingress gateways installed                                                    
    [32m✔[0m Installation complete                                                         
    Thank you for installing Istio 1.11.  Please take a few minutes to tell us about your install/upgrade experience!  https://forms.gle/kWULBRjUv7hHci7T6



```bash
%%bash
kubectl apply -n istio-system -f - << END
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: seldon-gateway
spec:
  selector:
    istio: ingressgateway # use istio default controller
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
END
```

    gateway.networking.istio.io/seldon-gateway created


#### Setup Seldon Core
We install seldon core as per the documentation https://docs.seldon.io/projects/seldon-core/en/v1.13.1/workflow/install.html#install-seldon-core-with-helm


```bash
%%bash
kubectl create ns seldon-system
helm upgrade --install \
    seldon-core seldon-core-operator \
    --repo https://storage.googleapis.com/seldon-charts  \
    --set usageMetrics.enabled=true --namespace seldon-system \
    --set istio.enabled="true" --set istio.gateway="seldon-gateway.istio-system.svc.cluster.local" \
    --version 1.13.1
```

    Release "seldon-core" has been upgraded. Happy Helming!
    NAME: seldon-core
    LAST DEPLOYED: Mon Apr 11 21:04:42 2022
    NAMESPACE: seldon-system
    STATUS: deployed
    REVISION: 2
    TEST SUITE: None


    Error from server (AlreadyExists): namespaces "seldon-system" already exists


#### Setup & configure MinIO

We install minio as a object bucket storage to upload artifacts https://docs.seldon.io/projects/seldon-core/en/v1.13.1/examples/minio_setup.html


```bash
%%bash
kubectl create ns minio-system
helm repo add minio https://helm.min.io/
helm upgrade --install minio minio/minio \
    --set accessKey=minioadmin \
    --set secretKey=minioadmin \
    --namespace minio-system
```

    namespace/minio-system created
    "minio" already exists with the same configuration, skipping
    Release "minio" does not exist. Installing it now.
    NAME: minio
    LAST DEPLOYED: Tue May 10 17:00:50 2022
    NAMESPACE: minio-system
    STATUS: deployed
    REVISION: 1
    TEST SUITE: None
    NOTES:
    Minio can be accessed via port 9000 on the following DNS name from within your cluster:
    minio.minio-system.svc.cluster.local
    
    To access Minio from localhost, run the below commands:
    
      1. export POD_NAME=$(kubectl get pods --namespace minio-system -l "release=minio" -o jsonpath="{.items[0].metadata.name}")
    
      2. kubectl port-forward $POD_NAME 9000 --namespace minio-system
    
    Read more about port forwarding here: http://kubernetes.io/docs/user-guide/kubectl/kubectl_port-forward/
    
    You can now access Minio server on http://localhost:9000. Follow the below steps to connect to Minio server with mc client:
    
      1. Download the Minio mc client - https://docs.minio.io/docs/minio-client-quickstart-guide
    
      2. Get the ACCESS_KEY=$(kubectl get secret minio -o jsonpath="{.data.accesskey}" | base64 --decode) and the SECRET_KEY=$(kubectl get secret minio -o jsonpath="{.data.secretkey}" | base64 --decode)
    
      3. mc alias set minio-local http://localhost:9000 "$ACCESS_KEY" "$SECRET_KEY" --api s3v4
    
      4. mc ls minio-local
    
    Alternately, you can use your browser or the Minio SDK to access the server - https://docs.minio.io/categories/17


#### Port orward Minio to access locally

Once minio is runnning you need to open another terminal and run:
```
kubectl port-forward -n minio-system svc/minio 9000:9000
```

#### Create client and bucket

We can now configure our client to talk to the minio inside of the cluster


```python
!mc config host add minio-seldon http://localhost:9000 minioadmin minioadmin
```

    [m[32mAdded `minio-seldon` successfully.[0m
    [0m


```python
!mc mb minio-seldon/fml-artifacts/ -p
```

    [m[32;1mBucket created successfully `minio-seldon/fml-artifacts/`.[0m
    [0m


```bash
%%bash
kubectl apply -f - << END
apiVersion: v1
kind: Secret
metadata:
  name: seldon-init-container-secret
type: Opaque
stringData:
  RCLONE_CONFIG_S3_TYPE: s3
  RCLONE_CONFIG_S3_PROVIDER: minio
  RCLONE_CONFIG_S3_ACCESS_KEY_ID: minioadmin
  RCLONE_CONFIG_S3_SECRET_ACCESS_KEY: minioadmin
  RCLONE_CONFIG_S3_ENDPOINT: http://minio.minio-system.svc.cluster.local:9000
  RCLONE_CONFIG_S3_ENV_AUTH: "false"
END
```

    secret/seldon-init-container-secret created



```python

```
