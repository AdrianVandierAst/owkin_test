from celery import Celery

# TODO: should be put in a configuration file
REDIS_URI = "redis://localhost:6379"


def make_celery():
    return Celery(__name__, backend=REDIS_URI, broker=REDIS_URI)


celery = make_celery()
