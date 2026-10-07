from conftest import MEETING_BODY


def test_case_01_create_returns_201_with_three_parts(client, gemini_gap):
    """실제 Gemini 를 불러 세 갈래로 나뉘는지 본다."""
    r = client.post(
        "/api/notes",
        json={
            "title": "출시 일정 회의",
            "met_at": "2026-01-10T01:00:00Z",
            "attendees": "김민수, 이영희",
            "body": MEETING_BODY,
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["id"] >= 1
    assert data["summary"].strip()
    assert data["decisions"].strip()
    todo_lines = data["todos"].splitlines()
    assert todo_lines, "할 일이 나와야 한다"
    assert all(line.count("|") == 2 for line in todo_lines)
    # 저장되어 다시 읽힌다 (새로고침해도 유지)
    again = client.get(f"/api/notes/{data['id']}").json()
    assert again["summary"] == data["summary"]
    assert again["body"] == MEETING_BODY


def test_case_03_get_one_has_body(client, seed):
    note_id = seed(body="원문 본문")
    r = client.get(f"/api/notes/{note_id}")
    assert r.status_code == 200
    assert r.json()["body"] == "원문 본문"


def test_case_10_unknown_id_is_404(client):
    assert client.get("/api/notes/9999").status_code == 404


def test_met_at_with_offset_is_stored_as_utc(client, seed, broken_gemini):
    """+09:00 로 보내면 UTC 로 바뀌어 Z 로 돌아온다 (구분이 실패해도 201)."""
    r = client.post(
        "/api/notes",
        json={"title": "시차", "met_at": "2026-01-10T10:00:00+09:00", "body": "본문"},
    )
    assert r.status_code == 201
    assert r.json()["met_at"] == "2026-01-10T01:00:00Z"


def test_classify_failure_still_saves_with_empty_parts(client, broken_gemini):
    r = client.post(
        "/api/notes",
        json={"title": "실패", "met_at": "2026-01-10T01:00:00Z", "body": MEETING_BODY},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["summary"] == data["decisions"] == data["todos"] == ""
    assert client.get(f"/api/notes/{data['id']}").status_code == 200
