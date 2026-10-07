FULL = {
    "title": "수정된 제목",
    "met_at": "2026-02-01T05:00:00Z",
    "attendees": "가, 나",
    "body": "수정된 본문",
    "summary": "수정 요약",
    "decisions": "수정 결정",
    "todos": "일 | 담당 | 내일",
}


def test_case_04_put_all_fields(client, seed):
    note_id = seed()
    r = client.put(f"/api/notes/{note_id}", json=FULL)
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "수정된 제목"
    assert data["met_at"] == "2026-02-01T05:00:00Z"
    assert data["summary"] == "수정 요약"
    assert client.get(f"/api/notes/{note_id}").json()["todos"] == "일 | 담당 | 내일"


def test_put_without_optional_fields_keeps_them(client, seed):
    note_id = seed(summary="기존 요약", todos="기존 | 담당 | 내일")
    required = {k: FULL[k] for k in ("title", "met_at", "body")}
    r = client.put(f"/api/notes/{note_id}", json=required)
    assert r.status_code == 200
    assert r.json()["summary"] == "기존 요약"
    assert r.json()["todos"] == "기존 | 담당 | 내일"


def test_put_validation_and_404(client, seed):
    note_id = seed()
    assert client.put(f"/api/notes/{note_id}", json={**FULL, "title": ""}).status_code == 400
    assert client.put(f"/api/notes/{note_id}", json={**FULL, "x": 1}).status_code == 422
    assert client.put("/api/notes/9999", json=FULL).status_code == 404


def test_case_05_delete_then_404(client, seed):
    note_id = seed()
    r = client.delete(f"/api/notes/{note_id}")
    assert r.status_code == 204
    assert r.content == b""
    assert client.get(f"/api/notes/{note_id}").status_code == 404
    assert client.delete(f"/api/notes/{note_id}").status_code == 404
