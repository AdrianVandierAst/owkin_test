@pytest.fixture
def dockerfile_example(shared_datadir):
    dockerfile = shared_datadir / "example.Dockerfile"
    return dockerfile
