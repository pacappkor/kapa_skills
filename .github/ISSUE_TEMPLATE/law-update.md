---
name: 관계법령 개정 반영
about: 토지보상법·감정평가법·부동산공시법·국토계획법·도시정비법, 관련 조항(B층), 공익사업 근거법(C층)이 개정되어 스킬을 갱신해야 할 때
title: "관계법령 개정 반영: <법령명> (YYYY-MM-DD 기준)"
labels: law-update
---

<!-- 처리 절차: rules/skill-update-maintenance/SKILL.md (1단계에서 실무기준도 함께 확인한다) -->

## 개정 법령 (알고 있는 범위)
| 법령 (법/시행령/시행규칙) | 공포 번호 | 시행일 | 컬렉션 (A/B/C층) |
|---|---|---|---|

## 알고 있는 변경 조문·별표
| 조문·별표 | 신설/개정/삭제 | 요지 |
|---|---|---|

## 처리 체크리스트 (skill-update-maintenance)
- [ ] 1. `tools/fetch_standard.py --check` 와 `tools/laws/fetch_laws.py --check` 를 둘 다 실행 (결과를 아래에 붙임)
- [ ] 3-L. 바뀐 컬렉션 수집, `diff_laws.py --markdown` 변경 목록 — 모든 행 처리
- [ ] 3-L. `build_laws.py --check` 오류 해소: 미배정 조문 배정, 별표 주제, 별표 가공본 재가공(`annex_prep.py`, 모든 페이지 대조)
- [ ] 3-L. B층 인용 번호 변화(`stale_citations.json`, `00-rel-start`), C층 근거법 변화(`handoff_scan.py --fetch`)
- [ ] 3-L. 요약·확인사항 갱신(`--coverage` MISSING 없음), 바뀐 조문을 전제로 한 실무기준 스킬·cases 확인
- [ ] (실무기준도 바뀌었으면) 3-S 수행
- [ ] 4. 재생성: build_laws → split_standard → graph --json → fix_links
- [ ] 5. 검증 전부 통과, `tools/validate.py` errors 0
- [ ] 6. CHANGELOG `### 관계법령 갱신`(판본 변화 + diff 표 + 행별 처리) → PR → 병합 → 태그·릴리스 (내용 변경 MINOR / 개정 표시만 PATCH)

## 1단계 확인 결과
```text
```
