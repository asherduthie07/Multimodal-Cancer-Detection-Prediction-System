import os
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test_oncofusion.db"
from services.api.oncofusion.main import app  # noqa: E402


def test_case_to_result_flow():
    with TestClient(app) as client:
        case = client.post("/demo/case").json()
        assert case["mode"] == "synthetic_demo"
        assert client.post(f"/cases/{case['id']}/validate").json()["valid"]
        alignment = client.post(f"/cases/{case['id']}/align/breast_mammo_detection_demo").json()
        assert alignment["valid"]
        job = client.post(f"/cases/{case['id']}/inference/breast_mammo_detection_demo").json()
        result = client.get(f"/jobs/{job['id']}/result").json()
        assert result["evaluation_status"] == "synthetic_demo"
        assert result["model_version"] == "synthetic-fixture-v1"
        assert client.get("/evaluations/breast_mammo_detection_demo").json()["sample_count"] == 0


def test_unsupported_upload_and_task():
    with TestClient(app) as client:
        client.post("/demo/case")
        response = client.post("/cases/DEMO-001/assets", files={"file": ("../../evil.exe", b"bad")})
        assert response.status_code == 415
        assert client.post("/cases/DEMO-001/inference/not-a-task").status_code == 404
