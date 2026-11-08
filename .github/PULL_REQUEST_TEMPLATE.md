## 요약
<!-- 무엇을 왜 바꾸는가 -->

## 변경 종류 (버전 영향: docs/RELEASING.md)
- [ ] 실무기준 개정 반영 (MINOR) — 근거 고시: 국토교통부고시 제____-___호
- [ ] 관계법령 개정 반영 — 내용 변경 MINOR / 개정 표시만 PATCH — 법령·시행일:
- [ ] 스킬·작업 절차·컬렉션 추가 (MINOR)
- [ ] 스킬 경로·이름 변경/삭제 (호환성 깨짐 — 0.x 에서는 MINOR + `### 호환성 깨짐`)
- [ ] 요약·확인사항·별표 가공본 정정, 별칭·사례·문서·도구 수정 (PATCH)

## 확인
- [ ] `CHANGELOG.md` 의 `[Unreleased]` 에 항목을 추가했다
  - 실무기준 개정: 조항별 표(개정 반영 항목 템플릿) / 관계법령 개정: `### 관계법령 갱신`(판본 변화, diff 표, 행별 처리)
- [ ] 개정 반영이면 `rules/skill-update-maintenance` 1–6단계를 모두 수행했다 (`fetch_standard.py --check`·`fetch_laws.py --check` 둘 다)
- [ ] `python -I tools/split_standard.py --check` 통과
- [ ] `python -I tools/laws/build_laws.py --check` 통과 (`--status` 모든 주제 OK)
- [ ] `python -I tools/validate.py` → errors 0
- [ ] 요약을 바꾼 조항·조문은 `source.md` 원문(별표는 원본 PDF)과 대조했다
