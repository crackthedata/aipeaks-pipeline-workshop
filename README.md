# Welcome to AI Peaks

**From 0 to Pipeline using Kubernetes**  
*Author: Pete George*  
  
## Whattaya cryin' about?
I'm from a big Italian family. When I was a child, my father would collect every receipt he had in his wallet so he could reconcile them against his bank statement the following month.  

![bulging-wallet](https://github.com/crackthedata/aipeaks-pipeline-workshop/assets/87875118/b95ababc-880c-431c-aeeb-933e1e69d9d4)

What if he had a tool that would help him?  
What if that tool could extract the text in those receipts for him?

Let's help Pete's dad!

We are going to build that tool today!  

## Step 1: Using Donut locally
[Donut](https://arxiv.org/abs/2111.15664) is a model that enables VDU (Visual Document Understanding). It consists of an image transformer encoder and an autoregressive text transformer decoder that is able to "understand" documents in a new way that does not involve OCR (Optical Character Recognition), along with the performance hits and error-prone methods.

Donut can be installed from Pypi using
```
pip install donut-python
```  

At the time of this workshop, the Donut package was not yet compatible with the latest versions of `timm` and `transformers` that ship with PyTorch. To get Donut to work, we must roll back to compatible versions of these packages (don't worry, this is done automatically in Step 2 and 3)  

```
pip install timm==0.5.4 transformers==4.25.1
```

Run `test-metaflow.py` on your computer to view the extracted text from `receipt_test.jpg`, which does a good job of extracting text from the receipt image:

```
{'predictions': [[{'menu': [{'nm': 'Made by you"', 'discountprice': '(386)', 'price': '767-7495'}, {'num': [{'cnt': 'BlvD', 'discountprice': '-0261', 'price': 'BlvD'}, {'nm': 'SALE'}], 'discountprice': '1/04/22', 'price': '13:03'}, {'nm': '2002 HOLIDAY SALE', 'num': '0659,9010,002', 'price': '19.99'}, {'nm': 'ST TREND STYLE PH', 'num': '1924007624', 'unitprice': '@ 6.00', 'cnt': '1', 'price': '5.99'}, {'nm': 'GA LISEED REFINE', 'price': '15.99'}, {'nm': 'CPN GET ITM20X', 'unitprice': '@ 12.79', 'cnt': '1', 'price': '12.79'}, {'nm': 'YOU SAVED $ 320-', 'num': {'unitprice': 'IN20%'}, 'price': '24.77'}, {'nm': 'Sales Tax 6.5%'}], 'subtotal_price': '26.65', 'discount_price': '26.65', 'service_price': '26.65', 'tax_price': '1.63', 'etc': ['26.65', '', '', '', 'VISA CREDIT']}, {'nm': 'AID: A00000000010', 'num': [{'price': '08900'}, {'nm': 'TUR: TSI: E800', 'cnt': '8*00', 'price': '03/04/22'}, {'nm': 'Thes receipt expires at'}, {'nm': 'Click. Bug. Create. Shop michaels.com', 'price': 'today!'}, {'nm': 'Gtjef Savings & Inspiration* SIGNP'}], 'price': '273283'}, {'nm': 'with a link To Join Michels', 'price': 'alerts.'}, {'nm': 'Aaron Brothers'}]]}
```

It's not perfect and we can retrain the model using PyTorch and more receipt images, but you get the idea.  

The scope of this workshop is to utilize scalable compute to run our ML models more efficiently, not retraining them using PyTorch (at least not yet). If you're interested or need assistance in retraining our Donut model using PyTorch, please contact me directly.  

## Step 2: Containerization
#### Install Docker Desktop
Docker Desktop can be found [here](https://docs.docker.com/desktop/install/windows-install/)

#### Install kubectl as a toolkit for running Kubernetes locally
Docker Desktop has its own version of `kubectl`, but follow these instructions if you need to install it manually in the future.

For the latest version of `kubectl` at the time of this workshop, run 

```
curl.exe -LO "https://dl.k8s.io/release/v1.28.2/bin/windows/amd64/kubectl.exe"
```  

Verify the checksum and test the installation, as described [here](https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/).

#### Install Minikube as a local cluster management tool

Using Windows PowerShell as Administrator, download and run the installer

```
New-Item -Path 'c:\' -Name 'minikube' -ItemType Directory -Force
Invoke-WebRequest -OutFile 'c:\minikube\minikube.exe' -Uri 'https://github.com/kubernetes/minikube/releases/latest/download/minikube-windows-amd64.exe' -UseBasicParsing
```

And don't forget to add the location of the `minikube.exe` binary to your `PATH`

#### Build the docker image

`cd` to the local repository location (with the `Dockerfile` present) and build the docker image that will pull the latest version of Ubuntu from Docker Hub, install Python 3.12, install Donut, and configure the environment so we can run it as a container. We're going to call this image `aipeaks` for now.

```
docker build -t aipeaks .
```  
 
#### Let's test our image locally using Metaflow
Execute the docker image in a container

```
docker run -it aipeaks
```  

In the container's terminal, set environment variables so we can connect to our S3 bucket, which contains our test images

```
export AWS_ACCESS_KEY_ID=my_aws_access_key_id
export AWS_SECRET_ACCESS_KEY=my_aws_secret_access_key`
```  

Now run `flow.py`, which will take 2 images from our S3 bucket and run Donut on them locally.

```
python3 flow.py run
```  

#### Configuring Minikube
In a terminal, start Minikube

```
minikube start
```   

For cluster monitoring, open a Minikube dashboard in a separate terminal. Keep this terminal session running for as long as you need monitoring as closing it will kill the dashboard.

```
minikube dashboard
```   
Minikube comes with its own docker service. In the first terminal, execute 

```
@FOR /f "tokens=*" %i IN ('minikube -p minikube docker-env --shell cmd') DO @%i
```

This will switch docker commands running in this terminal to run against the minikube cluster. 

View the images available in the minikube cluster with `docker image ls`. Notice that our `aipeaks` image is not there. We can either push our `aipeaks` image to the minikube cluster, or we can build the `aipeaks` image directly inside the minikube cluster. For the purpose of simplicity, let's build our `aipeaks` image directly in the minikube cluster with `docker build -t aipeaks .` . Sometimes, the minikube cluster has a separate context that does not align with docker. If the image build fails, update the context using `docker context use default` so minikube can pick up the new context.

If you want to explore the former option, check [this](https://minikube.sigs.k8s.io/docs/handbook/pushing/) for more information. 

We can now create jobs and deployments using `kubectl`. They will show up in the dashboard.

As an example, run `kubectl create job aipeaks-job --image=aipeaks` to create a job. Remember, this image is not optimized yet so your computer (and cluster) will need a lot of availabe memory to run it.

## Step 3: Looking to the clouds
[Metaflow](https://docs.metaflow.org/introduction/what-is-metaflow) is a great Data Science workflow tool that will automatically scale as Data Science Workflows are created and executed. 

Outerbounds, the maintainer of Metaflow, publishes templates to deploy your stack in Azure, GCP, and AWS. They publish a variety of terraform files, helm charts, and YAML configuration files to make standing up cloud infrastructure stacks easy. As an example, checkout `metaflow-cloudformation-setup.yaml` to deploy a basic stack in AWS. This template is just one of the many available the public [Metaflow Github Repository](https://github.com/outerbounds/metaflow-tools/blob/master/aws/cloudformation/metaflow-cfn-template.yml). Setup for the stack took about 10 minutes, which is pretty speedy for a basic sandbox.

In Sagemaker, comment out line 11 in `flow.py`

`#urls = [obj.url for obj in s3.list_paths(['test_images'])]`

and uncomment lines 12 and 17

`urls = [obj.url for obj in s3.list_paths(['lotsa_images'])]`

`@batch(queue='job-queue-aipeaks' ...`

and save it using `Ctrl` + `S` on your keyboard.

We're going to pull from the `lotsa_images` folder in our S3 bucket, which has 99 receipt images instead of 1 image. Metaflow will manage the cluster and scale the compute pods up and down depending on the load.

You could just as easily uncomment line 18 to run `flow.py` in EKS (Amazon Elastic Kubernetes Service).

And kick it off with `python flow.py run`
