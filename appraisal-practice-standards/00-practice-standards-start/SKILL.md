---
name: 00-practice-standards-start
description: 「감정평가 실무기준」 스킬 컬렉션의 입구. 작업 유형을 가려 알맞은 작업 절차 스킬로 보내고, 컬렉션의 층 구조를 설명한다.
---

# 00-practice-standards-start — 입구

「감정평가 실무기준」(국토교통부고시 제2023-522호, 2023. 9. 13. 일부개정·시행)을 에이전트가 쓰기 좋게 나눈 컬렉션이다.
이 파일은 짧게 둔다. 작업 유형을 가린 뒤 해당 **작업 절차 스킬**(`workflows/`)로 넘어간다.

## 1. 작업 유형 → 작업 절차 스킬

| 작업 유형 | 신호 | 다음에 읽을 것 |
|---|---|---|
| **평가 수행** | 의뢰서, "~을 감정평가해줘", 가액 산정, 평가 계획 | [workflow-appraisal](../workflows/workflow-appraisal/SKILL.md) |
| **조항·개념 질의** | "~란?", "~는 어떻게 평가하나", "근거 조항은?", 시험 문제 | [lookup-clause](../workflows/lookup-clause/SKILL.md) |
| **감정평가서 검토·심사** | 작성된 감정평가서, 적정성 심사, "검토해줘" | [workflow-report-review](../workflows/workflow-report-review/SKILL.md) |
| **수임 판단** | "맡아도 되나", 이해관계, 조건부 의뢰, 철회 | [workflow-engagement-check](../workflows/workflow-engagement-check/SKILL.md) |
| **개정·버전 확인** | "현행 기준인가", 오래된 기준시점 | [foundation-general-provisions](../foundations/foundation-general-provisions/SKILL.md) 부칙 목록. 이 컬렉션은 제2023-522호 기준이다 |

여러 유형이 섞이면 처리 순서는 수임 판단 → 평가 수행 → 검토다.

## 2. 컬렉션의 층 구조

실무기준의 장 순서(100~900)가 아니라 **에이전트가 규정을 쌓아 쓰는 방식**으로 폴더를 나눴다.

```text
00-practice-standards-start/   입구 (이 파일)
workflows/                     작업 절차 — 무엇을 어떤 순서로 읽고 확인할지
  workflow-appraisal/          평가 수행: 결정 사실 → 우선순위 스택 → 절차 단계별 읽기 (+ facets.md 조회표, cases.md 사례)
  lookup-clause/               찾기: 용어 색인(terms.md), 원문 검색, 인용 따라가기
  workflow-report-review/      감정평가서 검토·심사
  workflow-engagement-check/   수임 판단
foundations/   foundation-*    기반 규정 — 모든 평가에 깔리는 [100]~[500] (정의·윤리·수임·절차와 방법·감정평가서)
assets/        asset-*         기반 규정 — 대상물건별 [600], 물건 계열별 하위 폴더
  real-estate/                 토지·건물·구분소유·복합부동산·산림·과수원·염전·공사중단 건축물 [610]
  industrial/                  공장재단·광업재단·기계기구류 [620]·[630]
  movables/                    자동차·건설기계·선박·항공기 [640 의제부동산] + 동산 [670-1]
  intangibles/                 광업권·어업권·영업권·지식재산권·주식·채권·기업가치
  income-and-loss/             임대료·권리금·소음등으로 인한 가치하락분
  asset-other/                 위에 없는 물건 [670-5]
overlays/      overlay-*       특칙 — 기반 규정 위에 덮어쓰는 목적별 [700]·보상평가 [800]
  purpose/                     담보·경매·도시정비·재무보고·상담자문
  compensation/                취득 토지·사용 토지·권리·영업손실 보상
```

- 평가 하나는 **기반 규정(foundations + 해당 assets) 위에 특칙(overlays)을 얹은 스택**이다. 보통 특칙은 하나다.
  다만 특칙 원문이 다른 특칙으로 보낼 수 있다(도시정비 수용등 [730-3.5] → 보상 [800], 사용 토지 [820-5.2.1-2] → 취득 토지 [810-5.6]).
  이런 호출 관계와 법적 우선순위(보상 > 목적 > 물건 > 공통)는 다른 개념이다. workflow-appraisal 2단계에서 구분한다.
- 특칙 절이 다른 장을 "적용"하는지 "준용"하는지는 원문이 스스로 정한다.
- 우선순위를 정하는 방법은 [workflow-appraisal](../workflows/workflow-appraisal/SKILL.md) 에 있다.
- 내용 스킬마다 두 파일이 있다.
  - `SKILL.md`: 요약, 확인사항, 함께 읽을 스킬, 조항 목차, 참조 관계
  - `source.md`: 원문 전문

## 3. 공통 원칙

읽기 규칙은 [skill-reading-rules](../../rules/skill-reading-rules/SKILL.md) 하나에 있다. 다음 사항이 그 스킬에 정리되어 있다.
- 요약만 보고 결론 내리지 않고 `source.md` 로 확인하는 것
- `[610-1.5.2.1-①]` 형식 인용
- 원문에 없는 수치 금지와 "의뢰인 확인 필요"·"관계법규 확인 필요" 표시
- 의무/재량 구분
- 관계법령 > 실무기준 우선순위

관계법규 원문은 [00-laws-start](../../laws/00-laws-start/SKILL.md) 컬렉션에 있다.

## 4. 주소

- @skills:
  - 입구: `@skills:gh:pacappkor/kapa_skills/appraisal-practice-standards/00-practice-standards-start`
  - 층별 메뉴: `…/workflows`, `…/foundations`, `…/assets/real-estate`, `…/overlays/compensation` 등
- 상주시킨다면 이 입구 한 줄만 auto-trigger 에 둔다. 나머지는 경로로 그때그때 읽는다.
- @skills 클라이언트가 없으면 파일을 직접 읽으면 된다. 같은 경로를 그대로 쓴다.
