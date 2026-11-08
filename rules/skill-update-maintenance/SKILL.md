---
name: skill-update-maintenance
description: 감정평가 실무기준이나 관계법령이 개정됐을 때 기존 스킬을 갱신하는 절차(현행본 비교, 원문·배정·별표·요약 갱신, 검증, CHANGELOG·PR). 스킬을 바꾸는 작업만 다룬다.
---

# skill-update-maintenance — 개정에 따른 스킬 갱신 절차

## 적용 범위

- **언제 쓰나**: 사용자가 스킬 갱신을 명시적으로 지시했을 때만 쓴다. 지시는 다음 중 어느 것이든 될 수 있다.
  - "실무기준이 개정됐다, 반영하라"
  - "관계법령(토지보상법·국토계획법 등)이 개정됐다, 반영하라"
  - "최신 법령·기준과 비교해 업데이트하라"
- **1단계는 언제나 둘 다 확인한다.** 지시가 한쪽만 말해도 실무기준과 관계법령을 함께 확인한다.
  - 두 컬렉션은 서로 인용한다. 실무기준 → 법령 링크, 법령 → 실무기준 들어오는 연결.
  - 그래서 한쪽이 바뀌면 다른 쪽 스킬도 영향을 받는다.
- **범위 밖**: 스킬을 읽고 답하는 규칙. [skill-reading-rules](../skill-reading-rules/SKILL.md) 에 있고, 여기서 반복하지 않는다.
- **진행 방식**: 1단계부터 6단계까지 처음부터 끝까지 따른다.
  - 중간 단계에서 멈추지 않는다.
  - 변경을 일부만 보고 판단하지 않는다. 도구가 내놓은 변경 목록 전체를 처리한다.

저장소: `pacappkor/kapa_skills`

## 1. 확인 (무엇이 바뀌었나)

```sh
python -I tools/fetch_standard.py --check     # 「감정평가 실무기준」 현행 고시 = 저장소 판본?
python -I tools/laws/fetch_laws.py --check    # 관계법령 전부 = manifest 판본?
python -I tools/laws/fetch_versions.py --check # 연혁 변화·공포됨/미시행 개정 확인; 부칙·경과조치도 확인
```

| 결과 | 다음 |
|---|---|
| 실무기준·현행 법령·연혁 모두 같음 | 바뀐 것이 없다. 확인 일자와 세 결과를 사용자에게 보고하고 끝낸다(파일 변경 없음) |
| 실무기준·현행 법령은 같고 연혁만 바뀜 | 2 → 3-L(연혁 목록 갱신, 새 미시행 개정의 부칙·경과조치 검토) → 4 → 5 → 6. 현행 본문이 같아도 종료하지 않는다 |
| 실무기준만 바뀜 | 2 → 3-S → 4 → 5 → 6 |
| 법령만 바뀜 | 2 → 3-L → 4 → 5 → 6 |
| 둘 다 바뀜 | 2 → 3-S → 3-L → 4 → 5 → 6 (실무기준 먼저: 법령 쪽 B층 배정이 실무기준 인용에 따라 달라진다) |

## 2. 작업 브랜치

- `update/YYYYMMDD` 브랜치를 만든다. main 에 직접 커밋하지 않는다.
- 실무기준과 법령이 함께 바뀌었으면 한 브랜치·한 PR 로 처리한다.

## 3-S. 「감정평가 실무기준」 개정

1. `fetch_standard.py --check` 가 출력한 새 `admRulSeq` 로 원문을 받는다.
   - `admRulId` 는 화면(`admRulInfoP.do?admRulSeq=…`)에서 확인한다.
   - 명령: `python -I tools/fetch_standard.py <admRulSeq> <admRulId>`
2. `tools/split_standard.py` 를 고친다.
   - `SEQ`·`NOTICE`: 새 고시
   - `SKILLS`: 조항이 신설·삭제되면 배정을 고친다.
   - `IMAGE_TEXT`: 산식 이미지가 바뀌면 고친다.
   - `ALIASES`: 별칭 대상 조항이 바뀌면 고친다. 생성기가 원문 대조로 알려 준다.
3. `python -I tools/split_standard.py` 를 실행한다.
   - 사람이 쓴 문서의 고시 번호도 모두 고친다. `grep -rn "<이전 고시 번호>" --include=*.md .` 로 찾는다.
   - 대상 예: 실무기준 입구, `appraisal-practice-standards/README.md`, `README.md`, `NOTICE.md`
4. 바뀐 조항 목록을 만든다: `git diff --word-diff -- 'appraisal-practice-standards/**/source.md'`
   - 이 diff 의 **모든 조항**이 처리 대상이다. 조항마다 6단계 표에 결과를 적는다.
