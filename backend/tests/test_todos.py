from datetime import datetime


def test_case_07_todos_fields_and_order(client, seed):
    new_id = seed(
        title="최근 회의",
        met_at=datetime(2026, 2, 1),
        todos="시안 제출 | 김민수 | 다음 주 금요일\n계약서 검토 | 미정 | 월말",
    )
    old_id = seed(title="오래된 회의", met_at=datetime(2026, 1, 1), todos="예산안 작성 | 이영희 | 이번 주")
    seed(title="할 일 없음", met_at=datetime(2026, 1, 15), todos="")

    r = client.get("/api/todos")
    assert r.status_code == 200
    items = r.json()
    assert items == [
        {"what": "예산안 작성", "who": "이영희", "when": "이번 주", "note_id": old_id, "note_title": "오래된 회의"},
        {"what": "시안 제출", "who": "김민수", "when": "다음 주 금요일", "note_id": new_id, "note_title": "최근 회의"},
        {"what": "계약서 검토", "who": "미정", "when": "월말", "note_id": new_id, "note_title": "최근 회의"},
    ]


def test_todos_keep_deadline_text_as_is(client, seed):
    seed(todos="발표 준비 | 박 | 다음 주 금요일까지")
    assert client.get("/api/todos").json()[0]["when"] == "다음 주 금요일까지"


def test_todo_line_with_missing_parts(client, seed):
    seed(todos="내용만 있는 줄")
    item = client.get("/api/todos").json()[0]
    assert (item["what"], item["who"], item["when"]) == ("내용만 있는 줄", "미정", "")
