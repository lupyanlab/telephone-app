#!/usr/bin/env python
from invoke import run, task
import boto3
from unipath import Path


@task
def download():
    """Take a snapshot of the data on the server and store it locally."""
    cmd = 'ansible-playbook snapshot.yml -e snapshot_name={}'
    run(cmd.format('words-in-transition'))

@task
def push(bucket_name='telephone-app'):
    """Push a snapshot to S3."""
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    # download db and media files
    for key in Path('words-in-transition').listdir():
        with open(key, 'rb') as f:
            bucket.put_object(Body=f, Key=key)

@task
def load():
    """Load a snapshot in the telephone submodule."""
    run('cd telephone && python manage.py loaddata ../words-in-transition/words-in-transition.json')
    run('cd words-in-transition && unzip words-in-transition.zip && mv webapps/telephone/media ../media/')
    run('rm -rf webapps/')

