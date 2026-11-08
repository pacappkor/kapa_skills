# kapa_skills

감정평가 업무용 에이전트 스킬 저장소. 저장소 입구는 [00-kapa-start](00-kapa-start/SKILL.md) 이다. 두 갈래가 있다.

| 컬렉션 | 내용 | 입구 |
|---|---|---|
| [appraisal-practice-standards](appraisal-practice-standards/README.md) | 「감정평가 실무기준」(국토교통부고시 제2023-522호) [100]–[900] 전 조항. 입구 1 + 작업 절차 4 + 내용 스킬 41 | [00-practice-standards-start](appraisal-practice-standards/00-practice-standards-start/SKILL.md) |
| [laws](laws/README.md) | 관계법령. A층(전문): 토지보상법, 감정평가법·감정평가에 관한 규칙, 부동산공시법, 국토계획법, 도시정비법. B층: 실무기준·토지보상법 시행규칙이 인용한 다른 법령 조항. 주제 스킬 80 + 입구 | [00-laws-start](laws/00-laws-start/SKILL.md) |

## 에이전트가 이 저장소를 쓰는 방법

규칙은 두 갈래로 분리되어 있고 섞지 않는다(`tools/validate.py` 가 검사).
- **읽기 규칙** [skill-reading-rules](rules/skill-reading-rules/SKILL.md): 스킬을 읽고 답하는 모든 작업. 파일을 고치지 않는다.
- **갱신 절차** [skill-update-maintenance](rules/skill-update-maintenance/SKILL.md): 실무기준 또는 관계법령 개정에 따른 스킬 갱신을 명시적으로 지시받았을 때만 쓴다.

1. **입구를 읽는다**: 감정평가 업무는 `appraisal-practice-standards/00-practice-standards-start/SKILL.md`, 법령 조문은 `laws/00-laws-start/SKILL.md`.
   실무기준 입구는 작업 유형을 가려 작업 절차 스킬(`workflows/`)로 넘어간다.
   - 평가 수행 → `workflow-appraisal`
   - 조항·개념 질의 → `lookup-clause`
   - 감정평가서 검토 → `workflow-report-review`
   - 수임 판단 → `workflow-engagement-check`
2. 작업 절차 스킬이 가리키는 내용 스킬의 `SKILL.md` 를 읽는다. 요약, 확인사항, 함께 읽을 스킬, 참조 관계가 들어 있다.
3. 판단하거나 인용하기 전에 같은 폴더의 `source.md` 에서 원문을 확인한다. 근거는 실무기준 표기(예: `[610-1.5.2.1-①]`) 또는 조문 표기(예: `토지보상법 시행규칙 제22조`)로 단다.
4. 실무기준이 "감정평가관계법규에 따로 정한 것"으로 넘기는 내용은 `laws/` 의 법령 스킬로 확인한다. 실무기준 스킬의 "참조 관계"에 인용 조문 링크가 있다.

## 구조

```text
00-kapa-start/                     저장소 입구
rules/                             규칙: skill-reading-rules(읽기) · skill-update-maintenance(갱신)
laws/                              관계법령 (laws/README.md)
appraisal-practice-standards/
├── 00-practice-standards-start/   입구
├── workflows/                     작업 절차: workflow-appraisal(+facets.md, cases.md) · lookup-clause(+terms.md)
│                                             · workflow-report-review · workflow-engagement-check
├── foundations/  foundation-*     기반: 공통 [100]~[500]
├── assets/       asset-*          기반: 물건 [600] — real-estate · industrial · movables([640] 의제부동산+[670-1] 동산) · intangibles · income-and-loss
└── overlays/     overlay-*        특칙: purpose/ 목적별 [700] · compensation/ 보상평가 [800]
```

- 폴더는 실무기준의 장 순서가 아니라 **에이전트가 규정을 쌓아 쓰는 방식**으로 나눴다.
- 평가 하나는 "기반(foundations + 해당 assets) 위에 특칙(overlays)을 얹은" 우선순위 스택이다.
  보통 특칙은 하나지만, 특칙 원문이 다른 특칙을 부르면 함께 읽는다(workflow-appraisal 2단계).
- 이름은 `<층>-<주제>` 이고 폴더 이름과 같으며, 저장소 안에서 유일하다.
- 설계 검토(진입 방식 비교, 폴더 구조 근거, 독립 에이전트 검토 결과)는 [docs/ROUTING.md](docs/ROUTING.md) 에 있다.

