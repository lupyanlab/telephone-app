#!/usr/bin/env python
import math
from functools import partial

from invoke import run, task
import boto3
from boto.mturk.connection import MTurkConnection, MTurkRequestError
from unipath import Path
import pandas as pd


EXPERIMENT = 'words-in-transition'


@task
def download():
    """Take a snapshot of the data on the server and store it locally."""
    cmd = 'ansible-playbook snapshot.yml -e snapshot_name={}'
    run(cmd.format(EXPERIMENT))


@task
def mturk(hit_info_csv='mturk_hit_info.csv'):
    """Downloads the assignments from MTurk.

    Data contains completion codes and MTurk user ids that can be used to
    label the subj_id data.

        hit_info_records = [
            ("norm_seed", "Listen to sounds and pick the odd one out."),
            ("imitations", "Play the childhood game of telephone on the web."),
            ("imitation_matches", "Listen to a sound and pick the sound it's closest to."),
            ("transcriptions", "Transcribe a sound effect into a new English word."),
            ("transcription_matches", "Match words to sound effects."),
        ]

    """
    hit_info = pd.read_csv(hit_info_csv)
    mturk = MTurk()
    assignments = [mturk.get_assignments(hit_id) for hit_id in hit_info.HITId]
    all_assignments = pd.merge(hit_info, pd.concat(assignments))
    all_assignments.to_csv(Path(EXPERIMENT, 'mturk_subjects.csv'), index=False)


@task
def push(bucket_name='words-in-transition'):
    """Push a snapshot to S3."""
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    for key in Path(EXPERIMENT).listdir():
        with open(key, 'rb') as f:
            bucket.put_object(Body=f, Key=key)


@task
def load():
    """Load a snapshot in the telephone submodule."""
    run('cd telephone && rm -f telephone.sqlite3 && python manage.py migrate')
    run('cd telephone && python manage.py loaddata ../words-in-transition/words-in-transition.json')
    run('rm -rf media')
    run('cd words-in-transition && unzip words-in-transition.zip && mv webapps/telephone/media ../')
    run('rm -rf words-in-transition/webapps/')


class MTurk:
    ASSIGNMENTS_PER_PAGE = 100

    def __init__(self):
        self._mturk = MTurkConnection()

    def get_hit(self, hit_id):
        try:
            hit = self._mturk.get_hit(hit_id)
        except MTurkRequestError as error:
            raise LookupError(error.message)
        else:
            return hit[0]

    def get_assignments(self, hit_id):
        hit = self.get_hit(hit_id)
        max_responses = int(hit.MaxAssignments)
        pages = int(max_responses/self.ASSIGNMENTS_PER_PAGE) + 1
        assignments = [self.get_assignments_page(hit_id, page_number=n)
                       for n in range(1, pages+1)]
        return pd.concat(assignments)

    def get_assignments_page(self, hit_id, page_number):
        assignments = self._mturk.get_assignments(
            hit_id=hit_id,
            page_size=self.ASSIGNMENTS_PER_PAGE,
            page_number=page_number,
        )
        return assignments_to_frame(assignments)

def assignments_to_frame(assignments):
    # Create an iterable copy of each boto.mturk.connection.Assignment
    # so that pandas can create a frame for all assignment data.
    results = pd.DataFrame.from_records([a.__dict__ for a in assignments])

    def unfold_answers(assignment):
        try:
            answers = assignment.answers[0]  # answers are [[buried]] for some reason
        except IndexError:
            answers = []

        for answer in answers:
            assignment[answer.qid] = answer.fields[0]
        del assignment['answers']
        return assignment

    return results.apply(unfold_answers, axis=1)
