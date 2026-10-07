from datetime import datetime


def test_case_02_list_has_no_body(client, seed):
    seed(body="긴 원문")
    r = client.get("/api/notes")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert "body" not in items[0]


def test_case_06_search_matches_title_and_attendees_only(client, seed):
    seed(title="기획 회의", attendees="김민수")
    seed(title="주간 보고", attendees="박기획, 이영희")
    seed(title="디자인 리뷰", attendees="최디자", body="기획 이야기가 본문에만 있다")
    r = client.get("/api/notes", params={"q": "기획"})
    assert r.status_code == 200
    assert sorted(i["title"] for i in r.json()) == ["기획 회의", "주간 보고"]


def test_search_treats_percent_literally(client, seed):
    seed(title="100% 달성 회의")
    seed(title="일반 회의")
    r = client.get("/api/notes", params={"q": "%"})
    assert [i["title"] for i in r.json()] == ["100% 달성 회의"]


def test_date_range_is_inclusive_at_both_ends(client, seed):
    seed(title="전날", met_at=datetime(2026, 1, 9, 23, 59, 59))
    seed(title="시작일", met_at=datetime(2026, 1, 10, 0, 0, 0))
    seed(title="종료일 끝", met_at=datetime(2026, 1, 12, 23, 59, 59))
    seed(title="다음날", met_at=datetime(2026, 1, 13, 0, 0, 0))
    r = client.get("/api/notes", params={"from": "2026-01-10", "to": "2026-01-12"})
    assert sorted(i["title"] for i in r.json()) == ["시작일", "종료일 끝"]


def test_list_is_newest_first(client, seed):
    seed(title="오래된", met_at=datetime(2026, 1, 1))
    seed(title="최근", met_at=datetime(2026, 2, 1))
    titles = [i["title"] for i in client.get("/api/notes").json()]
    assert titles == ["최근", "오래된"]
