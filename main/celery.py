from django.conf import settings
import os
from celery import Celery
import tempfile
from ohapi import api
import requests
import zipfile
import logging
import json

import arrow

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oh_data_uploader.settings')


OH_BASE_URL = settings.OPENHUMANS_OH_BASE_URL

# Was used to generate reference genotypes in the previous file.

logger = logging.getLogger(__name__)

app = Celery('proj')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(CELERY_BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


def get_json(tf_in):
    print(tf_in.name)

    if tf_in.name.endswith('.zip'):
        zf = zipfile.ZipFile(tf_in)
        for f in zf.filelist:
            if f.filename.endswith('.json'):
                return zf.read(f)
    elif tf_in.name.endswith('.json'):
        return open(tf_in.name).read()
    else:
        return None


def process_file(dfile, access_token, member, metadata):
    infile_suffix = dfile['basename'].split(".")[-1]
    tf_in = tempfile.NamedTemporaryFile(suffix="."+infile_suffix)
    tf_in.write(requests.get(dfile['download_url']).content)
    tf_in.flush()
    tmp_directory = tempfile.mkdtemp()
    filename_base = 'Location History.json'
    location_data = get_json(tf_in)
    if location_data:
        location_json = json.loads(location_data)
        output_file = tmp_directory + '/' + filename_base
        with open(output_file, 'w') as raw_file:
            json.dump(location_json, raw_file)
        metadata = {
                    'description':
                    'Google Location History JSON',
                    'tags': ['google location history', 'gps'],
                    'creation_date': arrow.get().format(),
            }
        api.upload_aws(output_file, metadata,
                       access_token, base_url=OH_BASE_URL,
                       project_member_id=str(member['project_member_id']))
    else:
        api.message("Google Location History: A broken file was deleted",
                    "While processing your Google Location History file "
                    "we noticed that your file does not conform "
                    "to the expected specifications and it was "
                    "thus deleted. Please make sure you upload "
                    "the right file:\nWe expect the file to be a "
                    "single json file "
                    "or a .zip file as downloaded from Google Takeout."
                    " Please "
                    "do not alter the original file, as unexpected "
                    "additions can invalidate the file.",
                    access_token, base_url=OH_BASE_URL)
    api.delete_file(access_token,
                    str(member['project_member_id']),
                    file_id=str(dfile['id']),
                    base_url=OH_BASE_URL)


@app.task(bind=True)
def clean_uploaded_file(self, access_token, file_id):
    member = api.exchange_oauth2_member(access_token, base_url=OH_BASE_URL)
    for dfile in member['data']:
        if dfile['id'] == file_id:
            process_file(dfile, access_token, member, dfile['metadata'])
    pass
