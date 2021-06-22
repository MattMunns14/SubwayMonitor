#!/usr/bin/env bash

set -o allexport
source .env
set +o allexport

sam build
sam deploy --template-file template.yml \
                             --stack-name SubwayMonitor \
                             --s3-bucket ${S3_BUCKET} \
                             --s3-prefix SubwayMonitor \
                             --parameter-overrides \
                             ApiKey=${API_KEY} \
                             --capabilities CAPABILITY_NAMED_IAM \
                             --role-arn ${ROLE_ARN} \
                              --region ${AWS_REGION}