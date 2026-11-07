---
name: 실무기준 개정 반영
about: 「감정평가 실무기준」이 개정되어 스킬을 갱신해야 할 때
title: "실무기준 개정 반영: 국토교통부고시 제____-___호"
labels: standard-update
---

## 개정 고시
- 고시 번호:
- 개정일 / 시행일:
- 국가법령정보센터 URL (admRulSeq):

## 개정 조항 (알고 있는 범위)
| 조항 | 신설/개정/삭제 | 요지 |
|---|---|---|

## 처리 체크리스트 (docs/RELEASING.md)
- [ ] 원문 수집 (`tools/fetch_standard.py`)
- [ ] `split_standard.py` 의 SEQ·NOTICE·배정표·IMAGE_TEXT·ALIASES 갱신
- [ ] 바뀐 조항 전수 확인 (`git diff --word-diff`)
- [ ] 영향 스킬 요약·확인사항 갱신
- [ ] 작업 절차·facets·cases 영향 확인
- [ ] `tools/validate.py` errors 0
- [ ] CHANGELOG 항목 작성 → PR → 병합 → 태그·릴리스
