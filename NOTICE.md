# 라이선스와 출처

## 이 저장소의 라이선스: GNU GPL v3.0

이 저장소는 [GNU General Public License v3.0](LICENSE)(GPL-3.0-only)으로 배포한다.
다음 자료는 편집·창작물로서 저작권 보호를 받을 수 있으므로 GPL 의 적용을 받는다.

- 스킬 묶음의 구성: 분류 체계, 폴더·스킬 이름, 조항 배정
- `SKILL.md` 의 요약·확인사항·함께 읽을 스킬
- `00-practice-standards-start`
- 문서(README·AGENTS 등)
- `tools/` 의 코드

이 저장소를 복제·수정해 배포하려면 GPL v3.0 조건을 따른다. 수정본에도 같은 라이선스를 적용하고, 소스를 공개하며, 이 고지를 유지해야 한다.

```text
kapa_skills — 감정평가 업무용 에이전트 스킬
Copyright (C) 2026 pacappkor

This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, version 3.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
License for more details. You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
```

## 원문 (저작권 보호 대상 아님)

- 「감정평가 실무기준」 국토교통부고시 제2023-522호 (2023. 9. 13. 일부개정, 시행 2023. 9. 13.), 소관: 국토교통부(부동산평가과)
- 출처: 국가법령정보센터 <https://www.law.go.kr/LSW/admRulInfoP.do?admRulSeq=2100000229230>
- 수집: `tools/fetch_standard.py` (2026-11-07)
- 위치: `sources/appraisal-practice-standards/`, 각 스킬의 `source.md`

국가·지방자치단체의 고시·훈령은 「저작권법」 제7조제1호에 따라 이 법에 의한 보호를 받지 못한다.
따라서 원문 텍스트 자체는 GPL 과 관계없이 누구나 이용할 수 있다. GPL 은 이 저장소가 더한 구성과 창작 부분에 적용된다.

원문 처리 내역:
- 내용은 바꾸지 않았다.
- 줄 단위 텍스트로 변환했다.
- 조항 단위로 나눴다.
- 본문에 이미지로 실린 산식 3개를 전사했다. 원본 이미지도 함께 둔다.
- 장 번호 뒤에 마침표가 붙은 제목 하나(`5. 자동가치산정모형 사용 윤리`)는 조항 번호 체계에 맞춰 `[200-5]` 로 표기했다.

## 면책

`SKILL.md` 의 요약·확인사항과 `00-practice-standards-start` 는 원문을 찾아 읽기 위한 보조 자료다. 원문과 다르면 원문이 우선한다.
관계법규(감정평가법·감정평가에 관한 규칙, 토지보상법, 도정법 등)의 내용은 다루지 않는다. 법적 판단은 원문과 관계법규로 확인한다.
