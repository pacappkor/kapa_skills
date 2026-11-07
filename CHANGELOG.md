# 변경 이력 (CHANGELOG)

이 저장소의 모든 주요 변경을 기록한다.
- 형식: [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)
- 버전: [유의적 버전](https://semver.org/lang/ko/)
- 버전 규칙과 릴리스 절차: [docs/RELEASING.md](docs/RELEASING.md)

새 변경은 먼저 `[Unreleased]` 에 쌓는다. 릴리스할 때 버전 제목으로 옮긴다.
개정을 반영할 때는 `docs/RELEASING.md` 의 템플릿을 복사해 쓴다. 실무기준은 "개정 반영 항목 템플릿", 관계법령은 "관계법령 갱신 항목 템플릿"이다.

## [Unreleased]

### 추가
- `laws/` 관계법령 컬렉션 (국가법령정보센터 현행 법령, 2026-11-08 수집)
  - A층(법·시행령·시행규칙 전 조문 + 별표 + 주제별 요약):
    - 토지보상법 16주제
    - 감정평가법·감정평가에 관한 규칙 12주제
    - 부동산공시법 6주제
    - 국토계획법 19주제
    - 도시정비법 15주제
  - B층 `related-provisions`: 실무기준·토지보상법 시행규칙 제5장이 조문 번호로 인용한 다른 법령 38개 문서의 해당 조항 5주제
    - 인용 문맥표 포함
    - 개정 전 번호 인용(수산업법·외부감사법·항공법)은 현행 대응 조문을 함께 수록
  - 입구 `00-laws-start`, 갱신 절차는 저장소 규칙 `rules/` 로 분리(아래 "변경"), 저장소 입구 `00-kapa-start`
- 별표 가공본 `sources/laws/<컬렉션>/annex-md/` 55건(원본 PDF 120쪽)
  - 대상: 토지보상법 7, 감정평가법 시행령 4, 국토계획법 시행령·시행규칙 33, 도시정비법 시행령 8, 관련 조항 3(산림자원법 시행규칙 별표 3, 수산업법 시행령 별표 4·10)
  - 에이전트가 원본 PDF 의 모든 페이지 이미지를 보고 표·목록으로 가공했다. 수치·항목은 원문 그대로이고, 원문 오기는 `[원문 그대로]` 로 표시했다.
  - PDF 페이지 순서가 본문과 다른 별표(국토계획법 시행령 별표 16·17·19·20·24)는 항목 번호로 순서를 복원했다.
  - `source.md` 에 가공본과 원본 PDF·HWP 링크를 함께 싣는다.
  - `build_laws.py --check` 는 다음 경우를 오류로 알린다: 가공본 없음, 미검증, 원본 파일 번호(`pdf_flseq`)가 현행 별표와 다름(개정).
  - 관련 주제 요약을 가공본과 대조해 고치고, PDF 추출 주의 문구를 없앴다. 예: 국토계획법 건축제한 세부 요건, 수산업법 시행령 별표 10 어선 내용연수·잔존가치율, 구 별표 4 인용과의 대응.
- `tools/laws/annex_prep.py`: 별표 원본 PDF 를 페이지 이미지로 렌더링하고 가공 작업 목록 생성
- `tools/fetch_standard.py --check`: 국가법령정보센터의 현행 「감정평가 실무기준」 고시가 저장소 판본과 같은지 확인
- 도구 `tools/laws/`
  - `fetch_laws.py`: 수집. `--check` 로 최신 판본 비교
  - `diff_laws.py`: 조문 단위 변경 목록
  - `build_laws.py`: 생성. `--check`·`--status`·`--coverage` 로 조문 배정과 요약의 조문 인용 누락 검사
  - `draft_topics.py`: 배정표 초안
  - `lawindex.py`: 조문 → 스킬 색인
  - `image_text.json`: 본문 산식 이미지 전사
- C층 `laws/public-works-acts`
  - 범위: 토지보상법 별표의 공익사업 근거법 115개(A층 제외)
  - 내용: 토지보상법을 언급하는 조문 258개, 7개 분야 주제
  - 색인: 법률별 색인, 특례 색인(사업인정 의제·재결신청 기간·준용)
- 양방향 연결
  - `tools/graph.py` 가 모든 스킬에 "들어오는 연결"을 생성한다(조문 단위 표기, `docs/graph.json`)
  - 법령 간 절차 `laws/workflow-compensation-chain` 과 회귀 사례 `cases.md`
- 개정 전 번호 인용 대응표 `tools/laws/stale_citations.json`
- 실무기준 스킬의 "참조 관계"에 원문이 인용한 관계법령 조문 링크를 자동 생성. 연속 인용과 "같은 법"을 해석하고, 개정 전 번호는 현행 조문으로 연결한다
- `tools/fix_links.py`: 스킬 이름 기준 링크 재계산

### 변경
- 저장소 규칙을 `rules/` 의 두 스킬로 분리했다. `rules/` 에는 이 두 스킬만 둔다.
  - `skill-reading-rules`: 스킬을 읽고 답하는 규칙. 읽는 순서, 원문 확인, 인용 형식, 우선순위, 판본, 생성 블록·별표 가공본의 의미. 파일을 바꾸지 않는다.
  - `skill-update-maintenance`: 실무기준 또는 관계법령 개정에 따른 갱신 절차. 어느 쪽 지시든 둘 다 확인하고, 실무기준·법령 트랙을 거쳐 재생성·검증·기록한다.
  - 입구 스킬·AGENTS·CLAUDE 에 흩어져 있던 읽기 규칙은 `skill-reading-rules` 로 모았다.
  - `docs/RELEASING.md` 의 실무기준 개정 절차는 `skill-update-maintenance` 로 옮겼다. RELEASING 에는 버전·기록 규칙만 남겼다.
  - `tools/validate.py` 가 분리를 검사한다. 다음 경우는 오류다.
    - 갱신 스킬 밖의 스킬 폴더 파일에 도구 명령·갱신 절차가 있음
    - 읽기 규칙에 갱신 작업 용어가 있음
    - 갱신 스킬에 읽기 규칙 절이 있음
    - 입구·AGENTS·CLAUDE 가 읽기 규칙을 가리키지 않음
  - 생성 블록과 `source.md` 머리말에서 도구 경로 언급을 뺐다.
- 실무기준만 전제하던 운영 규칙·도구를 관계법령 개정까지 다루도록 고쳤다.
  - 이슈 템플릿:
    - "실무기준 개정 반영"(`standard-update`)과 "관계법령 개정 반영"(`law-update`, 새 라벨)으로 나눴다.
    - 둘 다 1단계에서 양쪽 확인을 요구한다.
    - "내용 오류 보고"(`source-check`) 템플릿을 추가했다.
  - PR 템플릿: 관계법령 개정 반영 항목, `build_laws.py --check` 확인을 추가했다.
  - `docs/RELEASING.md`:
    - 버전 규칙에 관계법령 내용 변경(MINOR)과 개정 표시만 변경(PATCH)을 넣었다.
    - "관계법령 갱신 항목 템플릿"을 추가했다.
  - AGENTS·README·NOTICE: 원문 생성기·이름 규칙·새 컬렉션 위치·버전·라벨·면책을 실무기준과 관계법령 모두에 맞게 고쳤다. 상주 입구를 `00-kapa-start` 로 바꿨다.
  - `tools/fetch_standard.py`: 인자가 없으면 고정 판본 대신 저장소 판본(`split_standard.SEQ`)을 받는다.
- `workflow-appraisal` 우선순위 ①(관계법규)과 지장물·농업손실·이주대책 등 실무기준에 절이 없는 보상 항목을 토지보상법 스킬로 연결
- 생성기들의 링크를 최단 상대경로로 통일(`fix_links.py` 와 충돌 방지)
- `validate.py`: 법령 컬렉션 검사 포함

<!--
### 근거 고시          ← 실무기준 개정 반영일 때만
### 실무기준 개정 반영  ← 조항별 표 (docs/RELEASING.md 템플릿)
### 관계법령 갱신      ← 관계법령 개정 반영일 때만: 판본 변화 + diff 표 + 행별 처리
### 추가
### 변경
### 정정
### 삭제
### 호환성 깨짐        ← 스킬 경로·이름 변경/삭제 등 @skills 주소가 바뀌는 변경
-->

## [v0.0.0] - 2026-11-07

최초 릴리스. PR #1.

### 근거 고시
- 「감정평가 실무기준」 국토교통부고시 제2023-522호 (2023. 9. 13. 일부개정, 시행 2023. 9. 13.)
- 국가법령정보센터 admRulSeq=2100000229230

### 추가
- `appraisal-practice-standards` 컬렉션
  - 입구: `00-practice-standards-start`
  - 작업 절차 4개: `workflow-appraisal`, `lookup-clause`, `workflow-report-review`, `workflow-engagement-check`
  - 내용 스킬 41개: `foundations/` 5, `assets/` 27, `overlays/` 9. 원문 [100]~[900]·부칙 전 조항을 빠짐없이 배정했다
- 내용 스킬 구성
  - `SKILL.md`: 요약, 적용 시 확인사항, 함께 읽을 스킬
  - 자동 생성 블록: 조항 목차, 참조 관계
  - `source.md`: 원문 전문
- 찾기 도구
  - 용어·조항 색인 `terms.md`: 원문 정의·조항 제목·검증된 별칭 31개
  - 조회표 `facets.md`
  - 라우팅 사례 `cases.md`: 23개
- 원문 산식 이미지 3개의 전사와 원본 gif: [810-6.2.7], [820-5.2.2.1], [840-5.2-③]
- 도구
  - `tools/fetch_standard.py`: 원문 수집
  - `tools/split_standard.py`: 조항 분할·생성, `--check`
  - `tools/fix_links.py`: 링크 재계산
  - `tools/validate.py`: 구조 검증
- 문서
  - README, AGENTS, CLAUDE
  - NOTICE: GPL-3.0-only, 원문은 「저작권법」 제7조 비보호 저작물
  - `docs/ROUTING.md`: 진입 방식 비교, 폴더 구조 근거, 독립 에이전트 검토 결과

[Unreleased]: https://github.com/pacappkor/kapa_skills/compare/v0.0.0...HEAD
[v0.0.0]: https://github.com/pacappkor/kapa_skills/releases/tag/v0.0.0
