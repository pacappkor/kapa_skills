# 법령 연혁 판본 식별

## 저장과 선택

- 연혁 목록 `sources/laws/<collection>/versions/<level>.json` 의 판본 키는 `(lsiSeq, efYd)` 다. 분할 시행으로 같은 `lsiSeq` 가 여러 번 나타날 수 있다. 목록을 `lsiSeq` 만으로 사전화하거나 중복 제거하지 않는다.
- 과거 본문은 `sources/laws/<collection>/versions/<level>/<lsiSeq>-<efYd>.json` 에 저장한다. `headings`, `articles`, `annexes` 와 함께 `addenda`(부칙·경과조치)를 보존한다.
- `fetch_version.py <collection> <level> <lsiSeq>` 는 연혁 행이 하나일 때만 선택한다. 여러 시행일이면 `--ef YYYY-MM-DD` 로 정확히 지정한다. `--at YYYY-MM-DD` 는 기준일에 공포·시행된 가장 최근 판본을 선택한다. 두 옵션은 함께 쓰지 않는다.
- 상태는 `current`(현행), `scheduled`(미시행), `past`(과거), `predecessor`(이전 이름의 법령), `repealed`(시행된 폐지)다. 개정 종류가 `폐지` 또는 `타법폐지`이면 현행으로 승격하지 않는다. `폐지제정`은 새 제정이므로 폐지 상태로 분류하지 않는다. 폐지 시행일부터는 현행 판본이 없고 이전 행은 `past`다. `--at` 은 폐지 시행일 이후에 폐지 행이나 직전 판본을 시행 중인 것으로 선택하지 않고 오류를 낸다.
- 본문 응답의 `lsiSeq` 와 `efYd` 를 함께 검증한다. 요청과 다른 단계 시행일로 돌아온 본문은 저장하거나 그 행의 법령명으로 사용하지 않는다.
- `fetch_version.py` 는 선택한 연혁 행의 개정 종류가 `폐지` 또는 `타법폐지`일 때에만 조문 0개인 전체 폐지 본문을 저장할 수 있다. 법령명(공백 제외)·`lsiSeq`·`efYd`가 요청과 일치하고, 정제된 부칙에 `「<해당 법령명>」을 폐지한다` 또는 `「<해당 법령명>」를 폐지한다` 문장이 있어야 한다. 부칙 밖의 문구나 스크립트·화면 제어 문구는 증거로 쓰지 않는다. 비폐지 행(`폐지제정` 포함)의 조문 0개 본문은 계속 거부하며, 현행 수집의 공용 검증은 완화하지 않는다.
- 예: `python -I tools/laws/fetch_version.py land-compensation-act rule 86824 --ef 2008-04-18`. 샘플은 `86824-20080418.json` 이다.
- `fetch_versions.py --check` 는 저장 목록과 다른 경우 또는 수집 실패에만 실패한다. 이미 기록된 미시행 개정은 `SCHEDULED` 정보로 출력하며, 그 자체로 실패하지 않는다. 부칙·경과조치 검토 의무는 그대로다.
- 연혁 수집·검사 모두 생략된 법령명은 같은 `lsId`의 저장 목록에서 `(lsiSeq, efYd, ancYd, ancNo, kind)`가 일치하는 완전한 이름을 재사용한다. 표시된 이름 접두사도 일치해야 한다. 새 행·메타데이터 변경·이름 누락/생략·충돌은 공식 본문으로 다시 확인한다. 상태는 매번 기준일로 재계산하며, 목록 전체 비교와 `CHANGED` 판정은 유지한다. 마지막의 `live title requests`는 이름 확인을 위해 본문을 요청한 횟수다(현행 식별자 확인 요청은 제외).

## 인터페이스 호환성

기존 계약의 판본 ID `law/<lsId>@<lsiSeq>` 와 조문 ID `law/<lsId>@<lsiSeq>#a<조>[-<가지>]` 는 유지한다. `build_index.py` 와 `docs/law-index.json` 은 현행 본문만 색인하며, `current.efYd` 를 함께 제공한다. 따라서 현행 조문 ID 는 변경하지 않는다. 색인의 `versions_file` 은 모든 시행일 행을 보존한 목록을 가리킨다. 과거 본문을 현행 조문 색인에 합치지 않는다.

분할 시행 과거 판본을 외부에서 구별해야 할 때의 **하위 호환 확장 제안**은 `law/<lsId>@<lsiSeq>.<efYd>` 및 `law/<lsId>@<lsiSeq>.<efYd>#a<조>[-<가지>]` 다. 같은 순번의 시행일이 여러 개일 때만 날짜 접미사를 사용한다. 기존 ID 는 삭제·재작성하지 않으며, 현행 ID 는 그대로 현행 본문을 뜻한다. 과거 조회에서 날짜 없는 중복 순번은 임의의 첫 행으로 해석하지 않고 시행일 지정을 요구한다.

이 확장은 아직 외부 소비자에 구현된 계약이 아니다. 형제 저장소 `kapa_knowledge` 의 `docs/SCHEMA.md`, `tools/validate.py`(ID 정규식·연혁 확인), `tools/collect_article.py`(조문 ID 파서), `tools/lawweb.py`(조회 인자)는 도입 전에 함께 갱신해야 한다. 특히 날짜 접미사를 순번에 포함해 전송하지 말고, 순번과 시행일을 따로 검증·전달해야 한다. 이 PR 에서는 해당 저장소를 변경하거나 날짜 접미사 ID 를 출력하지 않는다.
