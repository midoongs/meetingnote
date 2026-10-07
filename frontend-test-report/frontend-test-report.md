# 프론트엔드 테스트 보고서

## 1. 개요

| 항목 | 내용 |
|---|---|
| 일시 | 2026-10-07 |
| 대상 | MeetingNote 프론트엔드 (`http://127.0.0.1:8000/`, 백엔드가 같은 오리진에서 제공) |
| 도구 | Playwright (Chromium) |
| 화면 크기 | 데스크톱 1280×800, 모바일 360×740 |
| 데이터 | 실제 SQLite DB(빈 상태에서 시작), 실제 Gemini 호출 (`gemini-3.1-flash-lite`) |
| 테스트 파일 | 한국어 합성 음성 wav(`backend/tests/fixtures/meeting_sample.wav`), mp4(가짜), 26MB mp3(가짜) |
| 정리 | 테스트로 만든 회의록은 모두 삭제해 DB 를 빈 상태로 되돌림 |

## 2. 결과 요약

**33개 케이스 모두 통과.** 기능 결함은 없고, 경미한 개선점 1건(수정 완료)과 참고 사항 2건이 있다 (5장).

| 영역 | 케이스 수 |
|---|---|
| 목록 | 6 |
| 넣기 | 6 |
| 상세 | 6 |
| 할 일 | 1 |
| 테마 | 5 |
| 유지 | 1 |
| 이동 | 1 |
| 보안 | 1 |
| 모바일 360 | 6 |

## 3. 테스트 케이스

