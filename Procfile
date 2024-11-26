web: daphne -b 0.0.0.0 -p $PORT eduresources.asgi:application
worker: celery -A eduresources worker -l INFO
beat: celery -A eduresources beat --scheduler django_celery_beat.schedulers:DatabaseScheduler -l INFO
