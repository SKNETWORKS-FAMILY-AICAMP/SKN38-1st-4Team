# 침착 — 데이터로 확인하는 내 주변의 침수 위험 주차장

SKN38 1차 프로젝트 4팀. 2025년 강수량, 지형(고도), 과거 침수 이력 자료로 서울 5개 자치구(강북·강서·도봉·서대문·은평) 주차장별 **상대적인** 침수 위험도를 비교해 보여 주는 Streamlit 웹앱입니다. 실시간 침수 예측이 아닙니다.

> 지금은 개발 환경, 문서, 앱 입력 자료(주차장 163곳)까지 준비된 상태이고 화면 코드는 아직 없습니다.

## 문서

| 문서 | 내용 |
|---|---|
| [AGENTS.md](AGENTS.md) | AI 에이전트(Claude Code, Codex)와 사람이 함께 따르는 작업 지침: 폴더 구조, 코드 규칙, 화면에서 지킬 것, 검사, 에이전트가 대신 하는 git 작업 |
| [CLAUDE.md](CLAUDE.md) | Claude Code 가 AGENTS.md 를 읽게 하는 연결 |
| [docs/product-plan.md](docs/product-plan.md) | 화면 기획: 메뉴, 화면별 구성, 지운 기능, 색, 문구 규칙 |
| [docs/risk-index.md](docs/risk-index.md) | 위험지수: 사용 자료와 출처, 계산식, 가중치, 등급, 안내 문구, 앱 입력 자료 형식 |
| [docs/plan-images/](docs/plan-images/) | 기획 시안 이미지 |

## 개발 환경 준비

처음 한 번만 하면 됩니다. 그다음 git 작업(브랜치, 커밋, PR, 병합, 정리)은 에이전트(Claude Code, Codex)가 대신 합니다. 아래 「작업 올리기」를 보세요.

