# my_poke 작업 규칙

## 프로젝트
- 포켓몬 도감 Streamlit 앱 (app.py)
- 디자인은 DESIGN.md를 따른다

## ① Git 작업 방식 기초
- main, develop에 직접 커밋하지 않는다. 항상 새 브랜치에서 작업한다.
- 커밋 메시지는 [feat] / [fix] / [docs] / [test] / [refactor] 로 시작하고, 무엇을 왜 했는지 한국어로 쓴다.
- 한 커밋은 통째로 취소해도 아깝지 않은 단위로 한다. 시키지 않아도 작업 단위마다 커밋한다.
- .env, 비밀번호, API 키, .venv는 커밋하지 않는다.
- 요청하지 않은 파일은 건드리지 않는다.
- 브랜치 삭제나 강제 덮어쓰기는 하지 않고 먼저 나에게 묻는다.

## ② Gitflow 따르기
- main = 운영 배포본, develop = 개발 통합본.
- 기능 작업: develop에서 feature/<이름> 브랜치를 만들고, 끝나면 develop으로 Pull Request.
- 출시: develop에서 release/<버전> 브랜치를 만들고 main으로 Pull Request.
  머지된 뒤 main의 내용을 develop에도 반영한다.
- 긴급 수정: main에서 hotfix/<이름> 브랜치를 만들고 main으로 Pull Request.
  머지된 뒤 develop에도 반영한다.
- 작업이 끝나면 push하고 Pull Request까지 만든다. 머지는 사람이 한다.
