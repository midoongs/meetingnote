VALID = {"title": "기획 회의", "met_at": "2026-01-10T01:00:00Z", "body": "본문"}


def test_case_08_title_missing_is_400(client):
    payload = {k: v for k, v in VALID.items() if k != "title"}
    assert client.post("/api/notes", json=payload).status_code == 400


def test_case_09_met_at_bad_format_is_400(client):
    r = client.post("/api/notes", json={**VALID, "met_at": "내일 오후"})
    assert r.status_code == 400


def test_case_11_extra_field_is_422(client):
    r = client.post("/api/notes", json={**VALID, "unknown_field": 1})
    assert r.status_code == 422


def test_extra_field_cannot_set_summary(client):
    r = client.post("/api/notes", json={**VALID, "summary": "직접 입력"})
    assert r.status_code == 422


def test_body_and_met_at_missing_are_400(client):
    assert client.post("/api/notes", json={"title": "a", "met_at": VALID["met_at"]}).status_code == 400
    assert client.post("/api/notes", json={"title": "a", "body": "b"}).status_code == 400


def test_blank_title_and_too_long_title_are_400(client):
    assert client.post("/api/notes", json={**VALID, "title": "   "}).status_code == 400
    assert client.post("/api/notes", json={**VALID, "title": "가" * 201}).status_code == 400


def test_missing_plus_extra_is_400(client):
    payload = {"met_at": VALID["met_at"], "body": "b", "unknown_field": 1}
    assert client.post("/api/notes", json=payload).status_code == 400


def test_bad_date_query_is_400(client):
    assert client.get("/api/notes", params={"from": "2026/01/01"}).status_code == 400


def test_error_body_is_json_detail(client):
    r = client.post("/api/notes", json={})
    assert r.status_code == 400
    assert isinstance(r.json()["detail"], list)
