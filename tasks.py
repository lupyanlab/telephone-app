#!/usr/bin/env python
from invoke import run, task
import boto3
from unipath import Path

bucket_name = 'telephone-app'

@task
def download_experiment(snapshot_name='words-in-transition'):
    """Take a snapshot of the data on the server and store it on S3."""
    cmd = 'ansible-playbook snapshot.yml -e snapshot_name={}'
    run(cmd.format(snapshot_name))

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    # download db and media files
    for key in Path(snapshot_name).listdir():
        with open(key, 'rb') as f:
            bucket.put_object(Body=f, Key=key)
