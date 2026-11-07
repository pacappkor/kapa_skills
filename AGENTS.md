# AGENTS.md — kapa_skills 작업 규칙

## 스킬을 사용할 때 (의뢰 처리)

1. `appraisal-practice-standards/00-practice-standards-start/SKILL.md` 를 먼저 읽고, 작업 유형에 맞는 작업 절차 스킬(workflows/)을 따른다. 평가 수행이면 workflow-appraisal 4단계 형식으로 기록을 남긴다.
2. 목록의 `SKILL.md` 를 읽는다. 결론이나 인용이 필요한 부분은 반드시 같은 폴더의 `source.md`(원문)로 확인한다.
3. 근거는 실무기준 표기로 단다. 형식은 `[조항코드-항-호]` 다.
   - 예: `[610-1.5.2.1-①]`, `[810-5.6.2-②-1]`
   - 항(①②…)과 호(1. 2. …)를 원문 순서대로 붙인다.
4. 추측하지 않는다. 의뢰서에 없는 사실은 "의뢰인 확인 필요"로 남긴다.
   원문에 없는 수치·비율·기간은 만들지 않는다. 관계법규 내용은 "실무기준 밖"으로 표시한다.
5. 규범력의 차이를 구분한다. "하여야 한다"는 의무, "할 수 있다"는 재량이다.
   다른 장과의 관계도 구분한다. "적용"은 그대로 적용, "준용"은 성질에 맞게 적용이다.

## 스킬을 고칠 때

- **`source.md` 는 직접 고치지 않는다.** `tools/split_standard.py` 가 원문에서 생성한다.
  원문 텍스트를 바로잡아야 하면 `tools/fetch_standard.py` 의 변환 로직이나 `split_standard.py` 의 `IMAGE_TEXT` 를 고친 뒤 다시 생성한다.
- `SKILL.md` 의 `<!-- BEGIN GENERATED:x -->` ~ `<!-- END GENERATED:x -->` 블록은 자동 생성이므로 손대지 않는다.
  사람이 쓰는 부분은 `description`, `## 언제 읽나`, `## 핵심 내용`, `## 적용 시 확인사항` 이다.
- description 은 한 줄로 쓴다. 실무기준 조항과 다루는 대상을 사실대로 적는다(140자 이하).
  트리거 문구("~할 때 반드시 사용")나 키워드 나열은 넣지 않는다.
- 새 스킬을 만들 때:
  - 폴더 이름을 `name` 과 같게 한다.
  - 이름은 `<층>-<주제>` 로 짓는다(foundation-·asset-·overlay-·workflow-). 내용 스킬은 원문 절과 1:1 로 두고 `tools/split_standard.py` 의 배정표에 등록한다.
  - 스킬 폴더 안에 또 다른 스킬을 두지 않는다(leaf rule).
  - workflow-appraisal/facets.md 조회표에 추가한다(validate.py 가 누락을 잡는다).
- 새 컬렉션(예: 감정평가에 관한 규칙, 토지보상법 시행규칙)은 저장소 최상위에 별도 폴더로 만든다.
  같은 원칙(짧은 입구 + workflows + 내용 스킬 + 원문 `source.md`)을 따르고, 기존 컬렉션과의 관계를 입구에 적는다. 스킬 이름이 다른 컬렉션과 겹치지 않게 한다.

## 검증 (커밋 전 필수)

```sh
python -I tools/split_standard.py --check   # 원문 배정·생성 블록 최신 여부
python -I tools/validate.py                 # 구조·링크·입구/workflows 범위 (errors: 0)
```

## 저장소 운영

- 변경은 `CHANGELOG.md` 의 `[Unreleased]` 에 기록한다. 버전 규칙과 릴리스·실무기준 개정 반영 절차는 `docs/RELEASING.md` 에 있다.
  실무기준 개정은 MINOR, 정정은 PATCH, 스킬 경로·이름 변경은 호환성 깨짐이다.

- 기본 브랜치 `main` 에 직접 커밋하지 않는다. 작업 브랜치를 만들고 PR 로 반영한다.
- 저장소는 비공개(private)로 유지한다.
- 토큰과 인증정보를 커밋, 로그, PR 본문에 남기지 않는다.
- 이슈 라벨:
  - 원문 대조 필요: `source-check`
  - 요약 검토: `summary-review`
  - 라우팅 개선: `routing`
  - 실무기준 개정 반영: `standard-update`

## 라이선스

저장소는 GPL-3.0-only 다([LICENSE](LICENSE), [NOTICE.md](NOTICE.md)).
- 새 코드 파일에는 `SPDX-License-Identifier: GPL-3.0-only` 를 단다.
- GPL 과 호환되지 않는 조건의 외부 자료(교재, 유료 해설 등)는 넣지 않는다.
- 원문 고시는 저작권 보호 대상이 아니다. 다만 출처(고시 번호·국가법령정보센터 URL)는 항상 밝힌다.
