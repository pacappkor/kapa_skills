---
name: workflow-compensation-chain
description: 공익사업의 수용·보상 사건을 근거법(도로법·도시개발법·국토계획법·도시정비법 등)→토지보상법→감정평가 실무기준으로, 또는 그 역방향으로 따라가는 법령 연결 절차.
---

# workflow-compensation-chain — 법령 사이를 오가는 수용·보상 절차

공익사업의 수용·보상은 법령 세 겹이 함께 작동한다.

```text
근거법 (사업을 정한 개별 법률: 도로법, 도시개발법, 택지개발촉진법, 하천법, 국토계획법, 도시정비법 …)
   │ 수용·사용 권한, 사업인정 의제, 재결신청 기간 특례, 토지보상법 준용, 보상 특례
   ▼
토지보상법 · 시행령 · 시행규칙 (절차와 보상 기준)
   │ 보상액 산정 = 감정평가 (법 제68조), 평가 기준 (시행규칙 제5장)
   ▼
감정평가 실무기준 [800] 보상평가 → [600] 물건별 → [100]~[500] 공통
```

사건은 어느 층에서든 시작될 수 있다. 시작한 층과 상관없이 세 층을 모두 확인하고, 아래 우선순위로 정리한다.

## 1. 출발점을 파악한다

| 출발점 | 예 | 먼저 볼 곳 |
|---|---|---|
| 근거법(개별 공익사업법) | "도로구역 편입", "도시개발구역 수용", "하천구역 편입", "택지개발지구 보상" | [00-pwa-start](../public-works-acts/00-pwa-start/SKILL.md) 법률별 색인 (법률 이름으로 grep) |
| 국토계획법 도시·군계획시설사업 | 도시계획도로·공원 등 시설사업, 장기미집행 시설 부지 매수청구 | [nlp-facility-project](../national-land-planning-act/nlp-facility-project/SKILL.md) (법 제88조 실시계획, 법 제96조 토지보상법 준용), [nlp-planning-facilities](../national-land-planning-act/nlp-planning-facilities/SKILL.md) (법 제47조 매수청구) |
| 도시정비법 정비사업 | 재개발 수용, 현금청산, 손실보상 | [ura-implementation-measures](../urban-redevelopment-act/ura-implementation-measures/SKILL.md) (법 제62조·제63조·제65조), [ura-management-disposal-plan](../urban-redevelopment-act/ura-management-disposal-plan/SKILL.md) (영 제60조 분양신청을 하지 않은 자 등) |
| 국토계획법 장기미집행 시설 부지 매수청구 | 매수가격 산정 | [nlp-planning-facilities](../national-land-planning-act/nlp-planning-facilities/SKILL.md): 법 제47조제4항은 매수가격·절차에 "이 법에 특별한 규정이 있는 경우 외에는" 토지보상법을 준용한다. 그다음 [lca-compensation-principles](../land-compensation-act/lca-compensation-principles/SKILL.md)(법 제67조 가격시점·개발이익 배제, 제68조 감정평가), [lca-land-compensation](../land-compensation-act/lca-land-compensation/SKILL.md)(규칙 제22조·제23조), 실무기준 [810]. 시설결정이 규칙 제23조의 "해당 공익사업의 시행을 직접 목적으로 하는 제한"인지는 원문 문구로 판단하고 근거를 남긴다 |
| 농작물·시설(비닐하우스 등)이 있는 편입 토지 | 농작물·시설·영농손실 | [lca-objects-compensation](../land-compensation-act/lca-objects-compensation/SKILL.md)(법 제75조제2항·규칙 제41조 농작물, 규칙 제33조·제36조 건축물·공작물), [lca-business-farming-loss](../land-compensation-act/lca-business-farming-loss/SKILL.md)(규칙 제48조 영농손실). 실무기준에는 농작물 평가 절이 없다. 규칙이 인용하는 고시(예: 농작물실제소득인정기준)는 이 저장소에 없으므로 원문을 확인해야 한다고 적는다 |
| 토지보상법 | 사업인정, 재결, 보상항목, 이의신청 | [00-lca-start](../land-compensation-act/00-lca-start/SKILL.md) 주제 지도 |
| 감정평가 의뢰·실무기준 | "보상평가 의뢰", "편입 토지 감정평가" | [workflow-appraisal](../../appraisal-practice-standards/workflows/workflow-appraisal/SKILL.md) (F1=손실보상) |

