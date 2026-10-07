# 04. Tasks

MVP 를 3개 Phase 로 진행한다. Phase 이름과 개수, Phase 별 단계 수는 고정이며 변경하지 않는다.

| Phase | 이름 | 단계 수 |
|---|---|---|
| 1 | 설계 | 10 |
| 2 | 백엔드 | 10 |
| 3 | 프론트 | 8 |

## 진행 규칙

- 순서대로만 진행한다. 병렬로 하지 않는다.
- 단계마다 검증 방법을 실행해 통과를 확인한 뒤에 완료 `[x]` 로 바꾼다.
- 완료 열은 `[ ]` 로 두고, 진행하면서 `[x]` 로 바꾼다.
- 'backend 진행해' = Phase 2 전체, 'frontend 진행해' = Phase 3 전체.

## 고정값

- 서버 포트: **8000**
- Phase 2 의존성은 아래 8개로 한정한다. 이 목록 밖은 추가하지 않는다.
  `fastapi`, `uvicorn`, `sqlalchemy`, `pytest`, `httpx`, `google-genai`, `python-multipart`, `python-dotenv`
- pytest 실행 시 `httpx2` 설치 권고가 떠도 무시한다.

## Phase 1 - 설계

CLAUDE.md + docs/ 6종 작성

| 단계 | 검증 방법 | 완료 |
|---|---|---|
| 1.1 CLAUDE.md 작성 (역할 / 기술 스택 / 시작 전 절차 / 절대규칙 6개) | 4개 섹션이 모두 있다 | [x] |
| 1.2 `.env` 작성 (`GEMINI_API_KEY`, `GEMINI_MODEL`) | 키 값은 비어 있고 모델명이 `gemini-3.1-flash-lite` 이다 | [x] |
| 1.3 `.gitignore` 작성 | `.env` 가 제외 목록에 있다 | [x] |
| 1.4 `docs/` 6개 파일 생성 | 이름과 순서가 CLAUDE.md 와 같다 | [x] |
| 1.5 `00-overview.md` 작성 | 매핑표·읽는 순서·화면·분리 원칙이 있다 | [x] |
| 1.6 `01-product.md` 작성 | 목표·페르소나·MVP 범위·성공 기준이 있다 | [x] |
| 1.7 `02-specs.md` 작성 | 모델 8필드, API 7개, 오류 코드가 있다 | [x] |
| 1.8 `03-design.md` 작성 | 표 8행과 의존성 추가 정책이 있다 | [x] |
| 1.9 `04-tasks.md` 작성 | Phase 3개, 단계 수 10/10/8 이다 | [x] |
| 1.10 `05-conventions.md` 작성 + 첫 커밋 | 파일에 내용이 있고 `git log` 에 첫 커밋이 보인다 | [x] |

## Phase 2 - 백엔드

`backend/` FastAPI > API 7개 + 받아쓰기 > Swagger 확인

| 단계 | 검증 방법 | 완료 |
|---|---|---|
| 2.1 `backend/` 폴더, 가상환경, 의존성 8개 설치 | `pip list` 에 8개만 있고 그 밖의 직접 추가는 없다 | [x] |
| 2.2 앱 뼈대, `.env` 읽기(`python-dotenv`), 포트 8000 | `uvicorn` 이 8000 에서 뜨고 키가 코드에 하드코딩되지 않았다 | [x] |
| 2.3 Meeting 모델 8필드 + DB 연결 | 테이블 DDL 에 `AUTOINCREMENT` 가 있고, 지운 id 가 재사용되지 않는다 (pytest) | [x] |
| 2.4 스키마(`extra="forbid"`)와 예외 핸들러 | 필수값 누락 400, 스펙 외 필드 422 (pytest) | [x] |
| 2.5 `POST /api/notes`(201), `GET /api/notes/{id}`(200/404) | 저장 후 단건 조회가 되고 없는 id 는 404 (pytest) | [x] |
| 2.6 `GET /api/notes` 목록과 검색 | `q`(제목·참석자), `from`·`to` 양끝 포함, 목록에 `body` 없음 (pytest) | [x] |
| 2.7 `PUT /api/notes/{id}`(200), `DELETE`(204) | 수정값이 반영되고 삭제 후 404 (pytest) | [x] |
| 2.8 `GET /api/todos` | 필드 `what`/`who`/`when`/`note_id`/`note_title`, 회의 날짜 오래된 순 (pytest) | [x] |
| 2.9 `POST /api/upload` + 세 갈래 구분 연결 (`google-genai`) | mp3·wav 외 415, 25MB 초과 413, 외부 실패 502, 구분 실패 시 빈 값으로 201 저장 (pytest, 실제 Gemini 호출, 호출 사이 1초 간격 - `05-conventions.md`) | [x] |
| 2.10 전체 pytest + Swagger 확인 | 전체 통과, `http://localhost:8000/docs` 에 7개 경로가 보인다 | [x] |

## Phase 3 - 프론트

`frontend/` HTML+JS+Tailwind > 화면 4종 > API 연결 > git push

화면 4종은 `02-specs.md` 화면 명세와 `03-design.md` 표대로 만든다.

| 단계 | 검증 방법 | 완료 |
|---|---|---|
| 3.1 `frontend/index.html`, `app.js` 2개 파일 뼈대 + 백엔드가 같은 오리진에서 제공 + 테마 토글 | `http://localhost:8000` 으로 열리고 `file://` 을 쓰지 않는다. 라이트/다크가 `localStorage` 에 저장되고 초기값은 시스템 설정이다 | [ ] |
| 3.2 목록 화면 (검색 포함) | 제목·참석자·날짜로 검색해 지난 회의가 나온다 | [ ] |
| 3.3 넣기 화면 (파일 업로드 / 메모 붙여넣기) | `datetime-local` 값이 UTC 로 전송되고, 저장하면 세 갈래로 구분되어 보인다 | [ ] |
| 3.4 상세 화면 (수정 / 삭제) | 수정·삭제가 되고, 구분 실패 시 화면에 표시된다 | [ ] |
| 3.5 할 일 화면 | 담당자·기한이 표시되고 기한은 회의에서 말한 문구 그대로다 | [ ] |
| 3.6 요소 이름 대조 | 화면의 요소 id 가 `03-design.md` 표와 모두 같다 | [ ] |
| 3.7 API 연결 최종 확인 | 새로고침해도 유지, 360px 에서 안 깨짐, 라이트/다크 모두 정상 | [ ] |
| 3.8 `git push` | 원격 저장소에 올라가고 `.env` 가 포함되지 않았다 | [ ] |
