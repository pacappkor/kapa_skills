---
name: 실무기준 개정 반영
about: 「감정평가 실무기준」(국토교통부고시)이 개정되어 스킬을 갱신해야 할 때
title: "실무기준 개정 반영: 국토교통부고시 제____-___호"
labels: standard-update
---

<!-- 처리 절차: rules/skill-update-maintenance/SKILL.md (1단계에서 관계법령도 함께 확인한다) -->

## 개정 고시
- 고시 번호:
- 개정일 / 시행일:
- 국가법령정보센터 URL (admRulSeq):

## 개정 조항 (알고 있는 범위)
| 조항 | 신설/개정/삭제 | 요지 |
|---|---|---|

## 처리 체크리스트 (skill-update-maintenance)
- [ ] 1. `tools/fetch_standard.py --check` 와 `tools/laws/fetch_laws.py --check` 를 둘 다 실행 (결과를 아래에 붙임)
- [ ] 3-S. 원문 수집, `split_standard.py` 의 SEQ·NOTICE·SKILLS·IMAGE_TEXT·ALIASES 갱신
- [ ] 3-S. 바뀐 조항 전수 확인 (`git diff --word-diff`) — 조항별 처리표 작성
- [ ] 3-S. 실무기준이 인용하는 법령 조문 변화 반영 (B층 배정 `related-provisions.json`, `stale_citations.json`)
- [ ] 3-S. 영향 스킬 요약·확인사항, 작업 절차·facets·cases, 그 조항을 인용하는 법령 스킬 확인
- [ ] (관계법령도 바뀌었으면) 3-L 수행
- [ ] 4. 재생성: build_laws → split_standard → graph --json → fix_links
- [ ] 5. 검증 전부 통과, `tools/validate.py` errors 0
- [ ] 6. CHANGELOG(개정 반영 항목 템플릿) → PR → 병합 → 태그·릴리스 (MINOR)

## 1단계 확인 결과
```text
```
