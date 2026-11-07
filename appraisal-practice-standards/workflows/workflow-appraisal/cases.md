# 라우팅 사례 — 기대 결과

[workflow-appraisal](SKILL.md) 와 [00-practice-standards-start](../../00-practice-standards-start/SKILL.md) 를 고친 뒤 이 사례로 다시 확인한다.
각 사례의 "핵심 조항"은 원문에서 확인한 것이다. "스택"은 위가 우선이다.

| # | 작업 | 유형 | 결정 사실 | 스택(특칙 > 물건 > 기반) | 핵심 조항 |
|---|---|---|---|---|---|
| 1 | 은행이 아파트 한 호실 담보평가 의뢰 | 평가 수행 | F2=담보, F3=구분소유 | [overlay-collateral](../../overlays/purpose/overlay-collateral/SKILL.md) > [asset-condominium](../../assets/real-estate/asset-condominium/SKILL.md) > foundations | [710-②·③], [610-3.1.3], [400-4] |
| 2 | 법원 경매 — 단독주택(토지+건물) | 평가 수행 | F2=경매, F3=복합부동산 | [overlay-auction](../../overlays/purpose/overlay-auction/SKILL.md) > [asset-land-building-composite](../../assets/real-estate/asset-land-building-composite/SKILL.md) + [asset-land](../../assets/real-estate/asset-land/SKILL.md) + [asset-building](../../assets/real-estate/asset-building/SKILL.md) | [720-②], [610-3.2.3], [610-1.5.1-③-3] |
| 3 | 도로 공사에 편입되는 농지 보상 | 평가 수행 | F1=취득 토지 | [overlay-compensation-land-acquisition](../../overlays/compensation/overlay-compensation-land-acquisition/SKILL.md) > [asset-land](../../assets/real-estate/asset-land/SKILL.md)(810 미규정 사항) | [810-2], [810-5.6], [810-5.7] |
| 4 | 지하철 구분지상권 설정을 위한 지하 사용 보상 | 평가 수행 | F1=사용 토지 | [overlay-compensation-land-use](../../overlays/compensation/overlay-compensation-land-use/SKILL.md) > [overlay-compensation-land-acquisition](../../overlays/compensation/overlay-compensation-land-acquisition/SKILL.md)(토지가액 [810-5.6]) | [820-5.2.1-2], [820-5.2.2.1] |
| 5 | 공익사업으로 음식점 휴업 — 영업손실 | 평가 수행 | F1=영업손실 | [overlay-compensation-business-loss](../../overlays/compensation/overlay-compensation-business-loss/SKILL.md) > foundations | [840-2], [840-6.1], [840-6.3] |
| 6 | 재개발 조합의 종전자산 평가 | 평가 수행 | F2=도시정비, F3=토지·건물 | [overlay-urban-redevelopment](../../overlays/purpose/overlay-urban-redevelopment/SKILL.md) > asset-land / asset-building / asset-condominium | [730-1-①], [730-3.1] |
| 7 | 상장사 투자부동산 공정가치 (K-IFRS) | 평가 수행 | F2=재무보고, F4=공정가치 | [overlay-financial-reporting](../../overlays/purpose/overlay-financial-reporting/SKILL.md) > 해당 asset | [740-1-①], [740-3], [610-1.5.1-③-1] |
| 8 | 공장 저당을 위한 공장재단 평가 | 평가 수행 | F2=담보, F3=공장재단 | overlay-collateral > [asset-factory-foundation](../../assets/industrial/asset-factory-foundation/SKILL.md) → 준용: asset-land, asset-building, [asset-machinery](../../assets/industrial/asset-machinery/SKILL.md), asset-goodwill, asset-intellectual-property | [620-1.3.1], [620-1.3.2]~[620-1.3.6] |
| 9 | 상가 임차인 권리금 감정평가 (소송) | 평가 수행 | F2=없음, F3=권리금 | [asset-key-money](../../assets/income-and-loss/asset-key-money/SKILL.md) > foundations | [670-4.3.1] |
| 10 | 비상장 주식 가치 | 평가 수행 | F3=비상장주식 | [asset-stock](../../assets/intangibles/asset-stock/SKILL.md) → [asset-enterprise-value](../../assets/intangibles/asset-enterprise-value/SKILL.md) | [660-1.2.3-①·②], [660-3] |
| 11 | 공익사업 편입 건물(지장물) 보상 | 평가 수행 | F1=지장물 | 실무기준에 절 없음 → "실무기준 밖 — 관계법규 확인 필요" + 일반 규정 [asset-building](../../assets/real-estate/asset-building/SKILL.md) 참고 | [800] 구성(810~840) |
| 12 | "맹지는 어떻게 평가하나?" | 조항 질의 | — | [lookup-clause](../lookup-clause/SKILL.md) → terms.md → asset-land | [610-1.7.12] |
| 13 | "보상평가의 기준시점은?" | 조항 질의 | 맥락=보상 | lookup-clause → [810-5.7]; 일반 기준시점 [300-4]와 구분 | [810-5.7], [300-4] |
| 14 | 동료가 쓴 담보 감정평가서 심사 | 검토 | F2=담보 | [workflow-report-review](../workflow-report-review/SKILL.md) → 사례 1 스택 | [500-3], [500-4-②~④] |
| 15 | 감정평가사 친족 소유 토지의 시가 평가 의뢰 | 수임 판단 | — | [workflow-engagement-check](../workflow-engagement-check/SKILL.md) | [300-2], [200-4.2-②-1] |
| 16 | 지식산업센터 내 호실 (집합건물) 경매 | 평가 수행 | F2=경매, F3=구분소유 | overlay-auction > asset-condominium | [720-②], [610-3.1.3] |
| 17 | 신탁회사가 대출 담보로 임대 중인 오피스 빌딩(토지·건물 일체 거래) 평가 의뢰 | 평가 수행 | F2=담보, F3=복합부동산 | overlay-collateral > asset-land-building-composite (+asset-land, asset-building) > foundations. **asset-rent 아님**(임대수익은 수익방식 검토 자료) | [710-①·②], [610-3.2.3-①·②], [400-4-②], [610-1.5.1-③-4] |
| 18 | 도로사업 편입 토지 중 미지급용지와 미보상 송전선로 아래 토지 | 평가 수행 | F1=취득 토지 | overlay-compensation-land-acquisition > asset-land. **일반 고압선 감가 [610-1.7.13]를 먼저 적용하지 않음** | [810-6.2.3], [810-6.2.7-②] |
| 19 | 상장회사 재무보고 목적 기계기구류 감정평가서 검토 | 검토 | F2=재무보고, F3=기계기구류 | workflow-report-review → overlay-financial-reporting > asset-machinery. **asset-stock 아님**. 동료 검토와 법인 적정성 심사 [500-4-②]를 구분 | [740-2-②], [740-3], [630-1.3], [400-4-②·③] |
| 20 | 법원이 어선과 그 어업권을 함께 경매 | 평가 수행 | F2=경매, F3=선박+어업권 | overlay-auction > [asset-ship](../../assets/movables/asset-ship/SKILL.md) + [asset-fishery-right](../../assets/intangibles/asset-fishery-right/SKILL.md). **함께 의뢰 ≠ 자동 일괄**, 시설가액 중복 계상 확인 | [720-②], [400-2.3], [640-3.3], [650-2.3.2-①] |
| 21 | 재개발 구역에서 사업시행자의 토지 수용 보상 | 평가 수행 | F1=취득 토지, F2=도시정비 | overlay-urban-redevelopment ([730-3.5]) → overlay-compensation-land-acquisition > asset-land (특칙 연쇄) | [730-3.5], [810-2] |
| 22 | 송전선로 설치를 위한 구분지상권 설정(사실상 영구 사용) 보상 | 평가 수행 | F1=사용 토지 | overlay-compensation-land-use + overlay-compensation-land-acquisition [810-5.6] (특칙 간 참조) | [820-5.2.1-2], [810-5.6] |
| 23 | "공사중단 건축물은 어떤 방법으로 평가하나?" | 조항 질의 | — | lookup-clause → terms.md → [asset-suspended-construction](../../assets/real-estate/asset-suspended-construction/SKILL.md) → asset-building [610-2.4], 대지는 asset-land | [610-7.3.1] (원칙), [610-7.3.2] |
