release: python manage.py migrate
web: gunicorn oh_data_uploader.wsgi --log-file=-
worker: celery worker -A main --concurrency=1