| ID | 영역 | 테스트 내용 | 기대 결과 | 실제 결과 | 판정 | 캡처 |
|---|---|---|---|---|---|---|
| T01 | 목록 | 첫 화면(회의록 0건) | 빈 목록 안내 문구 표시 | "조건에 맞는 회의록이 없습니다." 표시 | 통과 | [T01](screenshots/T01-list-empty.png) |
| T02 | 넣기 | 넣기 화면 진입 | 빈 폼, 일시는 현재 시각 기본값 | 빈 폼, 일시에 현재 시각이 들어 있음 | 통과 | [T02](screenshots/T02-new-empty.png) |
| T03 | 넣기 | 필수값 비우고 정리하기 (제목/본문/일시/공백 제목/파일 없이 받아쓰기) | 항목별 검증 문구, 서버 호출 없음 | 5종 문구 모두 정상 ("제목을 입력하세요." 등) | 통과 | [T03](screenshots/T03-new-validation.png) |
| T04 | 넣기 | mp4 파일로 받아쓰기 | mp3·wav만 가능하다는 안내 | "mp3, wav 파일만 올릴 수 있습니다." | 통과 | [T04](screenshots/T04-upload-mp4-rejected.png) |
| T05 | 넣기 | wav 업로드 후 받아쓰기 (실제 Gemini) | 본문칸에 받아쓴 원문 채움 | 원문과 일치하게 본문이 채워짐 | 통과 | [T05a](screenshots/T05a-upload-done.png), [T05b](screenshots/T05b-transcribed-form-filled.png) |
| T06 | 넣기 | 정리하기 (실제 Gemini) | 진행 표시 → 요약/결정사항/할 일 세 칸, 폼 비움 | 버튼 비활성+"정리하는 중…" → 세 칸 표시, 폼 비워짐, 입력한 로컬 10:00이 목록에 "오전 10:00"로 되돌아와 표시됨(T07) | 통과 | [T06a](screenshots/T06a-saving-in-progress.png), [T06b](screenshots/T06b-saved-three-parts.png) |
| T07 | 목록 | 카드 목록 (회의록 3건) | 최신순, 제목·일시·참석자·요약 첫 줄 | 최신순 3건, 2열 카드 | 통과 | [T07](screenshots/T07-list-cards.png) |
| T08 | 목록 | 참석자 검색 "박과장" (본문에만 이름이 있는 회의 포함) | 참석자에 있는 2건만 | 2건 (본문만 일치한 회의는 제외) | 통과 | [T08](screenshots/T08-search-attendee.png) |
| T09 | 목록 | 제목 검색 "디자인" | 해당 1건 | 1건 | 통과 | [T09](screenshots/T09-search-title.png) |
| T10 | 목록 | 없는 검색어 | 빈 결과 안내 | "조건에 맞는 회의록이 없습니다." | 통과 | [T10](screenshots/T10-search-no-result.png) |
| T11 | 목록 | 날짜 범위 2026-03-09 ~ 2026-03-16 (양끝 포함) | 범위 안 2건, 3/23 회의 제외 | 2건 (로컬 3/16 17:00 회의 포함) | 통과 | [T11](screenshots/T11-search-date-range.png) |
| T12 | 상세 | 카드 클릭 | 가운데 겹침 창, 세 갈래 표시 | 상세 창 열림, 세 칸 표시 | 통과 | [T12](screenshots/T12-modal-open.png) |
| T13 | 상세 | "받아쓴 본문 보기" 펼침 | 기본 접힘, 클릭 시 원문 표시 | 접힘 상태에서 펼치면 원문 표시 | 통과 | [T13](screenshots/T13-modal-body-expanded.png) |
| T14 | 상세 | 제목 수정 (PUT) | 창 제목 즉시 갱신, 목록 갱신, 나머지 내용 유지 | 제목 갱신, "제목을 수정했습니다." | 통과 | [T14](screenshots/T14-modal-title-edited.png) |
| T15 | 상세 | 삭제 2단계 (1회 클릭 → "정말 삭제" → 2회 클릭) | 1회는 지워지지 않음, 2회에 삭제 후 창 닫힘·목록 갱신 | 1회: 버튼이 "정말 삭제"로 바뀌고 안내 문구 변경, 2회: 삭제되고 목록에서 사라짐 | 통과 | [T15a](screenshots/T15a-delete-confirm-step.png), [T15b](screenshots/T15b-after-delete-list.png) |
| T16 | 할 일 | 할 일 표 | 내용/담당자/기한/회의 열, 회의 날짜 오래된 순, 회의 칸 클릭 시 상세 | 4열, 오래된 순, 기한은 말한 그대로 표시 | 통과 | [T16](screenshots/T16-todos.png) |
| T17 | 상세 | 구분 실패 표시 (세 갈래가 모두 빈 회의록) | 카드에 "구분 실패", 상세 창에 안내 박스 | 카드·상세 모두 표시 | 통과 | [T17a](screenshots/T17a-split-failed-card-and-xss.png), [T17b](screenshots/T17b-split-failed-modal.png) |
| T18 | 테마 | 다크 전환 버튼 클릭 → 목록 | 다크 적용, 글자 대비 유지 | 정상 | 통과 | [T18](screenshots/T18-dark-list.png) |
| T19 | 테마 | 다크 상세 창 | 다크 적용 | 정상 | 통과 | [T19](screenshots/T19-dark-modal.png) |
| T20 | 테마 | 다크 할 일 | 다크 적용 | 정상 | 통과 | [T20](screenshots/T20-dark-todos.png) |
| T21 | 테마 | 다크 넣기 | 다크 적용 | 정상 | 통과 | [T21](screenshots/T21-dark-new.png) |
| T22 | 유지 | 새로고침 (다크 상태, #list) | 테마·화면·데이터 유지 | 다크 유지(localStorage=dark), 같은 화면, 3건 그대로 | 통과 | [T22](screenshots/T22-after-reload-persisted.png) |
| T23 | 이동 | 탭 이동 후 브라우저 뒤로 가기 | 이전 화면(해시)으로 복귀 | #todos → 뒤로 가기 → 목록 화면·탭 활성 일치 | 통과 | - |
| T24 | 테마 | 저장값 없음 + 시스템 설정이 다크 | 초기값이 다크 | 다크로 시작 (storage 비어 있음) | 통과 | [T24](screenshots/T24-system-dark-initial.png) |
| T25 | 넣기 | 26MB mp3 선택 후 받아쓰기 | 25MB 초과 안내, 서버 호출 없음 | "파일은 25MB 이하여야 합니다." | 통과 | [T25](screenshots/T25-upload-over-25mb-rejected.png) |
| T26 | 보안 | 제목에 HTML 문자열 (`<img onerror=...><b>`) | 태그로 해석되지 않고 글자 그대로 | 글자 그대로 표시, 스크립트 미실행, img/b 요소 0개 | 통과 | [T17a](screenshots/T17a-split-failed-card-and-xss.png) |
| T27 | 상세 | Esc 키 (실제 키 입력) | 상세 창 닫힘 | 닫힘 | 통과 | - |
| M01 | 모바일 360 | 목록 (라이트) | 카드 1열, 가로 스크롤 없음 | 1열, 문서 가로 넘침 0 | 통과 | [M01](screenshots/M01-360-light-list.png) |
| M02 | 모바일 360 | 넣기 (라이트, 전체 화면) | 1열 폼, 가로 스크롤 없음 | 정상, 넘침 0 | 통과 | [M02](screenshots/M02-360-light-new.png) |
| M03 | 모바일 360 | 할 일 (라이트) | 표만 가로 스크롤, 문서 전체는 스크롤 없음 | 표 안에서만 스크롤, 문서 넘침 0 | 통과 | [M03](screenshots/M03-360-light-todos.png) |
| M04 | 모바일 360 | 상세 창 (라이트) | 화면 안에 들어오고 세 칸이 세로로 쌓임 | 정상, 세 칸 1열, 버튼 모두 화면 안 | 통과 | [M04](screenshots/M04-360-light-modal.png) |
| M05 | 모바일 360 | 목록 (다크) | 다크 + 360px 정상 | 정상 | 통과 | [M05](screenshots/M05-360-dark-list.png) |
| M06 | 모바일 360 | 상세 창 (다크) | 다크 + 360px 정상 | 정상 | 통과 | [M06](screenshots/M06-360-dark-modal.png) |

## 4. 화면 캡처

### T01-list-empty
T01 · 첫 화면(회의록 0건)

![T01-list-empty](screenshots/T01-list-empty.png)

### T02-new-empty
T02 · 넣기 화면 진입

![T02-new-empty](screenshots/T02-new-empty.png)

### T03-new-validation
T03 · 필수값 비우고 정리하기 (제목/본문/일시/공백 제목/파일 없이 받아쓰기)

![T03-new-validation](screenshots/T03-new-validation.png)

### T04-upload-mp4-rejected
T04 · mp4 파일로 받아쓰기

![T04-upload-mp4-rejected](screenshots/T04-upload-mp4-rejected.png)

### T05a-upload-done
T05 · wav 업로드 후 받아쓰기 (실제 Gemini)

![T05a-upload-done](screenshots/T05a-upload-done.png)

### T05b-transcribed-form-filled
T05 · wav 업로드 후 받아쓰기 (실제 Gemini)

![T05b-transcribed-form-filled](screenshots/T05b-transcribed-form-filled.png)

### T06a-saving-in-progress
T06 · 정리하기 (실제 Gemini)

![T06a-saving-in-progress](screenshots/T06a-saving-in-progress.png)

### T06b-saved-three-parts
T06 · 정리하기 (실제 Gemini)

![T06b-saved-three-parts](screenshots/T06b-saved-three-parts.png)

### T07-list-cards
T07 · 카드 목록 (회의록 3건)

![T07-list-cards](screenshots/T07-list-cards.png)

### T08-search-attendee
T08 · 참석자 검색 "박과장" (본문에만 이름이 있는 회의 포함)

![T08-search-attendee](screenshots/T08-search-attendee.png)

### T09-search-title
T09 · 제목 검색 "디자인"

![T09-search-title](screenshots/T09-search-title.png)

### T10-search-no-result
T10 · 없는 검색어

![T10-search-no-result](screenshots/T10-search-no-result.png)

### T11-search-date-range
T11 · 날짜 범위 2026-03-09 ~ 2026-03-16 (양끝 포함)

![T11-search-date-range](screenshots/T11-search-date-range.png)

### T12-modal-open
T12 · 카드 클릭

![T12-modal-open](screenshots/T12-modal-open.png)

### T13-modal-body-expanded
T13 · "받아쓴 본문 보기" 펼침

![T13-modal-body-expanded](screenshots/T13-modal-body-expanded.png)

### T14-modal-title-edited
T14 · 제목 수정 (PUT)

![T14-modal-title-edited](screenshots/T14-modal-title-edited.png)

### T15a-delete-confirm-step
T15 · 삭제 2단계 (1회 클릭 → "정말 삭제" → 2회 클릭)

![T15a-delete-confirm-step](screenshots/T15a-delete-confirm-step.png)

### T15b-after-delete-list
T15 · 삭제 2단계 (1회 클릭 → "정말 삭제" → 2회 클릭)

![T15b-after-delete-list](screenshots/T15b-after-delete-list.png)

### T16-todos
T16 · 할 일 표

![T16-todos](screenshots/T16-todos.png)

### T17a-split-failed-card-and-xss
T17 · 구분 실패 표시 (세 갈래가 모두 빈 회의록)

![T17a-split-failed-card-and-xss](screenshots/T17a-split-failed-card-and-xss.png)

### T17b-split-failed-modal
T17 · 구분 실패 표시 (세 갈래가 모두 빈 회의록)

![T17b-split-failed-modal](screenshots/T17b-split-failed-modal.png)

### T18-dark-list
T18 · 다크 전환 버튼 클릭 → 목록

![T18-dark-list](screenshots/T18-dark-list.png)

### T19-dark-modal
T19 · 다크 상세 창

![T19-dark-modal](screenshots/T19-dark-modal.png)

### T20-dark-todos
T20 · 다크 할 일

![T20-dark-todos](screenshots/T20-dark-todos.png)

### T21-dark-new
T21 · 다크 넣기

![T21-dark-new](screenshots/T21-dark-new.png)

### T22-after-reload-persisted
T22 · 새로고침 (다크 상태, #list)

![T22-after-reload-persisted](screenshots/T22-after-reload-persisted.png)

### T24-system-dark-initial
T24 · 저장값 없음 + 시스템 설정이 다크

![T24-system-dark-initial](screenshots/T24-system-dark-initial.png)

### T25-upload-over-25mb-rejected
T25 · 26MB mp3 선택 후 받아쓰기

![T25-upload-over-25mb-rejected](screenshots/T25-upload-over-25mb-rejected.png)

### T17a-split-failed-card-and-xss
T26 · 제목에 HTML 문자열 (`<img onerror=...><b>`)

![T17a-split-failed-card-and-xss](screenshots/T17a-split-failed-card-and-xss.png)

### M01-360-light-list
M01 · 목록 (라이트)

![M01-360-light-list](screenshots/M01-360-light-list.png)

### M02-360-light-new
M02 · 넣기 (라이트, 전체 화면)

![M02-360-light-new](screenshots/M02-360-light-new.png)

### M03-360-light-todos
M03 · 할 일 (라이트)

![M03-360-light-todos](screenshots/M03-360-light-todos.png)

### M04-360-light-modal
M04 · 상세 창 (라이트)

![M04-360-light-modal](screenshots/M04-360-light-modal.png)

### M05-360-dark-list
M05 · 목록 (다크)

![M05-360-dark-list](screenshots/M05-360-dark-list.png)

### M06-360-dark-modal
M06 · 상세 창 (다크)

![M06-360-dark-modal](screenshots/M06-360-dark-modal.png)

## 5. 발견 사항

- **F-01 (경미·수정 완료) 받아쓰기가 성공해도 이전 검증 문구가 남는다.**
  - T03 이후 "제목을 입력하세요." 상태에서 wav 받아쓰기를 하면, 받아쓰기는 완료되지만 정리하기 옆에 이전 문구가 그대로 남아 있다 (T05a).
  - 제안: 수정 완료: 받아쓰기를 시작하거나 입력이 바뀌면 저장 상태 문구를 지운다. 같은 재현 순서로 재확인했다 (검증 문구 → 받아쓰기 클릭 → 문구 사라짐, 검증 문구 → 입력 → 문구 사라짐).
- **F-02 (참고) 360px에서 할 일 표의 기한·회의 열이 가로 스크롤 뒤에 있다.**
  - 화면구성.pdf 4쪽의 "좁은 화면에서는 표만 가로 스크롤" 지침대로 동작하지만, 기한을 보려면 표를 옆으로 밀어야 한다 (M03).
  - 제안: 필요하면 모바일에서 행을 카드형으로 바꾸는 것을 검토.
- **F-03 (참고) 날짜 검색은 UTC 날짜 기준이다.**
  - 한국 시간 자정~오전 9시 회의는 전날 날짜로 검색된다. 02-specs.md 에 기준이 없어 UTC 로 구현했다 (이전 보고와 동일).
  - 제안: 기준을 로컬 날짜로 할지 정해서 02-specs.md 에 적을 것.

## 6. 확인하지 못한 범위

- Chromium(Playwright) 한 가지 브라우저만 사용했다. Firefox·Safari·실기기는 확인하지 않았다.
- 서버 중단·네트워크 끊김 상태의 화면 문구는 확인하지 않았다.
- Gemini 실패(구분 실패) 화면은 실제 실패를 일으키지 않고, 세 갈래를 빈 값으로 저장한 회의록으로 확인했다 (T17). 실제 실패 경로는 백엔드 pytest 에서 잘못된 키로 검증했다.
- 받아쓰기 "진행 중" 문구는 업로드가 수 초 안에 끝나 캡처하지 못했다 (T05a 는 완료 직후). 정리하기의 진행 상태는 T06a 로 확인했다.
- 상세 창 바깥 어두운 영역 클릭은 이전(3.4 단계) 테스트에서 이벤트로 확인했고, 이번에는 Esc 키만 실제 키 입력으로 확인했다.
- 25MB 이하 큰 파일(예: 20MB)의 화면 업로드는 확인하지 않았다 (백엔드에서 15.6MB 파일로 확인).
