#!/bin/sh
awslocal s3 mb s3://fashion-datasets
awslocal s3 mb s3://fashion-tasks
awslocal s3 sync /tmp/localstack/dataset s3://fashion-datasets/dataset-v1