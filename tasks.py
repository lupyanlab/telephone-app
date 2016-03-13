#!/usr/bin/env python
from invoke import run, task
import boto3
from boto.mturk.connection import MTurkConnection, MTurkRequestError
from unipath import Path
import pandas as pd


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
    run('cd telephone && rm -f telephone.sqlite3 && python manage.py migrate')
    run('cd telephone && python manage.py loaddata ../words-in-transition/words-in-transition.json')
    run('cd words-in-transition && unzip words-in-transition.zip && mv webapps/telephone/media ../')
    run('rm -rf words-in-transition/webapps/')


# MTurk
@task
def mturk():
    """Downloads the assignments from MTurk.

    Data contains completion codes and MTurk user ids that can be used to
    label the subj_id data.
    """
    mturk = MTurk()
    survey_hit_title = "Listen to a sound and pick the sound it's closest to."
    survey_results = mturk.get_hit_results(survey_hit_title)
    survey_results.to_csv('mturk_survey_results.csv', index=False)


class MTurk:
    def __init__(self):
        self._mturk = MTurkConnection()

    def get_hit_info(self, title):
        results = []
        for hit in self._mturk.get_all_hits():
            num_responses = int(hit.NumberOfAssignmentsCompleted)
            if hit.Title == title and num_responses > 0:
                info = (hit.HITId, num_responses)
                results.append(info)
        return results

    def get_hit_results(self, title):
        hit_info = self.get_hit_info(title)
        hit_results = []
        for hit_id, num_responses in hit_info:
            assignments = self._mturk.get_assignments(hit_id, page_size=num_responses)
            assert len(assignments) == num_responses
            hit_results.append(assignments_to_frame(assignments))
        results = pd.concat(hit_results)
        return results


def assignments_to_frame(assignments):
    # Create an iterable copy of each boto.mturk.connection.Assignment
    # so that pandas can create a frame for all assignment data.
    results = pd.DataFrame.from_records([a.__dict__ for a in assignments])

    def unfold_answers(assignment):
        answers = assignment.answers[0]  # answers are [[buried]] for some reason
        for answer in answers:
            assignment[answer.qid] = answer.fields[0]
        del assignment['answers']
        return assignment

    return results.apply(unfold_answers, axis=1)