5. 실무기준이 인용하는 법령 조문이 바뀌었는지 본다.
   - 새로 인용하는 조문이 B층에 없으면 `tools/laws/topics/related-provisions.json` 에 배정한다.
   - 개정 전 번호 인용이 현행 번호로 고쳐졌으면 `tools/laws/stale_citations.json` 에서 그 항목을 지운다.
6. 각 조항에 대해 그 스킬의 요약·확인사항을 고친다. 영향을 확인할 곳은 다음과 같다.
   - `workflow-appraisal` 우선순위·단계표와 `facets.md`
   - `cases.md`
   - 그 조항을 인용하는 법령 스킬(`## 들어오는 연결`)

## 3-L. 관계법령 개정

1. 바뀐 컬렉션만 다시 받는다: `python -I tools/laws/fetch_laws.py <컬렉션id …>`
   - 연혁도 재수집한다: `python -I tools/laws/fetch_versions.py <컬렉션id …>`
   - 조문 배정 반영 후 색인을 재생성한다: `python -I tools/laws/build_index.py`
   - 과거 본문이 필요하면 `python -I tools/laws/fetch_version.py <컬렉션> <level> --at YYYY-MM-DD` 로 해당 시행 판본만 저장한다.
2. 조문 단위 변경 목록을 만든다: `python -I tools/laws/diff_laws.py --markdown`
   - 결과는 스크래치 경로에 저장한다.
   - 이 표의 **모든 행**이 처리 대상이다. 행마다 6단계 표에 결과를 적는다.
   - 행 종류: 신설 / 조문 없어짐 / 삭제 / 제목 변경 / 내용 변경 / 개정 표시만 변경 / 별표·서식 변경
3. `python -I tools/laws/build_laws.py --check` 오류를 모두 해소한다.
   - `미배정`: 신설 조문이다. `tools/laws/topics/<컬렉션>.json` 에서 알맞은 주제 범위에 넣는다. 주제가 없으면 새 주제를 만든다.
   - `별표 주제 미정`: 배정표의 `annex`(A층) 또는 `annex_no`(B층)에 지정한다.
   - `별표 가공본 없음` / `현행 별표와 다름`: 그 별표만 다시 가공한다(아래 작성 규칙).
     - 준비: `python -I tools/laws/annex_prep.py <스크래치 폴더> <컬렉션>`
   - B층: 실무기준·토지보상법 시행규칙이 인용하는 조문 번호가 바뀌었으면 배정표를 고친다. 차이는 `stale_citations.json` 과 `00-rel-start` 에 적는다.
   - C층: 토지보상법 별표나 근거법이 바뀌었으면 다음을 한다.
     - `python -I tools/laws/handoff_scan.py --fetch` 를 실행한다.
     - 바뀐 `handoff_selection.json` 을 `tools/laws/topics/public-works-acts.json` 에 반영한다.
4. 변경 목록의 각 조문을 처리한다. 주제 스킬 `source.md` 의 해당 조문을 읽고 요약·확인사항을 고친다.
   - 신설: 요약에 넣는다. 빠지면 `--coverage` 가 알려 준다.
   - 내용 변경: 기존 요약을 새 원문과 문장 단위로 대조한다. 수치·기간·의무/재량 표현을 특히 본다.
   - 삭제·조문 없어짐: 요약에서 지운다. 그 조문을 근거로 쓰는 다른 스킬을 `grep -rn "<법령 약칭> 제N조"` 로 찾아 함께 고친다.
   - 개정 표시만 변경: 요약은 고치지 않는다. 표에 "요약 영향 없음"이라고 적는다.
   - 실무기준 스킬(특히 overlays/compensation, overlay-urban-redevelopment, asset-*)이 바뀐 조문을 전제로 설명하는지도 확인한다.

## 4. 재생성 (순서 고정)

```sh
python -I tools/laws/build_laws.py      # 법령 source.md·생성 블록
python -I tools/split_standard.py       # 실무기준 source.md·생성 블록(법령 링크 포함)
python -I tools/graph.py --json         # 모든 스킬의 들어오는 연결, docs/graph.json
python -I tools/fix_links.py            # 스킬 링크 경로
python -I tools/laws/build_index.py     # 법령·조문·실무기준 조항 식별자 색인
```

## 작성 규칙 (3단계에서 지킬 것)

- 원문(`source.md`)과 `<!-- BEGIN GENERATED:… -->` 블록은 생성물이다. 직접 고치지 않는다.
  - 원문을 바로잡을 때: 실무기준은 `fetch_standard.py`·`split_standard.py` 의 `IMAGE_TEXT`, 법령은 `fetch_laws.py`·`tools/laws/image_text.json` 을 고친다.
