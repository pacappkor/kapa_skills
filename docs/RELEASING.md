# 버전 규칙과 릴리스 절차

## 버전 규칙 (vMAJOR.MINOR.PATCH)

| 올리는 자리 | 이런 변경일 때 | 예 |
|---|---|---|
| MAJOR | 스킬 경로·이름의 변경·삭제처럼 **@skills 주소나 스킬 이름에 의존하는 사용처가 깨지는** 변경. 작업 절차 출력 형식을 호환되지 않게 바꾸는 변경 | `assets/real-estate/asset-land` → 다른 경로 |
| MINOR | **실무기준 개정 반영**(근거 고시가 바뀜), 새 컬렉션·스킬·작업 절차 추가 | 국토교통부고시 제2023-522호 → 새 고시 |
| PATCH | 요약·확인사항 정정, 별칭·사례 추가, 문서·링크·도구 수정, 원문 변환 오류 수정(원문 내용은 그대로) | 요약의 의무/재량 표현 정정 |

- 1.0.0 전(0.x)에는 MAJOR 대신 MINOR 를 올린다. 이때 CHANGELOG 에 `### 호환성 깨짐` 절을 반드시 둔다.
- 근거 고시는 MINOR 단위로 기록한다. 같은 고시를 쓰는 동안은 PATCH 만 올라간다.
- 버전 태그는 해당 PR 이 `main` 에 병합된 커밋에 단다. 형식은 `v0.1.0` 처럼 `v` 접두어를 붙인다.

## 실무기준 개정 반영 절차

1. 국가법령정보센터에서 새 고시의 `admRulSeq`·`admRulId` 를 확인한다. 작업 브랜치(`standard/<고시번호>`)를 만든다.
2. `python -I tools/fetch_standard.py <admRulSeq> <admRulId>` 로 원문을 받는다.
3. `tools/split_standard.py` 의 `SEQ`·`NOTICE` 를 고친다.
   - 조항이 신설·삭제되면 배정표 `SKILLS` 를 고친다.
   - 산식 이미지가 바뀌면 `IMAGE_TEXT` 를 고친다.
   - 별칭 대상 조항이 바뀌면 `ALIASES` 를 고친다(생성기가 원문 대조로 알려 준다).
4. `python -I tools/split_standard.py` 를 실행한다. 이어서 다음으로 바뀐 조항을 모두 찾는다.
   - `git diff --word-diff -- appraisal-practice-standards/**/source.md`
   - 원문 텍스트 diff
5. 바뀐 조항마다 처리한다.
   - 해당 스킬의 요약·확인사항을 고친다.
   - 작업 절차(`workflow-appraisal` 우선순위·단계표, `facets.md`)와 `cases.md` 에 영향이 있는지 확인한다.
6. `python -I tools/validate.py` → errors 0
7. `CHANGELOG.md` 의 `[Unreleased]` 에 아래 템플릿으로 항목을 쓴다. PR 을 연다(라벨 `standard-update`).
8. 병합 후:
   - 병합 커밋에 태그를 단다: `git tag -a vX.Y.0 <merge-commit> -m "..."` → `git push origin vX.Y.0`
   - CHANGELOG 의 해당 절을 본문으로 GitHub 릴리스를 만든다.

## 개정 반영 항목 템플릿

```markdown
## [vX.Y.0] - YYYY-MM-DD

### 근거 고시
- 「감정평가 실무기준」 국토교통부고시 제YYYY-NNN호 (YYYY. M. D. 일부개정, 시행 YYYY. M. D.)
- 국가법령정보센터 admRulSeq=NNNNNNNNNNNNN
- 이전 근거: 국토교통부고시 제2023-522호

### 실무기준 개정 반영
| 조항 | 구분 | 개정 요지 (원문 기준) | 영향 스킬 | 요약·확인사항 | 작업 절차·사례 |
|---|---|---|---|---|---|
| [610-1.5.2.1] | 개정 | … | asset-land | 갱신 | 영향 없음 |
| [8xx-…] | 신설 | … | overlay-compensation-… | 신규 작성 | cases.md #N 추가 |
| [7xx-…] | 삭제 | … | overlay-… | 삭제 반영 | facets.md 수정 |

### 추가
### 변경
### 정정
### 삭제
### 호환성 깨짐
- (스킬 경로·이름이 바뀐 경우: 이전 경로 → 새 경로)

### 검증
- `tools/split_standard.py --check`: 통과
- `tools/validate.py`: errors 0
- 원문 대조 표본: [조항…]
```

## 일반 변경 항목 예시 (PATCH)

```markdown
## [v0.0.1] - YYYY-MM-DD
### 정정
- asset-land: [610-1.5.2.5] 요약의 "하여야 한다"/"할 수 있다" 표현 정정 (#이슈)
### 추가
- lookup-clause/terms.md: 별칭 `…` → [조항] 추가
```