## 2. 근거법을 확정하고 특례를 먼저 확인한다

1. 사업의 근거 법률을 확정한다.
   - 토지보상법 제4조(공익사업)와 그 별표가 근거법 목록이다: [lca-general](../land-compensation-act/lca-general/SKILL.md)
   - 의뢰서·사업인정고시·실시계획인가 등에 근거법이 적혀 있지 않으면 "의뢰인 확인 필요"로 남긴다.
2. 근거법 스킬에서 토지보상법과 다르게 정한 내용을 찾는다. 각 근거법 스킬의 `## 적용 시 확인사항` 을 따른다.
   - **수용·사용 권한과 대상**: 누가, 어느 구역에서, 어떤 토지등을
   - **사업인정 의제**: 어떤 인가·승인·고시를 사업인정(토지보상법 제20조)과 그 고시(제22조)로 보는지. 이 시점이 재결신청 기간과 보상기준 시점 판단에 쓰인다.
   - **재결신청 기간 특례**: 토지보상법 제23조(사업인정의 실효)·제28조(재결의 신청)와 다른 기간
   - **준용 범위**: 흔히 "이 법에 특별한 규정이 있는 경우 외에는 토지보상법을 준용한다"고 쓴다. 근거법 원문의 문구를 그대로 확인한다.
   - **보상 특례**: 이주대책, 보상기준, 협의·재결 절차 위탁 등
3. 근거법이 C층(공익사업 근거법)에 연결 조항이 없다고 표시되면 그 법률의 해당 사업 조항을 국가법령정보센터에서 확인한다.
   C층에는 토지보상법을 언급하는 조문만 수록했다.

## 3. 토지보상법의 절차와 보상 항목을 확인한다

| 단계·항목 | 스킬 |
|---|---|
| 협의취득 (토지조서·물건조서, 보상계획, 협의) | [lca-acquisition-by-agreement](../land-compensation-act/lca-acquisition-by-agreement/SKILL.md) |
| 사업인정, 재결 신청·청구, 재결 | [lca-expropriation-procedure](../land-compensation-act/lca-expropriation-procedure/SKILL.md) |
| 보상금 지급·공탁, 인도·이전 | [lca-expropriation-effects](../land-compensation-act/lca-expropriation-effects/SKILL.md) |
| 보상 원칙, 보상액 가격시점, 감정평가 의뢰(법 제68조) | [lca-compensation-principles](../land-compensation-act/lca-compensation-principles/SKILL.md) |
| 토지 / 물건 / 권리 / 영업·농업 / 이주대책 / 그 밖의 손실 | [lca-land-compensation](../land-compensation-act/lca-land-compensation/SKILL.md) / [lca-objects-compensation](../land-compensation-act/lca-objects-compensation/SKILL.md) / [lca-rights-compensation](../land-compensation-act/lca-rights-compensation/SKILL.md) / [lca-business-farming-loss](../land-compensation-act/lca-business-farming-loss/SKILL.md) / [lca-relocation](../land-compensation-act/lca-relocation/SKILL.md) / [lca-other-losses](../land-compensation-act/lca-other-losses/SKILL.md) |
| 이의신청·행정소송 / 환매권 | [lca-objection-litigation](../land-compensation-act/lca-objection-litigation/SKILL.md) / [lca-repurchase-right](../land-compensation-act/lca-repurchase-right/SKILL.md) |

## 4. 감정평가로 넘어간다

- 보상액을 감정평가로 산정할 때는 [workflow-appraisal](../../appraisal-practice-standards/workflows/workflow-appraisal/SKILL.md) 을 F1=손실보상으로 수행한다.
- 감정평가 기준은 두 곳에서 본다.
  - 토지보상법 시행규칙 제5장(손실보상평가의 기준)
  - 「감정평가 실무기준」 [800]
