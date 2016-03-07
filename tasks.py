#!/usr/bin/env python
from invoke import run, task
import boto3

bucket_name = 'telephone-app'

@task
def download_experiment(output_dir):
    run('ansible-playbook snapshot.yml')
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    # download db and media files
    
