<!-- SPDX-License-Identifier: GPL-3.0-only -->

# 정적 사이트

사이트: <https://pacappkor.github.io/kapa_skills/>

원본 Markdown은 기존 위치에만 보관한다. 표준 라이브러리만 쓰는
`tools/build_site.py`는 Git 추적 Markdown과 출처 이미지를 `.site-src/`에 준비한다.
추적하지 않은 파일은 게시하지 않는다. 비 Markdown 자료·코드 링크는 GitHub의 원본으로
연결한다. 자격 증명이나 저장소 밖의 파일을 읽지 않는다.

## 로컬 빌드

저장소 루트에서 Python 3.12 이상을 사용한다.

```sh
python -m venv .venv-docs
# Linux/macOS
. .venv-docs/bin/activate
# Windows PowerShell에서는 .venv-docs\Scripts\Activate.ps1
python -m pip install --require-hashes -r requirements-docs.txt
python -I -B tools/build_site.py --strict
mkdocs build --strict
# 선택: mkdocs serve
```

`.site-src/`, `site/`, `.venv-docs/`는 gitignore 대상이다. `.site-src/`는 매번
교체되므로 직접 수정하지 않는다. 원문 생성기·색인은 먼저 기존 절차로 갱신한다.
빌드 스크립트는 원문·스킬·그래프·법령 색인을 변경하지 않는다.

- 홈: README와 00-kapa-start의 안내·입구로 연결
- 스킬 색인: 경로의 분류별로 모든 SKILL.md를 그룹화
- 법령 색인: `docs/law-index.json`의 수록 판본·시행일·조문·실무기준
- 관련 스킬: `docs/graph.json`의 들어오는/나가는 인용을 함께 표시
- 디렉터리 링크: README가 있으면 overview로, 없으면 생성한 디렉터리 색인으로 연결
- README는 staging에서만 overview.md로 이름을 바꿔 MkDocs의 index.md 충돌을 피한다.
- 로컬 링크 대상의 존재를 검사하고 `--strict`에서는 누락·저장소 탈출을 실패 처리한다.
  코드 예제는 제외한다. 외부 URL의 응답·법적 유효성이나 모든 원문 앵커까지 검증하는 도구는 아니다.
- MkDocs Material 9.6.14에 `lunr.ko.min.js`가 포함됨을 확인했다. `ko` + `en` 검색과
  공백·하이픈·제로폭 공백 분리를 사용한다. 한국어 형태소 분석이나 조사 제거를 보장하지 않는다.
- 모든 콘텐츠 페이지의 공지 바는 README의 면책 문구와 law.go.kr·NOTICE 링크를 표시한다.
  생성 색인에는 편집 링크를 숨기고, README 별칭은 원본 README를 편집하도록 연결한다.

## 배포

CI의 기존 필수 `offline-checks`는 그대로 유지하며 별도 `docs-build` 작업이 PR에서도
엄격 빌드만 수행한다. `pages.yml`은 main 푸시/수동 실행에서 빌드 후 GitHub Pages
아티팩트를 배포한다. 공식 액션 SHA는 `git ls-remote --tags`로 확인했다.
Pages 및 OIDC 쓰기 권한은 deploy 작업에만 있다. 저장소 Settings → Pages에서
Source를 **GitHub Actions**로 설정해야 한다. 워크플로 파일만 커밋한 상태에서는
사이트가 게시되지 않으며 main 반영 후 실행되어야 한다.

의존성은 전이 의존성까지 버전과 PyPI SHA-256으로 고정한다. 업데이트 시 별도
가상환경에서 다시 해시를 확인하고 Python 3.12 CI와 엄격 전체 빌드를 수행한다.
