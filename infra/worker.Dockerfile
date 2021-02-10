# A dockerfile that installs all dependencies and run the celery worker.
# This worker will have to communicate with the docker daemon, it should be based on docker-in-docker
FROM docker:dind
