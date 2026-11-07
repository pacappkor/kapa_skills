## 요약
<!-- 무엇을 왜 바꾸는가 -->

## 변경 종류 (버전 영향: docs/RELEASING.md)
- [ ] 실무기준 개정 반영 (MINOR) — 근거 고시: 국토교통부고시 제____-___호
- [ ] 스킬·작업 절차·컬렉션 추가 (MINOR)
- [ ] 스킬 경로·이름 변경/삭제 (호환성 깨짐 — 0.x 에서는 MINOR + `### 호환성 깨짐`)
- [ ] 요약·확인사항 정정, 별칭·사례·문서·도구 수정 (PATCH)

## 확인
- [ ] `CHANGELOG.md` 의 `[Unreleased]` 에 항목을 추가했다 (개정 반영이면 조항별 표 포함)
- [ ] `python -I tools/split_standard.py --check` 통과
- [ ] `python -I tools/validate.py` → errors 0
- [ ] 요약을 바꾼 조항은 `source.md` 원문과 대조했다
