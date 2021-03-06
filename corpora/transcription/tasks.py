from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from corpus.models import Recording, Sentence, Source
from transcription.models import \
    Transcription, TranscriptionSegment, AudioFileTranscription
from corpus.views.views import RecordingFileView
from django.contrib.sites.shortcuts import get_current_site

from corpora.utils.tmp_files import prepare_temporary_environment
from people.helpers import get_current_known_language_for_person

from transcription.utils import create_and_return_transcription_segments

from django.core.files import File
import wave
import contextlib
import os
import stat
import commands
import ast
import sys
import requests
import urllib2
import json
import uuid
from subprocess import Popen, PIPE
import time


from django.core.cache import cache

import logging
logger = logging.getLogger('corpora')


@shared_task
def launch_transcription_api():
    num_jobs = cache.get('TRANSCRIPTION_JOBS', 0)

    logger.debug('NUM_TRANSCRIPTION_JOBS: {0: <4f}'.format(num_jobs))

    '''
    Let's check jobs every minut, and maybe have a cooldown of 5 minutes
    so the initial get re4quests cause us to ensure that we're running a server,
    but after 5 minutes if there are no actual transcription jobs then we should
    just take the servers down
    '''

    logger.debug('LAUNCHING')
    return "DISABLED CHANGING OF AUTOSCALINGGROUP"

    import boto3
    import os
    os.environ['PROJECT_NAME']
    client = boto3.client(
        'autoscaling',
        aws_access_key_id=os.environ['AWS_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET'],
        region_name='ap-southeast-2')

    response = client.set_desired_capacity(
            AutoScalingGroupName='asg-corpora-production-deepspeech',
            DesiredCapacity=1,
            HonorCooldown=False,
        )


@shared_task
def launch_watcher():
    # Use beat to schedule this
    last_queue = cache.get('JOBS_PING', [])
    num_jobs = cache.get('TRANSCRIPTION_JOBS', 0)
    last_queue.insert(0, num_jobs)

    count = 0
    for i in range(len(last_queue)-1):
        if last_queue[i] - last_queue[i+1] == 0:
            count = count + 1

    if count == 3:
        num_jobs = 0

    last_queue = cache.set('JOBS_PING', last_queue)
    logger.debug('NUM_TRANSCRIPTION_JOBS: {0: <4f}'.format(num_jobs))

    if num_jobs <= 0:
        logger.debug('STOPPING')

        return "DISABLED CHANGING OF AUTOSCALINGGROUP"

        client = boto3.client(
            'autoscaling',
            aws_access_key_id=os.environ['AWS_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET'],
            region_name='ap-southeast-2')

        response = client.set_desired_capacity(
                AutoScalingGroupName='asg-corpora-production-deepspeech',
                DesiredCapacity=0,
                HonorCooldown=True,
            )