설계는 [@skills: Attention is all you have (arXiv:2608.12610)](https://arxiv.org/abs/2608.12610)를 따른다.
- 스킬을 설치해 설명을 프롬프트에 상주시키지 않고, 경로로 주소를 붙여 필요할 때 읽는다.
- 디렉터리는 메뉴다. 예: `…/assets/real-estate` 를 읽으면 부동산 스킬 목록이 나온다.
- leaf rule 을 지킨다(스킬 안에 스킬 없음).
- description 은 사실만 담은 한 줄로 쓴다.
- 상주시킨다면 입구 한 줄만 둔다: `.atskills/.autotrigger` 에 `gh:pacappkor/kapa_skills/00-kapa-start`. 실무기준과 관계법령 양쪽으로 갈라진다(실무기준만 쓰면 `…/appraisal-practice-standards/00-practice-standards-start`).

@skills 클라이언트가 없는 에이전트는 파일을 직접 읽으면 된다.
스킬을 설치하는 도구(Claude Code·Codex 등)라면 스킬 폴더를 복사해도 된다. 이름이 유일하므로 충돌하지 않는다.

## 원문과 재생성

관계법령(`laws/`)의 수집·생성·검증·갱신 도구는 [laws/README.md](laws/README.md) 의 "도구" 표에 있다. 아래는 실무기준 도구다.

- `tools/fetch_standard.py`: 국가법령정보센터 행정규칙 본문(AJAX 엔드포인트)을 받아 `sources/appraisal-practice-standards/<admRulSeq>.txt` 로 저장한다.
  본문 속 산식 이미지 3개는 `img-<flSeq>.gif` 로 저장한다.
- `tools/split_standard.py`:
  - 원문을 조항 단위로 파싱하고 배정표(`SKILLS`)대로 각 스킬 폴더에 `source.md` 를 쓴다.
  - `SKILL.md` 의 자동 생성 블록(근거, 조항 목차, 참조 관계)만 갱신한다.
  - `--check` 는 모든 조항이 정확히 한 스킬에 배정됐는지 확인한다.
- `tools/validate.py`:
  - frontmatter, 이름 유일성, leaf rule, 깨진 링크를 검사한다.
  - 입구·workflows 가 모든 스킬을 다루는지 검사한다.
  - `split_standard.py --check`·`build_laws.py --check`·`graph.py --check` 를 함께 실행한다.
  - 읽기 규칙과 갱신 절차의 분리(`rules/`)를 검사한다.

```sh
python -I tools/fetch_standard.py --check  # 현행 고시가 저장소 판본과 같은지 확인
python -I tools/fetch_standard.py          # 원문 다시 받기 (개정 시 새 admRulSeq 인자)
python -I tools/split_standard.py          # source.md·생성 블록 갱신
python -I tools/validate.py                # 검증 (오류 0 이어야 함)
```

실무기준이나 관계법령이 개정되면 [rules/skill-update-maintenance](rules/skill-update-maintenance/SKILL.md) 절차를 따른다.
- 어느 쪽 개정이든 `fetch_standard.py --check`·`fetch_laws.py --check` 로 둘 다 확인한다.
- 이슈는 `.github/ISSUE_TEMPLATE` 의 "실무기준 개정 반영" 또는 "관계법령 개정 반영" 템플릿으로 연다.

## 버전과 변경 이력

- 현재 버전과 변경 내용: [CHANGELOG.md](CHANGELOG.md)
- 버전·기록 규칙: [docs/RELEASING.md](docs/RELEASING.md)
  - 실무기준 개정과 관계법령 내용 변경은 MINOR 를 올린다. 법령의 개정 표시만 바뀌면 PATCH 다.
  - CHANGELOG 각 버전에 근거 고시 번호(실무기준)와 법령별 판본 변화(관계법령)를 기록한다.

## 라이선스와 출처

법령 원문은 국가법령정보센터(law.go.kr) 현행 법령이며 「저작권법」 제7조에 따라 보호받지 않는다.

이 저장소는 **[GNU GPL v3.0](LICENSE)** 으로 배포한다. GPL 이 적용되는 범위는 다음과 같다.

- 스킬 묶음의 구성: 분류 체계, 이름, 조항 배정
- 요약
- 입구·작업 절차 스킬
- 문서
- 도구

원문인 「감정평가 실무기준」은 국토교통부 고시(행정규칙)라 「저작권법」 제7조에 따라 보호받지 않으며, 원문 텍스트 자체는 누구나 이용할 수 있다.
자세한 내용은 [NOTICE.md](NOTICE.md) 에 있다. 요약과 라우팅 문서는 보조 자료다. 법적 판단은 원문과 관계법규로 확인한다.