- 실무기준 [800]은 810(취득 토지)·820(사용 토지)·830(광업권·어업권)·840(영업손실)뿐이다. 그 밖의 항목은 토지보상법 시행규칙을 따른다(3단계 표).

## 5. 우선순위로 정리한다

```text
① 근거법의 특별 규정        (근거법이 위임한 그 시행령 등 포함. 근거법이 "특별한 규정이 있는 경우 외에는 토지보상법 준용" 구조일 때. 원문 문구로 확인)
② 토지보상법                (법률)
③ 토지보상법 시행령·시행규칙
④ 감정평가 실무기준 [800] 해당 절   ([810-2] 등: 토지보상법 등 감정평가관계법규에서 따로 정한 것을 제외하고 적용)
⑤ 감정평가 실무기준 [600] 물건 → [100]~[500] 공통
```

- **근거법이 하위 법령에 위임한 경우**: 근거법 자신의 시행령이 정한 기준이 토지보상법보다 먼저다(①에 포함).
  - 예: 도시정비법 제65조제1항 단서는 "정비사업의 시행에 따른 손실보상의 기준 및 절차는 대통령령으로 정할 수 있다"고 한다.
  - 이에 따라 도시정비법 시행령 제54조·제60조 등이 정한 내용은 토지보상법보다 먼저 본다([ura-implementation-measures](../urban-redevelopment-act/ura-implementation-measures/SKILL.md), [ura-management-disposal-plan](../urban-redevelopment-act/ura-management-disposal-plan/SKILL.md)).
- **개정 전 번호 인용**: 실무기준이 개정 전 조문 번호로 인용한 경우가 있다(예: [730]의 도정법 제38조·제39조·제48조·제66조).
  - 실무기준 스킬의 "참조 관계"는 이런 인용을 현행 대응 조문(제63조·제64조·제74조·제98조)으로 연결하고 "개정 전 번호 → 현행"을 표시한다.
- 근거법과 토지보상법이 충돌하는 것처럼 보이면 근거법 원문의 준용 문구와 특례 조문을 인용해 판단 근거를 남긴다. 추측으로 정하지 않는다.
- 관계법령은 판본(시행일)을 확인한다. 사건 당시 판본이 현행과 다를 수 있다.

## 6. 역방향으로 찾을 때

- **특례를 가진 법률을 찾을 때**: [00-pwa-start](../public-works-acts/00-pwa-start/SKILL.md) 의 "특례 색인"을 grep 한다. 사업인정 의제, 재결신청 기간 특례, 준용 여부와 문구 발췌가 법률·조문별로 있다.
- 각 스킬 끝의 **들어오는 연결**(`## 들어오는 연결`)을 쓴다. 표기는 `도로법 제82조: 「…」 제23조` 처럼 인용하는 쪽 조문까지 보인다.
  - 예: [lca-expropriation-procedure](../land-compensation-act/lca-expropriation-procedure/SKILL.md) 의 들어오는 연결에는 토지보상법 제20조·제23조·제28조 등을 인용하는 근거법 스킬과 국토계획법·실무기준 스킬이 나온다.
  - "어떤 법률이 사업인정 의제·재결신청 기간 특례를 두는가"를 이렇게 찾는다.
- 저장소 전체 간선 목록은 `docs/graph.json` 에 있다.

## 7. 기록

```text
출발점: <근거법 / 국토계획법 / 도시정비법 / 토지보상법 / 실무기준>
근거법과 연결 조항: <「도로법」 제82조 등 — 수용 권한, 사업인정 의제(시점), 재결신청 기간, 준용 범위, 특례>
토지보상법: <절차 단계와 보상 항목별 조문>
감정평가: <실무기준 조항, 시행규칙 조항>
우선순위 판단: <①~⑤ 중 적용한 것과 근거 문구>
확인 필요: <의뢰서·고시에 없는 사실, 판본 차이>
```

회귀 사례와 기대 결과: [cases.md](cases.md). 이 절차나 연결 생성기를 고치면 사례로 다시 확인한다.
