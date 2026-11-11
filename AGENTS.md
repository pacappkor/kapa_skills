# AGENTS.md — kapa_skills 작업 규칙

## 규칙의 두 갈래 (서로 섞지 않는다)

| 작업 | 따를 스킬 | 할 수 있는 일 |
|---|---|---|
| 스킬을 읽고 답하기 (의뢰 처리, 조문·조항 질의, 평가서 검토) | [skill-reading-rules](rules/skill-reading-rules/SKILL.md) | 읽기만 한다. 파일을 고치지 않고, 어긋난 내용은 보고한다 |
| 실무기준·관계법령 개정에 따른 기존 스킬 갱신 (사용자가 명시적으로 지시했을 때만) | [skill-update-maintenance](rules/skill-update-maintenance/SKILL.md) | 1–6단계 전체를 수행하고 PR 로 반영한다 |

- 읽기 규칙(원문 확인, 인용 형식, 우선순위, 판본)은 `skill-reading-rules` 에만 둔다. 입구 스킬은 그곳을 가리킨다.
- 갱신 명령·절차는 `skill-update-maintenance` 에만 둔다. 다른 스킬 폴더의 파일에는 도구 명령을 쓰지 않는다.
- `tools/validate.py` 가 이 분리를 검사한다.
- `rules/` 에는 두 스킬만 둔다. 규칙을 바꿀 때는 해당 스킬 하나만 고치고 CHANGELOG 에 기록한다.

## 스킬을 고칠 때

- **`source.md` 는 직접 고치지 않는다.** 생성기가 원문에서 만든다.
  - 실무기준: `tools/split_standard.py`. 원문 텍스트를 바로잡으려면 `tools/fetch_standard.py` 의 변환 로직이나 `split_standard.py` 의 `IMAGE_TEXT` 를 고친다.
  - 관계법령: `tools/laws/build_laws.py`. `tools/laws/fetch_laws.py`·`tools/laws/image_text.json`·별표 가공본(`sources/laws/<컬렉션>/annex-md/`)을 고친다.
- `SKILL.md` 의 `<!-- BEGIN GENERATED:x -->` – `<!-- END GENERATED:x -->` 블록은 자동 생성이므로 손대지 않는다.
  사람이 쓰는 부분은 `description`, `## 언제 읽나`, `## 핵심 내용`, `## 적용 시 확인사항` 이다.
- description 은 한 줄로 쓴다. 근거(실무기준 조항 또는 법령·조문)와 다루는 대상을 사실대로 적는다(140자 이하).
  트리거 문구("…할 때 반드시 사용")나 키워드 나열은 넣지 않는다.
- 새 스킬을 만들 때:
  - 폴더 이름을 `name` 과 같게 한다.
  - 스킬 폴더 안에 또 다른 스킬을 두지 않는다(leaf rule).
  - 실무기준 스킬:
    - 이름은 `<층>-<주제>` 로 짓는다(foundation-·asset-·overlay-·workflow-).
    - 원문 절과 1:1 로 두고 `tools/split_standard.py` 의 배정표에 등록한다.
    - workflow-appraisal/facets.md 조회표에 추가한다(validate.py 가 누락을 잡는다).
  - 법령 주제 스킬:
    - 이름은 `<법령 약칭>-<주제>` 로 짓는다(예: lca-·nlp-). 입구 이름은 `00-<약칭>-start` 다.
    - `tools/laws/topics/<컬렉션>.json` 에 조문 범위를 배정한다. 입구 주제 지도는 자동 생성된다.
- 새 법령 컬렉션은 `laws/` 아래에 만든다.
  - `tools/laws/catalog.json` 에 등록하고 층(A·B·C)을 정한다.
  - 입구 + 주제 스킬 + 원문 `source.md` 구조를 따른다.
  - 스킬 이름이 다른 컬렉션과 겹치지 않게 한다.
- 실무기준이 아닌 새 기준·고시 컬렉션은 저장소 최상위에 별도 폴더로 만든다. 같은 원칙(짧은 입구 + 내용 스킬 + 원문 `source.md`)을 따르고, 기존 컬렉션과의 관계를 입구에 적는다.

## 관계법령 컬렉션 (laws/)

- 원문·생성 블록·배정표·별표 가공본·요약의 작성 규칙과 갱신 순서는 [skill-update-maintenance](rules/skill-update-maintenance/SKILL.md) 에 있다.
- 하위 에이전트에게 요약이나 별표 가공을 맡길 때:
  - 완료 조건을 준다. 요약은 "`build_laws.py --coverage <컬렉션>` 에 MISSING·TODO 없음", 별표는 "`--check` 에 해당 별표 오류 없음"이다.
  - 오케스트레이터는 `--status` 로 직접 확인한다.
  - 일부만 하고 멈추면 남은 범위를 명시해 재개하거나 다른 에이전트에게 넘긴다.

## 검증 (커밋 전 필수)

```sh
python -I tools/split_standard.py --check   # 원문 배정·생성 블록 최신 여부
python -I tools/laws/build_laws.py --check   # 법령: 조문 배정·생성물·요약 인용 누락
python -I tools/laws/build_index.py --check  # 현행 조문·실무기준 조항 식별자 색인
python -I tools/validate.py                 # 구조·링크·입구/workflows 범위·법령 검사 포함 (errors: 0)
```

## 저장소 운영

- 기본 검토 소유자는 `.github/CODEOWNERS` 에 지정한다.

- 변경은 `CHANGELOG.md` 의 `[Unreleased]` 에 기록한다. 버전·기록 규칙은 `docs/RELEASING.md`, 개정 반영 절차는 `rules/skill-update-maintenance` 에 있다.
  - MINOR: 실무기준 개정, 관계법령 내용 변경
  - PATCH: 정정, 법령 개정 표시만 변경
  - 호환성 깨짐: 스킬 경로·이름 변경

- 기본 브랜치 `main` 에 직접 커밋하지 않는다. 작업 브랜치를 만들고 PR 로 반영한다.
- 2026-11-11 정책에 따라 GitHub 저장소는 공개할 수 있다. HF 시장 데이터셋 `pacappkor/kapa-market-data`는 공개이며, HF staging 데이터셋은 비공개로 유지한다.
- 공개 허용은 외부 자료의 재배포 제한을 해제하지 않는다. 라이선스와 개인정보·비밀정보 보호 규칙을 지킨다.
- 토큰과 인증정보는 어떤 저장소에도 두지 않으며, 커밋, 로그, PR 본문에 남기지 않는다.
- 이슈 라벨:
  - 원문 대조 필요: `source-check`
  - 요약 검토: `summary-review`
  - 라우팅 개선: `routing`
  - 실무기준 개정 반영: `standard-update`
  - 관계법령 개정 반영: `law-update`

## 라이선스

저장소는 GPL-3.0-only 다([LICENSE](LICENSE), [NOTICE.md](NOTICE.md)).
- 새 코드 파일에는 `SPDX-License-Identifier: GPL-3.0-only` 를 단다.
- GPL 과 호환되지 않는 조건의 외부 자료(교재, 유료 해설 등)는 넣지 않는다.
- 원문 고시는 저작권 보호 대상이 아니다. 다만 출처(고시 번호·국가법령정보센터 URL)는 항상 밝힌다.