- 사람이 쓰는 부분은 description, `## 언제 읽나`, `## 핵심 내용`, `## 적용 시 확인사항` 이다.
  - 법령 주제 스킬: 맡은 조문(삭제 조문 제외)을 모두 `법 제70조`·`영 제38조의2`·`규칙 제22조` 형식으로 인용한다.
  - 실무기준 스킬: 근거를 `[610-1.5.2.1-①]` 형식으로 단다.
  - 원문에 없는 수치·기간을 쓰지 않는다. 의무/재량("하여야 한다"/"할 수 있다") 표현은 원문대로 둔다.
- 별표 가공본(`sources/laws/<컬렉션>/annex-md/<level>-<id>.md`):
  - 원본 PDF 의 모든 페이지 이미지를 보고 만든다.
  - PDF 페이지 순서가 본문 순서와 다른 경우가 있다(예: 국토계획법 시행령 별표 16·17·19·20·24). 항목 번호의 이어짐으로 순서를 복원한다.
  - frontmatter 는 `annex`, `pdf_flseq`, `status: verified-against-pdf` 다.
  - 표는 마크다운 표로, 건축물 목록은 번호를 살린 중첩 목록으로 옮긴다.
  - 수치·항목·비고는 원문 그대로 옮긴다. 읽을 수 없는 곳은 `[판독 불가]` 로 표시한다.
  - 그 별표를 설명하는 주제 요약도 대조해 고친다.
- 스킬 폴더의 파일(SKILL.md 등)에는 도구 명령이나 갱신 절차를 쓰지 않는다. 그런 내용은 이 스킬에만 둔다(`tools/validate.py` 가 검사).
- 하위 에이전트에게 나눌 때는 두 가지를 반드시 준다.
  - 맡을 변경 행 전체
  - 완료 조건: 요약은 `--coverage` 에 MISSING 없음, 별표는 `--check` 에 해당 오류 없음
- 오케스트레이터는 `build_laws.py --status` 로 직접 확인한다. 일부만 하고 멈춘 에이전트는 남은 범위를 명시해 재개한다.

## 5. 검증

```sh
python -I tools/fetch_standard.py --check      # 실무기준: 같은 현행 고시
python -I tools/laws/fetch_laws.py --check     # 법령: 같은 현행 판본
python -I tools/laws/fetch_versions.py --check # 연혁·미시행 개정 재확인, 부칙 검토 결과 기록
python -I tools/laws/build_index.py --check    # 식별자 색인 최신
python -I tools/split_standard.py --check      # 실무기준 배정·생성 블록 최신
python -I tools/laws/build_laws.py --check     # 법령 배정·생성물·요약 인용·별표 가공본
python -I tools/laws/build_laws.py --status    # 모든 주제 OK
python -I tools/graph.py --check               # 들어오는 연결 최신
python -I tools/validate.py                    # 저장소 전체 errors 0 (읽기/갱신 규칙 분리 포함)
```

## 6. 기록과 반영

1. `CHANGELOG.md` 의 `[Unreleased]` 에 기록한다.
   - 실무기준 개정: `docs/RELEASING.md` 의 "개정 반영 항목 템플릿"을 쓴다. 근거 고시와 조항별 처리표를 적는다.
   - 관계법령 개정: `docs/RELEASING.md` 의 "관계법령 갱신 항목 템플릿"으로 `### 관계법령 갱신` 절을 만든다.
     - 법령별 판본 변화(시행일 이전 → 현행)를 적는다.
     - `diff_laws.py --markdown` 표를 붙이고, 행마다 처리 결과(요약 갱신 / 배정표 변경 / 영향 없음)를 단다.
2. PR 을 연다.
   - 제목: `실무기준·관계법령 갱신 (YYYY-MM-DD 기준)`. 바뀐 쪽만 이름에 넣는다.
   - 라벨: 실무기준 개정은 `standard-update`, 관계법령 개정은 `law-update` (둘 다면 둘 다)
   - 이슈 템플릿: `.github/ISSUE_TEMPLATE/standard-update.md`, `law-update.md`
3. 버전(`docs/RELEASING.md`):
   - MINOR: 실무기준 개정, 또는 법령 내용 변경
   - PATCH: 개정 표시만 변경
   - 병합 후 병합 커밋에 태그를 달고 릴리스를 만든다.
4. 사용자에게 보고한다.
   - 확인 일자, 실무기준 고시 변화, 바뀐 법령 수, 변경 조항·조문 수
   - 요약을 고친 스킬 목록
   - 사람이 판단해야 할 사항. 예: 조문 번호가 바뀌어 실무기준 인용이 어긋나게 된 경우
