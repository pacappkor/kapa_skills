# laws — 감정평가 관계법령

국가법령정보센터(law.go.kr) 현행 법령을 주제별 스킬로 나눈 컬렉션 모음이다.
- 에이전트 입구: [00-laws-start](00-laws-start/SKILL.md)
- 읽기 규칙: [skill-reading-rules](../rules/skill-reading-rules/SKILL.md) (스킬 사용, 파일 변경 없음)
- 갱신 절차: [skill-update-maintenance](../rules/skill-update-maintenance/SKILL.md) (실무기준·법령 개정 반영 지시 때만)

이 README 는 사람용이다.

## 범위를 정한 기준

| 층 | 기준 | 수록 범위 | 법령 |
|---|---|---|---|
| A | 감정평가·손실보상의 근거가 되는 법률. 「감정평가 실무기준」이 장(章) 단위로 의존하는 법령 | 법·시행령·시행규칙 **전 조문**과 별표(PDF 텍스트 추출), 별지 서식 목록. 주제별 요약 | 토지보상법, 감정평가법·감정평가에 관한 규칙, 부동산공시법, 국토계획법, 도시정비법 |
| B | 「감정평가 실무기준」과 토지보상법 시행규칙 제5장(손실보상평가의 기준)이 **조문 번호까지** 인용한 다른 법령 | 인용된 조항과 별표만. 인용 번호가 개정 전 번호면 현행 대응 조문도 함께 수록. 요약 포함 | 건축법, 수산업법, 광업법, 산림자원법, 농지법, 통계법 등 38개 문서 (`00-rel-start` 인용 문맥표) |
| C | 토지보상법 별표(제4조제8호 관련)에 열거된 **공익사업 근거법** 가운데 A층에 없는 115개 | 본문에서 토지보상법을 언급하는 조문만 기계적으로 선택(`tools/laws/handoff_scan.py`). 수용 권한·사업인정 의제·재결신청 기간 특례·준용·보상 특례. 법률별 색인 포함 | 도로법, 도시개발법, 택지개발촉진법, 하천법, 공공주택 특별법, 산업입지법 등 (`00-pwa-start`) |
| (미수록) | 법령 이름만 인용하고 조문을 특정하지 않은 법률 | 수록하지 않는다. `00-rel-start` 에 목록을 둔다 | 공장 및 광업재단 저당법, 집합건물법, 산지관리법, 상법 등 |

B층 법령의 전문이 필요해지면 `tools/laws/catalog.json` 에서 A층 컬렉션으로 올리고 배정표를 만든다. 수집·생성·검증 도구는 그대로 쓴다.

## 구조

```text
laws/
├── 00-laws-start/              입구
├── land-compensation-act/      00-lca-start + lca-* 16개
├── appraisal-act/              00-apa-start + apa-* 12개
├── price-disclosure-act/       00-pda-start + pda-* 6개
├── national-land-planning-act/ 00-nlp-start + nlp-* 19개
├── urban-redevelopment-act/    00-ura-start + ura-* 15개
├── related-provisions/         00-rel-start + rel-* 5개
├── public-works-acts/          00-pwa-start + pwa-* 7개 (C층)
└── workflow-compensation-chain/ 근거법 → 토지보상법 → 실무기준 (역방향 포함) 절차
```

**양방향 연결**: 모든 스킬에 두 블록이 자동 생성된다.
- 나가는 연결("참조 관계"): `build_laws.py`·`split_standard.py`
- 들어오는 연결: `tools/graph.py`

어느 법령에서 출발해도 그 법령을 인용·준용하는 쪽과, 그 법령이 인용·준용하는 쪽으로 모두 이동할 수 있다.

- **주제 스킬 하나**: 법의 장·절 하나(필요하면 더 잘게 나눔)와, 그 위임을 받은 시행령·시행규칙 조문이다.
  배정표는 `tools/laws/topics/<컬렉션>.json` 에 있다. 모든 조문이 정확히 한 주제에 들어간다(생성기가 검사).
- **스킬 폴더 구성**:
  - `SKILL.md`: 요약, 확인사항
  - 생성 블록: 근거 판본, 맡은 조문, 참조 관계
  - `source.md`: 원문
- **요약 완전성**: 각 주제 요약은 맡은 조문을 빠짐없이 인용해야 한다. 하나라도 빠지면 `build_laws.py --check` 가 실패한다.

## 도구

| 명령 | 하는 일 |
|---|---|
| `python -I tools/laws/fetch_laws.py [컬렉션…]` | 현행 법령 수집 → `sources/laws/` (조문 JSON, 부칙, 별표 텍스트, manifest) |
| `python -I tools/laws/fetch_laws.py --check` | 수집하지 않고 현행 판본과 manifest 비교(바뀐 법령 보고) |
| `python -I tools/laws/fetch_versions.py [컬렉션…] [--check]` | 연혁 목록 수집·manifest 법령ID 보강 / 미시행 개정과 목록 변화 확인(쓰기 없음) |
| `python -I tools/laws/fetch_version.py <컬렉션> <level> (<lsiSeq> [--ef YYYY-MM-DD] 또는 --at YYYY-MM-DD)` | 필요한 과거 시행 판본 본문·부칙 저장. 중복 lsiSeq 는 시행일 필수([판본 식별](../docs/LAW-VERSIONS.md)) |
| `python -I tools/laws/build_index.py [--check]` | `docs/law-index.json` 법령·현행 조문·실무기준 조항 색인 생성 / 최신 검사 |
| `python -I tools/laws/diff_laws.py [--markdown]` | 기준 커밋 대비 조문 단위 변경 목록(신설·삭제·내용 변경 등과 영향 스킬) |
| `python -I tools/laws/build_laws.py` | 배정표대로 `source.md`·생성 블록·입구 지도 생성 |
| `python -I tools/laws/build_laws.py --check` / `--status` / `--coverage` | 배정·생성물·요약 인용 누락 검사 / 주제별 진행 상태 / 누락 조문 |
| `python -I tools/laws/handoff_scan.py [--fetch]` | C층: 토지보상법 별표의 근거법을 받아 토지보상법 언급 조문을 고른다(`handoff_selection.json`) |
| `python -I tools/graph.py [--check] [--json]` | 저장소 전체 인용 그래프 → 각 스킬의 "들어오는 연결" 블록, `docs/graph.json` |
| `python -I tools/laws/annex_prep.py <작업폴더> [컬렉션…]` | 별표 가공 준비: 수록 별표의 원본 PDF 를 페이지 이미지로 렌더링하고 작업 목록 생성. 가공본은 `sources/laws/<컬렉션>/annex-md/` (원본 PDF 번호 기록, 개정 시 검사가 알림) |
| `python -I tools/laws/draft_topics.py <컬렉션>` | 새 컬렉션의 배정표 초안(법의 장·절 기준, 하위 법령은 인용·장 이름으로 연결) |

## 출처와 이용 조건

법령은 「저작권법」 제7조에 따라 보호받지 않는 저작물이다. 국가법령정보센터를 출처로 밝힌다.
이 저장소의 구성·요약·도구는 GPL-3.0-only 다(저장소 `NOTICE.md`).
