# 버전 규칙과 릴리스 절차

## 버전 규칙 (vMAJOR.MINOR.PATCH)

| 올리는 자리 | 이런 변경일 때 | 예 |
|---|---|---|
| MAJOR | 스킬 경로·이름의 변경·삭제처럼 **@skills 주소나 스킬 이름에 의존하는 사용처가 깨지는** 변경. 작업 절차 출력 형식을 호환되지 않게 바꾸는 변경 | `assets/real-estate/asset-land` → 다른 경로 |
| MINOR | **실무기준 개정 반영**(근거 고시가 바뀜), **관계법령 내용 변경 반영**(조문 신설·삭제·내용 변경, 별표 변경), 새 컬렉션·스킬·작업 절차 추가 | 국토교통부고시 제2023-522호 → 새 고시, 토지보상법 시행규칙 개정 |
| PATCH | 관계법령의 개정 표시만 변경, 요약·확인사항·별표 가공본 정정, 별칭·사례 추가, 문서·링크·도구 수정, 원문 변환 오류 수정(원문 내용은 그대로) | 요약의 의무/재량 표현 정정 |

- 1.0.0 전(0.x)에는 MAJOR 대신 MINOR 를 올린다. 이때 CHANGELOG 에 `### 호환성 깨짐` 절을 반드시 둔다.
- 근거 고시와 법령 판본은 MINOR 단위로 기록한다. 같은 고시·판본을 쓰는 동안은 PATCH 만 올라간다.
- 버전 태그는 해당 PR 이 `main` 에 병합된 커밋에 단다. 형식은 `v0.1.0` 처럼 `v` 접두어를 붙인다.

## 개정 반영 (실무기준·관계법령)

- 절차는 [rules/skill-update-maintenance](../rules/skill-update-maintenance/SKILL.md) 하나에 있다. 여기에는 버전·기록 규칙만 둔다.
- 사용자가 어느 쪽 개정을 말하든 그 절차의 1단계에서 실무기준과 관계법령을 모두 확인한다(`fetch_standard.py --check`, `fetch_laws.py --check`).
- 버전:
  - 실무기준 개정(근거 고시 변경): MINOR. 기록은 아래 "개정 반영 항목 템플릿"
  - 관계법령 내용 변경(조문 신설·삭제·내용 변경, 별표 변경): MINOR. 개정 표시만 바뀌면 PATCH
- 관계법령 기록은 CHANGELOG 의 `### 관계법령 갱신` 절에 쓴다.
  - 법령별 판본 변화(시행일)
  - `tools/laws/diff_laws.py --markdown` 표와 행별 처리 결과
- 병합 후:
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

## 관계법령 갱신 항목 템플릿

```markdown
## [vX.Y.0] - YYYY-MM-DD

### 관계법령 갱신
- 확인 일자: YYYY-MM-DD (`fetch_standard.py --check`: 실무기준 변동 없음 / 있음 → 위 템플릿 병행)
| 법령 | 이전 시행일 (공포번호) | 현행 시행일 (공포번호) | 컬렉션 |
|---|---|---|---|
| 「…」 시행규칙 | YYYY. M. D. (제N호) | YYYY. M. D. (제N호) | land-compensation-act |

| 조문·별표 | 변경 (diff_laws) | 처리 | 영향 스킬 |
|---|---|---|---|
| 규칙 제NN조 | 내용 변경 | 요약 갱신 | lca-… |
| 규칙 별표 N | 별표 변경 | 가공본 재가공·요약 대조 | lca-… |
| 영 제NN조 | 개정 표시만 변경 | 요약 영향 없음 | — |

### 검증
- `tools/laws/fetch_laws.py --check`: 같은 현행 판본
- `tools/laws/build_laws.py --check`·`--status`: 통과, 모든 주제 OK
- `tools/validate.py`: errors 0
```

## 일반 변경 항목 예시 (PATCH)

```markdown
## [v0.0.1] - YYYY-MM-DD
### 정정
- asset-land: [610-1.5.2.5] 요약의 "하여야 한다"/"할 수 있다" 표현 정정 (#이슈)
### 추가
- lookup-clause/terms.md: 별칭 `…` → [조항] 추가
```
