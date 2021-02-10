import requests
from tenacity import retry, retry_if_exception_type


class StillRunning(Exception):
    pass


def test_basic_dockerfile(dockerfile_example):
    response = requests.post("/", files={"file": dockerfile_example})
    assert response.status_code == 200
    job_id = response.json()["job_id"]

    # We retry during 30s (a random chosen duration for the moment).
    @retry(
        stop=stop_after_delay(30),
        retry=retry_if_exception_type(StillRunning),
        reraise=True,
    )
    def get_response():
        response = requests.get(f"/{job_id}")
        assert response.status_code == 200
        response_json = response.json()
        if response_json["status"] == "still running":
            raise StillRunning()
        assert response_json["status"] == "success", response_json
        assert response_json["perf"] == "0.99", response_json

    get_response()
