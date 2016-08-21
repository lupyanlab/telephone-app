#!/usr/bin/env python
import math

from invoke import run, task
import boto3
from boto.mturk.connection import MTurkConnection, MTurkRequestError
from unipath import Path
import pandas as pd


EXPERIMENT = 'words-in-transition'
MTURK_ASSIGNMENTS = Path(EXPERIMENT, 'mturk_assignments')

if not MTURK_ASSIGNMENTS.exists():
    MTURK_ASSIGNMENTS.mkdir()


@task
def download():
    """Take a snapshot of the data on the server and store it locally."""
    cmd = 'ansible-playbook snapshot.yml -e snapshot_name={}'
    run(cmd.format(EXPERIMENT))


@task
def mturk(experiment, hit_title):
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
    mturk = MTurk()
    survey_results = mturk.get_hit_results(hit_title)
    survey_results['experiment'] = experiment
    survey_results['comments'] = survey_results.comments.str.encode('utf-8')

    hit_dir = Path(MTURK_ASSIGNMENTS, experiment)
    if not hit_dir.exists():
        hit_dir.mkdir()
    survey_results.to_csv(Path(hit_dir, 'mturk_assignments.csv'), index=False)


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
        self._hits = None

    @property
    def hits(self):
        if not self._hits:
            self._hits = list(self._mturk.get_all_hits())
        return self._hits

    def get_hit_info(self, title):
        return [(hit.HITId, int(hit.MaxAssignments)) for hit in self.hits
                                                     if hit.Title == title]

    def get_hit_results(self, title):
        hit_info = self.get_hit_info(title)
        hit_results = []
        for hit_id, num_responses in hit_info:
            pages = int(num_responses/self.ASSIGNMENTS_PER_PAGE) + 1
            for page_number in range(1, pages+1):
                assignments = self._mturk.get_assignments(
                    hit_id,
                    page_size=self.ASSIGNMENTS_PER_PAGE,
                    page_number=page_number,
                )
                hit_results.append(assignments_to_frame(assignments))
        results = pd.concat(hit_results)
        results['hit_title'] = title
        return results

    def get_all_hit_results(self, titles):
        hit_results = [self.get_hit_results(t) for t in titles]
        return pd.concat(hit_results)


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
