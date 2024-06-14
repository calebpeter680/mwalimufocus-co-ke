web: gunicorn eduresources.wsgi
worker: celery -A eduresources worker -l INFO
beat: celery -A eduresources beat --scheduler django_celery_beat.schedulers:DatabaseScheduler -l INFO
