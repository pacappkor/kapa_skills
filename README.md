# kapa_skills

[스킬·법령·실무기준 사이트](https://pacappkor.github.io/kapa_skills/) · [로컬 사이트 빌드](docs/SITE.md)

[![visitors](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pacappkor/kapa_skills/traffic/.traffic/badge-views.json)](https://github.com/pacappkor/kapa_skills)
[![clones](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pacappkor/kapa_skills/traffic/.traffic/badge-clones.json)](https://github.com/pacappkor/kapa_skills)

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

## 공개 정책과 이용 시 주의사항

2026-11-11 정책에 따라 GitHub 저장소는 공개할 수 있다. HF 시장 데이터셋 `pacappkor/kapa-market-data`는 공개이며, HF staging 데이터셋은 비공개로 유지한다. 인증정보는 어떤 저장소에도 두지 않는다. 외부 자료의 라이선스와 재배포 제한은 계속 지킨다.

공개는 법적 정확성·최신성 또는 공식답안 지위를 보증하지 않는다. 적용 시점의 원문과 관계법규를 직접 확인한다. 보안 취약점은 [보안 정책](SECURITY.md)에 따라 비공개로 신고한다.

상단 배지는 GitHub 저장소 traffic views와 clone 수를 나타내며 외부 방문 추적 픽셀은 사용하지 않는다. `uniques`는 일별 합계로, 평생 중복 제거한 사용자 수가 아니다. 일일 집계는 [traffic 워크플로](.github/workflows/traffic.yml)가 main을 동기화한 `traffic` 브랜치에 보존한다. 첫 성공 실행 전에는 배지가 없거나 오류로 보일 수 있다. 운영자는 중앙 `pacappkor/.github` 공개, 제한된 `TRAFFIC_TOKEN` Actions secret(Administration 읽기 전용), `contents: write` 허용 및 traffic 브랜치의 정상 push 허용을 확인해야 한다. 집계 데이터는 main에서 편집하거나 역병합하지 않는다.

## CI

- [GitHub Actions CI](.github/workflows/ci.yml)는 모든 PR, `main` 푸시, 수동 실행에서 Python 3.12로 오프라인 검증을 수행한다.
- 한 작업에서 PR 변경 경로에 따라 실무기준·법령·구조 검증·도구 테스트를 선택한다. `LICENSE` 같은 비 Markdown 링크 대상까지 모든 경로 변경은 구조·링크 검증, `tools/` 변경은 전체 단위 테스트 대상이며, 생성기 사이에 공유하는 원문·색인 입력은 관련 검사를 함께 실행한다. 법령 색인 생성기가 있으면 `build_index.py --check`도 실행한다.
- PR 은 존재하는 기준 SHA, 일반 푸시는 조상인 `before` 를 사용한다. 강제 푸시는 공통 조상을 사용하되 전체 검사한다. 수동 실행·기준 누락·공통 조상 없음·변경 조회 실패도 전체 검사한다. 공백 검사는 같은 기준을 사용하며 기준이 없으면 빈 트리, 수동 실행에 부모가 있으면 `HEAD^`, 부모 없는 HEAD 는 항상 빈 트리와 비교한다. 선택 결과와 이유는 실행 요약에 남긴다.
- 공백 검사는 일반 변경 비교와 빈 트리 비교 모두에서 기계 생성 원문인 `**/source.md`와 `sources/laws/*/annex/*.txt`를 제외한다. 원문 공백은 보존하고 생성물은 생성기 `--check` 단계로 검증한다. 사람이 작성하는 파일(`annex-md/*.md`, `SKILL.md` 포함)은 두 비교 모두 공백 검사 대상이다.
- 현행 고시·법령 조회는 네트워크와 인증이 필요하므로 CI에서 실행하지 않는다. 비밀정보와 정기 실행 없이, 개정 확인은 사용자 요청에 따라 갱신 절차에서 수행한다.

### 표준 테스트 탐색과 위협 모델

저장소 루트에서 `python -I -B tools/ci_tests_supervise.py` 를 실행한다.
감독 실행기는 먼저 `python -I -B tools/ci_layout_check.py` 로 구조만 검사한다.
이 검사는 tools 코드를 import하지 않으며, `tools/**/test_*.py` 파일이 없거나
테스트 파일명이 unittest의 파일명 정규식에 맞지 않으면 실패한다.
패키지 폴더명은 Python 3.12·3.14의 표준 탐색처럼 식별자·예약어 여부를 검사하지 않는다
(`class`, `my-pkg`, `123abc`도 허용).
테스트 폴더에서 `tools/` 까지의 각 폴더에는 `__init__.py` 파일이 있어야 한다.

그다음 저장소 루트에서 다음 **표준 명령을 그대로** 별도 프로세스로 실행한다.

```sh
python -I -B -m unittest discover -s tools -t . -p "test_*.py" -v
```

Python 3.12·3.14에서 `-I` 와 함께 사용해도 unittest의 `-t .` 가 저장소 루트를
검색 경로에 추가하므로 tools 패키지를 탐색한다. 별도 로더, import 도달 관찰자,
import 캐시 조작, 완료 표지 없이 표준 unittest의 import·load_tests·skip 동작을 따른다.
테스트는 패키지 import 또는 테스트 파일 자체의 최소한의 형제 경로 설정을 사용한다.
`-B` 는 바이트코드 생성을 막으며 CI는 `PYTHONDONTWRITEBYTECODE=1` 도 설정한다.

stdout·stderr는 그대로 출력하되 판정에 필요한 경계 이전 stderr만 메모리에 보관한다.
성공하려면 종료 코드가 0이고, 외부 테스트 프로세스 종료 직후 이미 버퍼에 있는 stderr를
비차단으로 수집해 경계를 기록한다. 각 수집은 시작 시 대기 중인 바이트 수로 제한하여
계속 출력하는 하위 프로세스도 잠금을 무한히 점유하지 못하며 종료 후 10초 대기를 지킨다.
경계 이전 stderr의 마지막 `Ran N tests` 요약과 그 직후 비어 있지 않은 줄의 `OK` 또는
`OK (...)` 가 모두 있어야 한다. 이후 하위 프로세스 출력은 표시하되 판정에서는 제외한다.
N은 1 이상이어야 하며, 0이면 OK 줄에
`skipped=K` (K ≥ 1)가 있어야 한다. `os._exit(0)` 같은 우발적 조기 종료로 요약이
없거나, 빈 실행·실패 종료·마지막 OK 누락이면 원인을 표시하고 실패한다.

테스트 파일과 패키지 초기화 코드는 PR에서 검토하는 **신뢰된 코드**이며 임의의 코드를
실행할 수 있다. 이 검사는 패키지 구조와 출력 기반 완료 여부만 확인하는 것이지,
파일별 탐색 도달·모든 테스트의 실행을 증명하거나 샌드박스·악성 테스트 방어를 제공하지 않는다.
신뢰된 load_tests나 result.stop()의 동작도 표준 unittest에 맡긴다.
고의적인 출력 위조나 우회는 CI가 아니라 코드 리뷰에서 차단한다.

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
