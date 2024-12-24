# apihub

MMC API hub hosts all API in MMC domain. The template.yaml deploys the APIs in an ECS cluster with a load balancer in front. The pipeline.yaml creates pipeline for the AWS ECS API service.

![Map My Crop API](https://cronitor.io/badges/3dBIJZ/production/ZevT31nhh-u-R1100Xj7NEWBv-w.svg)

# Start the application

- Make you have python 3.12+ installed

```bash
# create virtual envirionment
python3 -m venv .venv

# activat the envirionment
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# make sure you have the .env
cp code/sample.env code/.env

# run dev code
cd code
uvicorn main:app --port 8000 --reload

# Make sure settings are added .env
# Running alembic migrations
cd code
alembic upgrade heads

```

Alternatively, you can use docker-compose

```
docker compose up
```

## Push to ECR (Will be moved to build file)

Make sure that you have the latest version of the AWS CLI and Docker installed. For more information,

Retrieve an authentication token and authenticate your Docker client to your registry.Use the AWS CLI:

```
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
```

Build your Docker image using the following command. For information on building a Docker file from scratch see the instructions here

```
docker build -t mmc-api .

```

After the build completes, tag your image so you can push the image to this repository:

```
docker tag mmc-api:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_IAMGE:latest
```

Run the following command to push this image to your newly created AWS repository:

```
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_IAMGE:latest
```

## Deploy to AWS

```
aws cloudformation create-stack --stack-name [STACK_NAME] --template-body file://[TEMPLATE].yaml --parameters ParameterKey=[NAME],ParameterValue={VALUE}

```

Make sure to use the same params as before

```
aws cloudformation update-stack --stack-name [STACK_NAME] --template-body file://[TEMPLATE].yaml --parameters ParameterKey=[NAME],ParameterValue={VALUE}
```
