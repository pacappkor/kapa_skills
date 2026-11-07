---
name: 00-kapa-start
description: kapa_skills 저장소의 입구. 감정평가 실무기준 컬렉션과 관계법령 컬렉션 중 어디서 시작할지 정한다.
---

# 00-kapa-start — 저장소 입구

감정평가 업무용 스킬 저장소다. 두 갈래로 나뉘고, 어느 쪽에서 출발해도 서로 이어진다.

| 시작점 | 내용 | 이럴 때 |
|---|---|---|
| [00-practice-standards-start](../appraisal-practice-standards/00-practice-standards-start/SKILL.md) | 「감정평가 실무기준」(국토교통부고시) 전 조항. 작업 절차(평가 수행·조항 찾기·평가서 검토·수임 판단) 포함 | 감정평가 의뢰를 처리하거나 평가 기준을 찾을 때. **대부분의 감정평가 업무는 여기서 시작한다** |
| [00-laws-start](../laws/00-laws-start/SKILL.md) | 관계법령: 토지보상법, 감정평가법·감정평가에 관한 규칙, 부동산공시법, 국토계획법, 도시정비법 전문과 실무기준이 인용한 다른 법령 조항 | 법령 조문 자체를 찾거나, 실무기준이 "관계법규에 따로 정한 것"으로 넘기는 내용을 확인할 때 |

## 출발점별 안내

| 출발점 | 먼저 읽을 것 |
|---|---|
| 감정평가 의뢰·평가서·수임 | [00-practice-standards-start](../appraisal-practice-standards/00-practice-standards-start/SKILL.md) |
| 공익사업 수용·보상 사건 (근거법·토지보상법·실무기준이 함께 걸림) | [workflow-compensation-chain](../laws/workflow-compensation-chain/SKILL.md) |
| 개별 법률에서 출발: 도로법·도시개발법·택지개발촉진법·하천법 등 공익사업 근거법 | [00-pwa-start](../laws/public-works-acts/00-pwa-start/SKILL.md) 법률별 색인 → workflow-compensation-chain |
| 국토계획법·도시정비법·토지보상법·감정평가법·부동산공시법 조문 | [00-laws-start](../laws/00-laws-start/SKILL.md) |
| 실무기준·토지보상법이 인용한 다른 법령 조항 (건축법, 수산업법 등) | [00-rel-start](../laws/related-provisions/00-rel-start/SKILL.md) |

## 양방향 연결

- **나가는 연결**: 각 스킬의 "참조 관계"에 그 원문이 인용한 조항·조문의 스킬 링크가 자동 생성된다.
  예: 실무기준 → 관계법령, 근거법 → 토지보상법
- **들어오는 연결**: 각 스킬 끝의 "들어오는 연결"에 그 스킬의 원문을 인용·준용하는 스킬이 자동 생성된다.
  예: 토지보상법 사업인정·재결 → 그것을 준용하는 도로법·도시개발법 등
- 실무기준의 `workflow-appraisal` 우선순위 ①(관계법규)은 법령 컬렉션을 가리킨다.

## 규칙 (서로 분리되어 있다)

| 규칙 | 언제 | 스킬 |
|---|---|---|
| 읽기 규칙 | 스킬을 읽고 답하는 모든 작업. 원문 확인, 인용 형식, 우선순위, 판본 | [skill-reading-rules](../rules/skill-reading-rules/SKILL.md) |
| 갱신 절차 | 사용자가 실무기준 또는 관계법령 개정에 따른 스킬 갱신을 명시적으로 지시했을 때만 | [skill-update-maintenance](../rules/skill-update-maintenance/SKILL.md) |

스킬을 읽는 작업 중에는 파일을 고치지 않는다. 갱신 절차는 갱신 지시를 받았을 때만 연다.
