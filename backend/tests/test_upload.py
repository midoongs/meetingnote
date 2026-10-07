from pathlib import Path

SAMPLE_WAV = Path(__file__).parent / "fixtures" / "meeting_sample.wav"


def test_case_12_mp4_is_415(client):
    r = client.post("/api/upload", files={"file": ("rec.mp4", b"x" * 100, "video/mp4")})
    assert r.status_code == 415


def test_case_13_30mb_is_413(client):
    big = b"\0" * (30 * 1024 * 1024)
    r = client.post("/api/upload", files={"file": ("rec.mp3", big, "audio/mpeg")})
    assert r.status_code == 413


def test_no_extension_is_415(client):
    assert client.post("/api/upload", files={"file": ("rec", b"x", "audio/mpeg")}).status_code == 415


def test_upload_wav_is_transcribed_by_real_gemini(client, gemini_gap):
    """실제 음성을 실제 Gemini 로 받아쓴다."""
    r = client.post("/api/upload", files={"file": ("meeting.wav", SAMPLE_WAV.read_bytes(), "audio/wav")})
    assert r.status_code == 200
    text = r.json()["text"]
    assert len(text) > 20
    assert "출시" in text or "회의" in text


def test_transcribed_text_can_be_saved_and_split(client, gemini_gap):
    """받아쓰기 결과를 그대로 본문으로 저장하면 세 갈래로 구분된다."""
    text = client.post(
        "/api/upload", files={"file": ("meeting.wav", SAMPLE_WAV.read_bytes(), "audio/wav")}
    ).json()["text"]
    r = client.post(
        "/api/notes", json={"title": "녹취 회의", "met_at": "2026-01-10T01:00:00Z", "body": text}
    )
    assert r.status_code == 201
    assert r.json()["summary"].strip()


def test_upload_gemini_failure_is_502(client, broken_gemini):
    r = client.post("/api/upload", files={"file": ("meeting.wav", SAMPLE_WAV.read_bytes(), "audio/wav")})
    assert r.status_code == 502
