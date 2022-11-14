from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import get_settings

settings = get_settings()


def test_get_files(session: Session, client: TestClient):
    response = client.request(
        "GET", "/files/", headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    response.json()
    assert response.status_code == 200


# def test_add_file(session: Session, client: TestClient):

#     logger.info(settings.PROJECT_DIR)
#     file = "postbox.png"
#     p = Path(settings.PROJECT_DIR / "tests" / file)
#     data = {"image": (p.open(mode="rb"), file)}
#     logger.info(p.is_file())
#     # assert 200 == 200
#     # file_name = "fake-text-stream.txt"
#     # data = {"file": (io.BytesIO(b"some initial text data"), file_name)}

#     # headers = {"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000", "Content-Type": "multipart/form-data"}
#     headers = {"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000", "Content-Type": "application/json"}
#     response = client.request("POST","/files/", data=data, headers=headers)
#     data = response.json()
#     logger.info(data)
#     assert response.status_code == 400