1. 프로그램을 설치합니다.
   - [Python](https://www.python.org/downloads/) 3.11 이상
   - [Git](https://git-scm.com/downloads)
   - [GitHub CLI](https://cli.github.com/) — 에이전트가 PR 을 만들고 병합할 때 씁니다. Windows 는 `winget install --id GitHub.cli`, macOS 는 `brew install gh` 로도 설치됩니다.
2. 터미널에서 GitHub 에 한 번 로그인합니다. 물음에는 차례로 `GitHub.com` → `HTTPS` → Git 인증 `Yes` → `Login with a web browser` 를 고르고, 브라우저에 뜨는 화면에서 승인합니다.

   ```bash
   gh auth login
   ```

3. 팀 저장소를 내 계정에 포크하고 받습니다. 이 명령 하나로 포크 만들기, 받기, 팀 저장소를 `upstream` 으로 등록하기가 모두 끝납니다. 이미 포크해서 받아 둔 폴더가 있으면 건너뜁니다.

   ```bash
   gh repo fork SKNETWORKS-FAMILY-AICAMP/SKN38-1st-4Team --clone
   cd SKN38-1st-4Team
   ```

4. 가상환경을 만들고 패키지를 설치합니다.

   ```bash
   python -m venv .venv
   ```

macOS·Linux:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
```

Windows(PowerShell):

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

> 예전에 저장소에 올라가 있던 `.venv` 폴더는 이제 git 이 관리하지 않습니다. 이 변경을 받은 뒤 `.venv` 가 지워졌다면 위 순서로 다시 만드세요.

## 앱 실행

앱 시작 파일(예: `streamlit_app.py`)을 만든 뒤 실행합니다. 브라우저에서 http://localhost:8501 이 열립니다.

```bash
.venv/bin/streamlit run streamlit_app.py
```

Windows 는 `.venv\Scripts\streamlit.exe run streamlit_app.py` 입니다.

## 앱 입력 자료 다시 만들기

팀 분석 결과(`data/raw/`)를 바꿨으면 앱이 읽는 `data/parking_risk.csv` 를 다시 만들어 함께 커밋합니다. 자료 설명과 계산은 [docs/risk-index.md](docs/risk-index.md) 에 있습니다.

```bash
.venv/bin/python -m analysis.build_parking_risk
```

Windows 는 `.venv\Scripts\python.exe -m analysis.build_parking_risk` 입니다.

## 검사

코드 검사(ruff)와 테스트(pytest)를 돌립니다. 테스트는 `tests/` 폴더에 `test_*.py` 로 둡니다. 팀 저장소로 PR 을 보내면 팀 저장소의 GitHub Actions 가 같은 검사를 돌립니다(포크의 Actions 는 켜지 않아도 됩니다). 검사가 승인 대기로 멈춰 있으면 팀 저장소 관리자가 PR 화면에서 승인합니다.

```bash
.venv/bin/python -m ruff check . && .venv/bin/python -m ruff format --check . && .venv/bin/python -m pytest
```

## 작업 올리기

### 에이전트에게 맡기기(기본)

저장소 폴더에서 Claude Code 나 Codex 를 실행하고 「반경 선택 기능 만들어서 올려 줘」처럼 말하면 됩니다. 에이전트가 [AGENTS.md](AGENTS.md) 「git 작업」 순서대로 다음을 모두 합니다.

1. 최신 코드 받기
2. 작업 브랜치 만들기
3. 작업과 검사
4. 커밋, 내 포크에 올리기
5. 팀 저장소로 PR 만들기
6. CI 검사 확인(실패하면 고쳐서 다시 올림)
7. 병합, 정리

팀 결정(2026-11-10)에 따라 CI 검사가 통과하면 사람 확인 없이 병합합니다.

- 에이전트가 명령을 실행해도 되는지 물으면 허용하세요. 같은 명령을 다시 묻지 않게 하는 선택지가 있으면 그것을 고르면 다음부터 자동으로 진행됩니다.
- 병합 권한이 없다고 나오면 팀 저장소에 쓰기 권한이 있는 팀원에게 병합을 부탁하거나 권한을 받으세요.
- Claude 앱·웹의 클라우드 세션은 팀 저장소에 연결되지 않아(조직에 Claude GitHub 앱이 없음) PR 생성과 병합을 못 합니다. 각자 컴퓨터에서 실행하세요.

### 직접 할 때

내 포크에 브랜치를 올리고 팀 저장소 main 으로 PR 을 보냅니다. 팀 저장소 main 에는 직접 push 하지 않습니다.

1. 팀 저장소 최신을 받아 내 main 을 맞춥니다.

   ```bash
   git switch main
   git pull --ff-only upstream main
   git push origin main
   ```

2. 작업 브랜치를 만들어 커밋하고 내 포크에 올립니다. 브랜치 이름과 커밋 메시지 형식은 [AGENTS.md](AGENTS.md) 「git 작업」을 따릅니다.

   ```bash
   git switch -c <브랜치 이름>
   git add <파일> && git commit -m "<무엇을 바꿨는지>"
   git push -u origin <브랜치 이름>
   ```

3. GitHub 의 내 포크 화면에 뜨는 **Compare & pull request** 를 누릅니다. base 가 `SKNETWORKS-FAMILY-AICAMP/SKN38-1st-4Team` 의 `main` 인지 확인하고 PR 을 만듭니다.
4. 검사가 초록이면 squash 병합합니다.
5. 병합된 뒤 PR 화면의 **Delete branch** 로 포크의 브랜치를 지우고, 내 컴퓨터에서도 지운 다음 1번으로 돌아갑니다. squash 병합은 커밋이 새로 만들어지므로 `-d` 로는 지워지지 않아 `-D` 를 씁니다.

   ```bash
   git switch main
   git branch -D <브랜치 이름>
   ```

내 포크의 main 에서는 커밋하지 않습니다. 그래야 1번의 `git pull --ff-only upstream main` 이 언제나 충돌 없이 됩니다.

## 저장소에 올리지 않는 것

`.gitignore` 가 막아 둡니다.

- 가상환경 `.venv/` — 팀원마다 운영체제와 경로가 달라서 각자 만듭니다.
- 비밀값 — API 키는 `.env` 나 `.streamlit/secrets.toml` 에 두고 올리지 않습니다.

## 환경 파일

| 파일 | 하는 일 |
|---|---|
| `requirements.txt` | 앱 실행에 필요한 패키지(streamlit, pandas) |
| `requirements-dev.txt` | 개발용 패키지(ruff, pytest) 추가 |
| `pyproject.toml` | ruff·pytest 설정 |
| `.streamlit/config.toml` | Streamlit 테마(흰색·파란색 기본) |
| `.github/workflows/ci.yml` | PR·main 에 검사 자동 실행 |
| `.gitignore` | git 에 올리지 않을 파일 |
| `.gitattributes` | 윈도우·맥 줄바꿈 차이 맞춤 |
