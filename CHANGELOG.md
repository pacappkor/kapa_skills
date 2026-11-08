# 변경 이력 (CHANGELOG)

이 저장소의 모든 주요 변경을 기록한다.
- 형식: [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)
- 버전: [유의적 버전](https://semver.org/lang/ko/)
- 버전 규칙과 릴리스 절차: [docs/RELEASING.md](docs/RELEASING.md)

새 변경은 먼저 `[Unreleased]` 에 쌓는다. 릴리스할 때 버전 제목으로 옮긴다.
개정을 반영할 때는 `docs/RELEASING.md` 의 템플릿을 복사해 쓴다. 실무기준은 "개정 반영 항목 템플릿", 관계법령은 "관계법령 갱신 항목 템플릿"이다.

## [Unreleased]

### 관계법령 갱신 — 미시행 개정 사전 검토 (2026-11-09)

- 확인: 실무기준 `admRulSeq=2100000229230`·현행 법령 모두 변동 없음. 연혁 검사 `documents: 169; changed: 0; failures: 0`, 추가 제목 조회 0회. 기존 미시행 목록 151행은 이미 기록되어 있었다.
- 현행 판본·요약·배정표·별표 가공본·색인은 유지한다. 아래는 시행 시점의 후속 작업표이지 현행 해설이 아니다. 지정된 9개 미시행 본문을 `versions/<level>/<lsiSeq>-<efYd>.json`에 보존했다. 각 응답의 순번과 시행일을 검증했으며 부칙을 함께 저장했다.
- 현행 본문 변경표(`diff_laws.py --markdown`): 변경 없음(처리할 행 0개). 아래 표는 별도로 확인한 미래 본문과 현행 본문의 내용 차이다. 공백·링크 경계·개정 표시만의 차이는 내용 변경에서 제외한다. 미래 본문은 앞선 단계 시행 내용을 누적하므로 이를 해당 공포번호만의 개정으로 오인하지 않는다.

| 법령 | 현행 lsiSeq / 시행일 | 검토 lsiSeq / 시행일 / 공포번호 | 처리 |
|---|---|---|---|
| 토지보상법 | 289333 / 2026-09-08 | 286797 / 2026-12-17, 2027-06-17, 2027-09-09 / 21810 | 단계 시행 본문·부칙·별표 확인, 현행 유지 |
| 국토계획법 | 284013 / 2026-07-01 | 286981 / 2026-12-17 / 21812 | 구분지상권 등 사전 검토 |
| 국토계획법 | 동일 | 285937 / 2027-05-13 / 21626 | 임도 근거법 교체 사전 검토 |
| 국토계획법 | 동일 | 286805 / 2027-06-17 / 21796 | 농어촌 빈집 사업 특례 사전 검토 |
| 도시정비법 | 284065 / 2026-07-01 | 289341 / 2027-09-09 / 21901 | 기금 용도 인용 분리 사전 검토 |
| 도시정비법 시행령 | 287285 / 2026-07-01 | 267119 / 2028-01-01 / 35083 | 별표 4 인력 요건 사전 검토 |
| 도시정비법 시행규칙 | 283327 / 2026-02-11 | 269615 / 2028-01-01 / 01461 | 등록정보 입력·자료 범위 사전 검토 |

#### 토지보상법 제21810호 — 단계 시행

공식 본문: [2026-12-17](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=286797&efYd=20261217), [2027-06-17](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=286797&efYd=20270617), [2027-09-09](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=286797&efYd=20270909).

| 조문·별표 | 확인한 변경·정확한 원문 인용 | 영향 스킬·시행 시 처리 |
|---|---|---|
| 법 제89조의2제1항·제2항·제3항·제4항 신설(2026-12-17) | 제1항: “1천만원 이하의 이행강제금을 부과할 수 있다.” 제2항: “이행강제금이 부과될 수 있음을 통지하여야 한다.” 제3항: “1년에 2회 이내의 범위에서” 반복 부과·징수할 수 있다. 제4항: “이행강제금의 부과ㆍ징수에 관하여는 「행정기본법」 제31조제2항부터 제6항까지에 따른다”(준용이 아닌 인용 규정에 따른 직접 적용) | `lca-objection-litigation`의 법 제83조–제90조 범위에 신설 조문 반영·요약 작성. 법 제43조 인도·이전 의무를 맡은 `lca-expropriation-effects`, `workflow-compensation-chain`도 대조. 벌칙의 자동 강화나 평가액 산정 변경으로 해석하지 않는다 |
| 부칙 제1조·제2조 | “제89조의2의 개정규정은 공포 후 6개월이 경과한 날부터 시행하고, 별표 제2호(8) 및 (38)의 개정규정은 2027년 9월 9일부터 시행한다”. 제2조: “같은 개정규정 시행 이후 수용 또는 사용의 개시일이 도래하는 분부터 적용한다.” | 단순 처분일·계약일이 아니라 수용·사용 개시일을 확인. 현행에 소급 적용하지 않음 |
| 별표 제2호(98) 신설(2027-06-17) | “「농어촌 빈집 정비 및 관리에 관한 특별법」에 따른 빈집정비사업” | `lca-general` 별표 가공본, `pwa-urban-housing-regional`·C층 근거법 선정표와 사업인정 의제 연결 재검토 |
| 별표 제2호(8)·(38) 변경(2027-09-09) | (8): “「빈 건축물 정비 및 지원에 관한 특별법」 제23조에 따라 빈 건축물을 수용하거나 사용할 수 있는 사업”. (38): “「소규모주택정비에 관한 특례법」 제35조의2에 따라 토지등을 수용하거나 사용할 수 있는 사업” | `lca-general`, `pwa-urban-housing-regional`의 종전 공사중단 건축물·빈집/소규모주택 근거법 대응을 변경. 시행 시 C층 스캔·선정표 재수집, 별표 재가공 필요 |

별표 PDF 대조: [현행/2026-12-17 flSeq 168912195](https://www.law.go.kr/LSW/flDownload.do?flSeq=168912195&bylClsCd=110201), [2027-06-17 flSeq 168912499](https://www.law.go.kr/LSW/flDownload.do?flSeq=168912499&bylClsCd=110201), [2027-09-09 flSeq 169053255](https://www.law.go.kr/LSW/flDownload.do?flSeq=169053255&bylClsCd=110201). 12월 단계는 현행과 같은 별표 파일이고, 6월에는 (98), 9월에는 (8)·(38)이 달라진다. 미래 별표를 현행 가공본으로 대체하지 않았다.

#### 국토계획법 — 세 시행 단계

| 판본·공식 본문 | 조문·원문 인용 | 영향·처리 |
|---|---|---|
| [286981 / 2026-12-17 / 제21812호](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=286981&efYd=20261217) | 신설 법 제43조의2제1항 “구분지상권을 설정하거나 이전하여야 한다.” 제2항은 구분지상권 설정·이전 내용의 수용·사용 재결을 받은 경우 「부동산등기법」 제99조를 **준용**하여 “단독으로 그 구분지상권의 설정등기 또는 이전등기를 신청할 수 있다.” 제3항 등기절차는 대법원규칙, 제4항 존속기간은 “도시ㆍ군계획시설이 존속하는 날까지로 한다.” | `nlp-planning-facilities`에 신설 조문 요약 필요. `nlp-facility-project`, `lca-rights-compensation`, `lca-land-compensation`, 보상평가의 공간 사용·권리 확인과 연결 대조. 등기 의무·신청 가능을 혼동하지 않음 |
| 동일 | 신설 법 제65조제10항 “무상귀속이 되는 공공시설의 인정기준 등에 필요한 사항은 대통령령으로 정한다.” | `nlp-development-permit` 공공시설 귀속 요약·확인사항에 위임 근거 추가, 시행령 제정 내용을 재확인 |
| 동일 | 법 제92조제1항제9호 “같은 법 제52조에 따른 도로와 다른 시설의 연결허가” 추가 | `nlp-facility-project` 실시계획 인허가 의제 범위 보완. 일반 개발허가와 의제 요건을 혼동하지 않음 |
| 동일 부칙 제1조·제2조 | 시행 “공포 후 6개월이 경과한 날”. 적용례 “이 법 시행 이후 도시ㆍ군계획시설사업의 시행자가 구분지상권의 등기를 신청하는 경우(이 법에 따라 구분지상권에 관한 수용ㆍ사용의 재결을 받았으나 등기를 마치지 못한 경우를 포함한다)부터 적용한다.” | 재결일만으로 제외하지 말고 등기 신청일·미등기 상태 확인 |
| [285937 / 2027-05-13 / 제21626호](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=285937&efYd=20270513) | 법 제56조제3항의 임도 설치 근거를 “「산림자원의 조성 및 관리에 관한 법률」”에서 “「임도의 설치 및 관리에 관한 법률」”로 교체. 해당 법 부칙 제7조제1항에 같은 개정문 명시. 부칙 제1조 “공포 후 1년이 경과한 날부터 시행한다.” | `nlp-development-permit`의 도시지역·계획관리지역 산림 임도 예외 근거법 교체. 앞선 43의2·65·92 변경도 누적된 판본임 |
| [286805 / 2027-06-17 / 제21796호](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=286805&efYd=20270617) | 법 제58조제1항제1호 단서에 “및 「농어촌 빈집 정비 및 관리에 관한 특별법」 제2조제3호에 따른 빈집정비사업”, 법 제59조제2항제6호에 “과 「농어촌 빈집 정비 및 관리에 관한 특별법」 제2조제3호에 따른 빈집정비사업” 추가 | `nlp-development-permit` 개발행위 규모 제한·도시계획위원회 심의 예외 대상 보완. 각각 대통령령으로 정하는 범위 확인 필요. 해당 특별법 부칙 제3조제3항 개정문, 제1조 “공포 후 1년이 경과한 날부터 시행한다.” 확인. 앞선 단계 변경은 중복 개정으로 세지 않음 |

#### 도시정비법·시행령·시행규칙

| 판본·공식 본문 | 변경 조문·부칙·정확한 인용 | 영향·처리 |
|---|---|---|
| [법 289341 / 2027-09-09 / 제21901호](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=289341&efYd=20270909) | 법 제126조제3항제7호: “「빈 건축물 정비 및 지원에 관한 특별법」 제31조에 따른 빈 건축물 정비사업에 대한 지원 및 「소규모주택정비에 관한 특례법」 제44조에 따른 소규모주택정비사업에 대한 지원”. 특별법 부칙 제6조제10항의 개정문과 일치. 부칙 제1조 “공포 후 1년이 경과한 날부터 시행한다.” | `ura-misc` 도시·주거환경정비기금 용도에 인용 법률·사업 분리 반영. 기존 빈집/소규모 사업의 지원 근거를 한 법률로 취급하지 않음. 정비사업 평가방법 자체 변경은 확인되지 않음 |
| [영 267119 / 2028-01-01 / 제35083호](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=267119&efYd=20280101) | 본문 내용 차이 없음. 별표 4 제2호가목1)나): “정비사업전문관리업에 10년 이상 근무한 사람으로서 국토교통부장관이 정하여 고시하는 경력ㆍ실적 및 교육이수 기준을 충족하는 자”, 4)나): “정비사업전문관리업에 3년 이상 근무한 사람으로서 국토교통부장관이 정하여 고시하는 경력ㆍ실적 및 교육이수 기준을 충족하는 자” 추가·재편. 종전 4)라)의 2003-07-01 당시 업체 근무·실적 경로는 미래 별표에서 없어짐 | `ura-management-consulting-business` 인력 분류·자격 요건 재작성, 고시 확인. 자본금·5인 기준·협약 특례를 이번에 새로 바뀐 것으로 설명하지 않음 |
| 동일 부칙 | 제1조제2호 “별표 4 제2호가목의 개정규정: 2028년 1월 1일”. 제2조 정비계획 변경 적용례·제3조 임대주택 인수계약 적용례는 이미 시행된 다른 개정 부분에 관한 것 | 미래 별표 적용 시점과 이미 시행된 본문을 구분. [미래 별표 PDF flSeq 166145111](https://www.law.go.kr/LSW/flDownload.do?flSeq=166145111&bylClsCd=110201) 2쪽 이미지 대조. 현행 가공본 유지 |
| [규칙 269615 / 2028-01-01 / 제1461호](https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=269615&efYd=20280101) | 신설 제18조제4항 “시ㆍ도지사는 제3항에 따라 정비사업전문관리업자 등록부에 기재하는 사항을 법 제108조에 따른 정비사업전문관리업 정보종합체계에 입력해야 한다.” 제20조제1항제5호 “보유 기술인력의 수, 기술인력별 자격ㆍ경력ㆍ실적 및 교육이수에 관한 현황”으로 확대 | `ura-management-consulting-business` 등록 절차의 입력 의무·요청 자료 범위 갱신. 제20조제1항 본문의 “제출을 요청할 수 있다”는 재량 표현 유지 |
| 동일 부칙 | “이 규칙은 2025년 3월 18일부터 시행한다. 다만, 제18조제4항 및 제20조제1항제5호의 개정규정은 2028년 1월 1일부터 시행한다.” | 2025년 일반 시행일을 두 조항의 시행일로 오인하지 않음. 두 개정에 별도 소급 적용례는 해당 부칙에서 확인되지 않음 |

#### 들어오는 연결 검토 범위

현재 `docs/graph.json`의 목적지 스킬별 전체 들어오는 연결을 대조했다. 아래는 **재검토 후보** 목록이며, 각 링크가 곧 개정 조문을 직접 인용한다는 뜻은 아니다. 신설 제89조의2·제43조의2에는 아직 직접 들어오는 조문 링크가 없으므로 배정 범위의 기존 스킬 및 인접 의무를 기준으로 검토했다. 스킬 간 링크와 실제 조문 인용은 시행일에 재생성해 다시 판별한다. 현행 문구를 미래 규정으로 바꿀 사유는 없었다.

| 변경 조문 소유/인접 스킬 | 현재 들어오는 연결의 출발 스킬(누락 없이) | 검토 결과 |
|---|---|---|
| `lca-objection-litigation` | nlp-misc, pwa-agri-ocean-culture, pwa-defense-public-special, pwa-environment-disaster, pwa-urban-housing-regional, pwa-water | 기존 이의·소송/준용 링크에 신설 이행강제금이 자동 적용된다고 단정하지 않음 |
| `lca-expropriation-effects` | lca-general, lca-objection-litigation, lca-penalties, pwa-environment-disaster, pwa-urban-housing-regional, ura-implementation-measures | 제43조 의무 자체는 바뀌지 않음. 의무 불이행에 대한 새로운 행정상 수단을 시행일·적용례와 구분 |
| `lca-general` | lca-expropriation-committee, lca-expropriation-procedure, lca-relocation, lca-repurchase-right, nlp-planning-facilities, pwa-agri-ocean-culture, pwa-defense-public-special, pwa-environment-disaster, pwa-industry-energy, pwa-transport, pwa-urban-housing-regional, pwa-water, ura-cost-sharing, ura-implementation-measures | 별표 근거법·사업인정 의제 사업 연결 중 빈집 관련 C층 재선정 필요. 다른 사업에 일괄 확대하지 않음 |
| `nlp-planning-facilities` | nlp-district-unit-plan, nlp-facility-project, nlp-management-plan-procedure, nlp-misc, nlp-penalties, pwa-industry-energy, pwa-urban-housing-regional, rel-building-housing, ura-implementation-measures, ura-implementation-plan | 입체적 시설 결정과 새 구분지상권 등기 의무·권한·존속기간 연결 점검 |
| `nlp-development-permit` | nlp-district-unit-plan, nlp-facility-project, nlp-management-plan-procedure, nlp-misc, nlp-penalties, nlp-planning-committee, nlp-planning-facilities, nlp-spatial-restructuring-plan, nlp-zoning-restrictions, pwa-agri-ocean-culture, pwa-defense-public-special, pwa-environment-disaster, pwa-industry-energy, pwa-urban-housing-regional, rel-tax-statistics-misc, ura-basic-plan-zone-designation | 허가/심의 예외와 공공시설 무상귀속을 구별, 임도·빈집 사업 및 하위 규정 범위만 후속 대조 |
| `nlp-facility-project` | nlp-development-permit, nlp-misc, nlp-planning-facilities, pwa-agri-ocean-culture, pwa-defense-public-special, pwa-environment-disaster, pwa-industry-energy, rel-tax-statistics-misc, ura-implementation-plan | 제92조 의제는 실시계획 및 협의를 전제로 함. 별도 허가 전반 면제라고 확대하지 않음 |
| `ura-misc` | ura-management-consulting-business, ura-management-disposal-plan, ura-penalties, ura-supervision | 기금 용도 인용 교체와 무관한 규정은 요약 영향 없음 |
| `ura-management-consulting-business` | ura-association, ura-misc, ura-penalties, ura-supervision | 전문관리업 인력·등록정보 관련 연결 대조. 조합/평가 업무 전체의 자격이 바뀐다고 확대하지 않음 |

법령 작업 절차 `workflow-compensation-chain`, 실무기준 보상평가 overlays의 인도·공간사용, `overlay-urban-redevelopment`의 기금/관리업 전제를 대조할 대상으로 식별했다. 이번 개정에서 평가액 산정 산식·평가 방법을 바꾸는 직접 문구는 확인되지 않았다. 이 검토는 상세 미래 규정을 실무기준 요약에 선반영하지 않는다.

#### 시행일 도래 시 후속 확인

- [ ] 2026-12-17: 토지보상법 제89조의2와 적용례, 국토계획법 제43조의2·제65조제10항·제92조제1항제9호 및 하위 규정 재확인 후 현행 수집·배정·요약 갱신.
- [ ] 2027-05-13: 국토계획법 제56조제3항 근거법·관련 B/C층 인용 점검.
- [ ] 2027-06-17: 토지보상법 별표 제2호(98)·국토계획법 제58조/제59조, C층 근거법 스캔·선정표·별표 가공본 갱신.
- [ ] 2027-09-09: 토지보상법 별표 제2호(8)/(38), 도시정비법 제126조제3항제7호의 법률명·특례 연결 갱신.
- [ ] 2028-01-01: 도시정비법 시행령 별표 4·시행규칙 제18조/제20조와 관련 경력·실적·교육 고시 재확인.
- 검증: 고정 순서 재생성 완료(현행 생성물 변경 0), `build_index --check`·`split_standard --check`·`build_laws --check`·`graph --check` 통과, `validate.py` errors 0, 단위 테스트 27개 통과(부칙 추출 회귀 테스트 4개 포함). 현행 스킬 내용 변경이 아닌 사전 검토·판본 보존 기록이다.
- 아직 공포되지 않았거나 이 검토에 포함되지 않은 후속 시행령·고시의 세부 기준은 확정하지 않는다. 나머지 기존 미시행 142행은 이번 지정 9판본 상세 검토 범위 밖이다. 이 기록만으로 전체 미시행 개정의 영향 검토가 완료되었다고 보지 않는다.

### 수정
- PR #7 검토 반영: 부칙은 `arDivArea` 내부의 법문 문단만 HTML 파서로 추출하여 속성 속 JavaScript·페이지 버튼·별표 다운로드 UI를 제외한다. 지정 미시행 9판본과 같은 오염이 있던 과거 시행규칙 `86824-20080418`을 재수집했다. 순번·시행일 일치 및 `addenda` 외 필드 불변을 확인했다. 현행 JSON 169개에는 저장된 `addenda` 필드가 없어 재수집하지 않았다. 토지보상법 제89조의2제4항의 “준용”을 “따른다”에 맞게 정정하고, 국토계획법 제43조의2제2항의 실제 준용 근거·재결 요건을 명시했다.
- 법령 연혁 수집·검사에서 동일한 판본·공포 메타데이터의 저장된 완전한 법령명을 재사용한다. 새 행·메타데이터 변경·불완전한 이름만 공식 본문으로 확인하여 중복 요청을 줄이고, 실제 이름 확인 요청 수를 출력한다. 변경 감지·단계 시행일·상태 재계산은 유지한다.
- PR #4 5차 검토 반영: 폐지제정을 실제 폐지와 구별하고, Markdown 원시 HTML 블록 전체를 본문 검사에서 제외한다. 현행 법령 수집도 요청 시행일과 본문 응답을 대조한다.
- PR #4 4차 검토 반영: 본문 응답의 단계 시행일·현행 연혁과 manifest 일치를 검증한다. 시행된 폐지는 별도 상태로 두고 날짜 조회에서 배제한다. 연혁만 바뀐 경우도 갱신·검토하며, Markdown 들여쓴 코드·HTML 블록 경계·이스케이프 백틱 처리를 보완했다.
- PR #4 3차 검토 반영: 현행 연혁 검증은 순번·시행일을 함께 대조하고, 생략된 법령명은 판본별 전체 이름을 확인한 뒤 분류한다. Markdown 코드 span 은 문단·새 블록 경계를 넘지 않는다.
- PR #4 재검토 반영: 닫히지 않은 backtick 을 본문으로 검사하고, 이름이 바뀌는 미시행 개정도 예정 판본으로 분류한다. 연혁 기준일과 수집일은 한국 시간(UTC+9)을 쓴다.
- PR #4 검토 반영: 과거 본문을 lsiSeq·시행일 복합 키로 저장하고 중복 순번 선택에 시행일을 요구한다. 부칙을 보존하고 샘플을 재수집했다. 기존 미시행 연혁은 검사 실패 대신 정보로 알리며, 인라인 backtick 코드가 뒤의 본문 검사를 가리지 않도록 수정했다.

### 추가
- 법령ID(`lsId`), 연혁 판본 목록(`fetch_versions.py`), 날짜·판본별 과거 본문 수집(`fetch_version.py`), 결정적 법령·조문·실무기준 색인(`build_index.py`, `docs/law-index.json`). 색인 최신 검사를 전체 검증에 포함한다.
- Markdown 본문 물결표 검사와 범위 en dash 표기. 원문 `source.md` 및 원문 과수 이식시기 별표의 물결표는 보존한다(코드도 검사 제외).
- `laws/` 관계법령 컬렉션 (국가법령정보센터 현행 법령, 2026-11-08 수집)
  - A층(법·시행령·시행규칙 전 조문 + 별표 + 주제별 요약):
    - 토지보상법 16주제
    - 감정평가법·감정평가에 관한 규칙 12주제
    - 부동산공시법 6주제
    - 국토계획법 19주제
    - 도시정비법 15주제
  - B층 `related-provisions`: 실무기준·토지보상법 시행규칙 제5장이 조문 번호로 인용한 다른 법령 38개 문서의 해당 조항 5주제
    - 인용 문맥표 포함
    - 개정 전 번호 인용(수산업법·외부감사법·항공법)은 현행 대응 조문을 함께 수록
  - 입구 `00-laws-start`, 갱신 절차는 저장소 규칙 `rules/` 로 분리(아래 "변경"), 저장소 입구 `00-kapa-start`
- 별표 가공본 `sources/laws/<컬렉션>/annex-md/` 55건(원본 PDF 120쪽)
  - 대상: 토지보상법 7, 감정평가법 시행령 4, 국토계획법 시행령·시행규칙 33, 도시정비법 시행령 8, 관련 조항 3(산림자원법 시행규칙 별표 3, 수산업법 시행령 별표 4·10)
  - 에이전트가 원본 PDF 의 모든 페이지 이미지를 보고 표·목록으로 가공했다. 수치·항목은 원문 그대로이고, 원문 오기는 `[원문 그대로]` 로 표시했다.
  - PDF 페이지 순서가 본문과 다른 별표(국토계획법 시행령 별표 16·17·19·20·24)는 항목 번호로 순서를 복원했다.
  - `source.md` 에 가공본과 원본 PDF·HWP 링크를 함께 싣는다.
  - `build_laws.py --check` 는 다음 경우를 오류로 알린다: 가공본 없음, 미검증, 원본 파일 번호(`pdf_flseq`)가 현행 별표와 다름(개정).
  - 관련 주제 요약을 가공본과 대조해 고치고, PDF 추출 주의 문구를 없앴다. 예: 국토계획법 건축제한 세부 요건, 수산업법 시행령 별표 10 어선 내용연수·잔존가치율, 구 별표 4 인용과의 대응.
- `tools/laws/annex_prep.py`: 별표 원본 PDF 를 페이지 이미지로 렌더링하고 가공 작업 목록 생성
- `tools/fetch_standard.py --check`: 국가법령정보센터의 현행 「감정평가 실무기준」 고시가 저장소 판본과 같은지 확인
- 도구 `tools/laws/`
  - `fetch_laws.py`: 수집. `--check` 로 최신 판본 비교
  - `diff_laws.py`: 조문 단위 변경 목록
  - `build_laws.py`: 생성. `--check`·`--status`·`--coverage` 로 조문 배정과 요약의 조문 인용 누락 검사
  - `draft_topics.py`: 배정표 초안
  - `lawindex.py`: 조문 → 스킬 색인
  - `image_text.json`: 본문 산식 이미지 전사
- C층 `laws/public-works-acts`
  - 범위: 토지보상법 별표의 공익사업 근거법 115개(A층 제외)
  - 내용: 토지보상법을 언급하는 조문 258개, 7개 분야 주제
  - 색인: 법률별 색인, 특례 색인(사업인정 의제·재결신청 기간·준용)
- 양방향 연결
  - `tools/graph.py` 가 모든 스킬에 "들어오는 연결"을 생성한다(조문 단위 표기, `docs/graph.json`)
  - 법령 간 절차 `laws/workflow-compensation-chain` 과 회귀 사례 `cases.md`
- 개정 전 번호 인용 대응표 `tools/laws/stale_citations.json`
- 실무기준 스킬의 "참조 관계"에 원문이 인용한 관계법령 조문 링크를 자동 생성. 연속 인용과 "같은 법"을 해석하고, 개정 전 번호는 현행 조문으로 연결한다
- `tools/fix_links.py`: 스킬 이름 기준 링크 재계산

### 변경
- 저장소 규칙을 `rules/` 의 두 스킬로 분리했다. `rules/` 에는 이 두 스킬만 둔다.
  - `skill-reading-rules`: 스킬을 읽고 답하는 규칙. 읽는 순서, 원문 확인, 인용 형식, 우선순위, 판본, 생성 블록·별표 가공본의 의미. 파일을 바꾸지 않는다.
  - `skill-update-maintenance`: 실무기준 또는 관계법령 개정에 따른 갱신 절차. 어느 쪽 지시든 둘 다 확인하고, 실무기준·법령 트랙을 거쳐 재생성·검증·기록한다.
  - 입구 스킬·AGENTS·CLAUDE 에 흩어져 있던 읽기 규칙은 `skill-reading-rules` 로 모았다.
  - `docs/RELEASING.md` 의 실무기준 개정 절차는 `skill-update-maintenance` 로 옮겼다. RELEASING 에는 버전·기록 규칙만 남겼다.
  - `tools/validate.py` 가 분리를 검사한다. 다음 경우는 오류다.
    - 갱신 스킬 밖의 스킬 폴더 파일에 도구 명령·갱신 절차가 있음
    - 읽기 규칙에 갱신 작업 용어가 있음
    - 갱신 스킬에 읽기 규칙 절이 있음
    - 입구·AGENTS·CLAUDE 가 읽기 규칙을 가리키지 않음
  - 생성 블록과 `source.md` 머리말에서 도구 경로 언급을 뺐다.
- 실무기준만 전제하던 운영 규칙·도구를 관계법령 개정까지 다루도록 고쳤다.
  - 이슈 템플릿:
    - "실무기준 개정 반영"(`standard-update`)과 "관계법령 개정 반영"(`law-update`, 새 라벨)으로 나눴다.
    - 둘 다 1단계에서 양쪽 확인을 요구한다.
    - "내용 오류 보고"(`source-check`) 템플릿을 추가했다.
  - PR 템플릿: 관계법령 개정 반영 항목, `build_laws.py --check` 확인을 추가했다.
  - `docs/RELEASING.md`:
    - 버전 규칙에 관계법령 내용 변경(MINOR)과 개정 표시만 변경(PATCH)을 넣었다.
    - "관계법령 갱신 항목 템플릿"을 추가했다.
  - AGENTS·README·NOTICE: 원문 생성기·이름 규칙·새 컬렉션 위치·버전·라벨·면책을 실무기준과 관계법령 모두에 맞게 고쳤다. 상주 입구를 `00-kapa-start` 로 바꿨다.
  - `tools/fetch_standard.py`: 인자가 없으면 고정 판본 대신 저장소 판본(`split_standard.SEQ`)을 받는다.
- `workflow-appraisal` 우선순위 ①(관계법규)과 지장물·농업손실·이주대책 등 실무기준에 절이 없는 보상 항목을 토지보상법 스킬로 연결
- 생성기들의 링크를 최단 상대경로로 통일(`fix_links.py` 와 충돌 방지)
- `validate.py`: 법령 컬렉션 검사 포함

<!--
### 근거 고시          ← 실무기준 개정 반영일 때만
### 실무기준 개정 반영  ← 조항별 표 (docs/RELEASING.md 템플릿)
### 관계법령 갱신      ← 관계법령 개정 반영일 때만: 판본 변화 + diff 표 + 행별 처리
### 추가
### 변경
### 정정
### 삭제
### 호환성 깨짐        ← 스킬 경로·이름 변경/삭제 등 @skills 주소가 바뀌는 변경
-->

## [v0.0.0] - 2026-11-07

최초 릴리스. PR #1.

### 근거 고시
- 「감정평가 실무기준」 국토교통부고시 제2023-522호 (2023. 9. 13. 일부개정, 시행 2023. 9. 13.)
- 국가법령정보센터 admRulSeq=2100000229230

### 추가
- `appraisal-practice-standards` 컬렉션
  - 입구: `00-practice-standards-start`
  - 작업 절차 4개: `workflow-appraisal`, `lookup-clause`, `workflow-report-review`, `workflow-engagement-check`
  - 내용 스킬 41개: `foundations/` 5, `assets/` 27, `overlays/` 9. 원문 [100]–[900]·부칙 전 조항을 빠짐없이 배정했다
- 내용 스킬 구성
  - `SKILL.md`: 요약, 적용 시 확인사항, 함께 읽을 스킬
  - 자동 생성 블록: 조항 목차, 참조 관계
  - `source.md`: 원문 전문
- 찾기 도구
  - 용어·조항 색인 `terms.md`: 원문 정의·조항 제목·검증된 별칭 31개
  - 조회표 `facets.md`
  - 라우팅 사례 `cases.md`: 23개
- 원문 산식 이미지 3개의 전사와 원본 gif: [810-6.2.7], [820-5.2.2.1], [840-5.2-③]
- 도구
  - `tools/fetch_standard.py`: 원문 수집
  - `tools/split_standard.py`: 조항 분할·생성, `--check`
  - `tools/fix_links.py`: 링크 재계산
  - `tools/validate.py`: 구조 검증
- 문서
  - README, AGENTS, CLAUDE
  - NOTICE: GPL-3.0-only, 원문은 「저작권법」 제7조 비보호 저작물
  - `docs/ROUTING.md`: 진입 방식 비교, 폴더 구조 근거, 독립 에이전트 검토 결과

[Unreleased]: https://github.com/pacappkor/kapa_skills/compare/v0.0.0...HEAD
[v0.0.0]: https://github.com/pacappkor/kapa_skills/releases/tag/v0.0.0
