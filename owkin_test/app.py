from flask import Flask, Blueprint, request

from .tasks import analyse_dockerfile

docker_analysis = Blueprint("docker_secured_run")

def create_app():
    app = Flask("Docker secured run")
    app.register_blueprint(docker_analysis)
    return app


# TODO: better error handling with exceptions mapped to return code.
# TODO: have a background running task that cleans task that no one has reclaim.
# TODO: use a marshaller like marshmallow for better return objects

@docker_analysis.route("/", methods=["POST"])
def post_dockerfile():
    if 'file' not in request.files:
        return 400, {"error": "file not in request"}
    dockerfile = request.files['file']
    
    # TODO: We should check for encoding of the file.
    task = analyse_dockerfile.delay(dockerfile.read(), prop)
    return 200, {"job_id": task.task_id}


@docker_analysis.route("/<string:job_id>", methods=["GET"])
def get_result(job_id):
    result = analyse_dockerfile.AsyncResult(job_id)

    # TODO: Return 404 is the job_id does not map to any celery task

    if not result.ready():
        return 200, {"status": "still running"}
    try:
        task_response = result.get(propagate=True)
    except Exception:
        # Return: add some info on what happened for the user to be able to correct it. Is it a temporary failure or because the dockerfile is wrong ?
        return 200, {"status": "failed"}

    if not task_response["success"]:
        return 200, {"status": "vulnerabilities found", "problems": task_response["error"]}

    return 200, {"status": "success", "perf": task_response["perf"]}
    

    


