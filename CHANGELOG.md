# 변경 이력 (CHANGELOG)

이 저장소의 모든 주요 변경을 기록한다.
- 형식: [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)
- 버전: [유의적 버전](https://semver.org/lang/ko/)
- 버전 규칙과 릴리스 절차: [docs/RELEASING.md](docs/RELEASING.md)

새 변경은 먼저 `[Unreleased]` 에 쌓는다. 릴리스할 때 버전 제목으로 옮긴다.
실무기준 개정을 반영할 때는 `docs/RELEASING.md` 의 "개정 반영 항목 템플릿"을 복사해 쓴다.

## [Unreleased]

<!--
### 근거 고시          ← 실무기준 개정 반영일 때만
### 실무기준 개정 반영  ← 조항별 표 (docs/RELEASING.md 템플릿)
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
  - 내용 스킬 41개: `foundations/` 5, `assets/` 27, `overlays/` 9. 원문 [100]~[900]·부칙 전 조항을 빠짐없이 배정했다
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
