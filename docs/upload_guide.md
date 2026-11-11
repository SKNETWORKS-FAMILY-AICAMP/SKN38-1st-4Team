# GitHub 업로드 및 공동작업

## 처음 업로드

1. GitHub에서 새 저장소를 만듭니다.
2. 저장소의 **Add file → Upload files**를 엽니다.
3. 이 프로젝트 폴더 안의 파일과 폴더를 선택해 올립니다. ZIP 파일 자체를 올리지 마세요.
4. 숨김 파일인 `.gitignore`와 `.streamlit/config.toml`도 포함됐는지 확인합니다.
5. **Commit changes**로 저장합니다.

대량 업로드나 이후 공동작업에는 GitHub Desktop에서 저장소를 Clone한 뒤, 이 폴더의 내용을 복사하여 Commit하고 Push하는 방법이 편합니다. `.gitignore`가 적용되어 로컬 환경과 실제 키 파일은 제외됩니다.

## 팀원 실행

저장소를 Clone하거나 Code → Download ZIP으로 내려받아 압축을 풉니다. Python 3.10 이상을 설치한 뒤 Windows에서는 `실행.bat`을 실행하세요. 다른 환경은 [실행·개발 안내의 설치 명령](run_guide.md#실행)을 따릅니다.

기본 지도는 API 키 없이 사용할 수 있습니다. 지도 상세 패널의 카카오 자동차 길찾기에 쓰는 키는 프로젝트 루트의 `.env`에 `KAKAO_REST_API_KEY=발급받은_REST_API_키` 형식으로 설정합니다. 같은 이름의 운영 환경 변수가 있으면 우선하며, 상세 설정은 [실행·개발 안내의 API 키 설정](run_guide.md#api-키-설정-env)을 따릅니다. 실제 키는 공유하지 않습니다.

`.env` 연결을 반영할 때는 루트의 `.gitignore`, `requirements.txt`, `prepare.bat`, `app.py`와 `services/api_config.py`, `services/kakao_navi.py`, `services/kakao_navi_view.py`, `tests/test_api_config.py`를 같은 경로로 함께 올립니다. `.env`는 로컬에서만 사용합니다. GitHub 웹의 Upload files는 `.gitignore`가 파일 선택을 막지 않으므로 `.env`와 사본을 직접 제외합니다.

## FAQ 수정 업로드 위치

대상 저장소는 `SKNETWORKS-FAMILY-AICAMP/SKN38-1st-4Team`입니다. 아래 경로는 모두 **저장소 루트 기준**이며, `newgit/` 폴더를 추가로 만들지 않습니다. 실제 업로드·커밋·푸시는 사용자가 진행합니다.

| 로컬 파일 = GitHub에 올릴 경로 | 용도 |
|---|---|
| `sql/Table07_faq.sql` | FAQ 원본 27개. 화면 실행에 필요 |
| `services/faq.py` | FAQ 원본을 읽는 공통 서비스 |
| `pages/1_FAQ.py` | 카테고리 선택·그룹별 질문 화면 |
| `scripts/build_sql_dump.py` | FAQ 원본을 포함하는 통합 덤프 생성기 |
| `sql/skn_1st_4team.sql` | 새 FAQ가 반영된 전체 DB 덤프 |
| `sql/faq_queries.sql` | FAQ 조회와 카테고리 조건 |
| `sql/parking_risk_queries.sql` | FAQ 27개에 맞춘 적재 확인 |
| `sql/flood_rainfall_queries.sql` | FAQ 27개에 맞춘 적재 확인 |
| `tests/test_faq.py` | SQL 원본·문자열 처리 검증 |
| `tests/test_app_navigation.py` | 화면 전환과 카테고리 필터 검증 |
| `README.md` | 실행·폴더 구조 안내 |
| `docs/upload_guide.md` | 이 업로드 위치 안내 |
| `TASKS.md` | 작업 상태·인계 기록 |

루트에 있던 `Table07_faq.sql`은 `sql/Table07_faq.sql`로 이동했습니다. 원격 저장소에도 루트 파일이 있다면 이번 업로드에서 삭제하고 새 경로만 유지합니다. GitHub 웹 업로드는 이전 경로를 자동으로 삭제하지 않으므로 별도로 확인합니다.

위 파일은 같은 변경으로 함께 반영합니다. 특히 `services/faq.py`와 `sql/Table07_faq.sql`이 함께 있어야 FAQ 화면이 실행됩니다. `.handoff/`는 로컬 작업·검증 기록이며 이번 FAQ 배포에는 필요하지 않습니다.

SQL을 수정한 뒤에는 프로젝트 루트에서 `python scripts/build_sql_dump.py`와 `python -m unittest discover -s tests -t .`를 실행해 통합 덤프와 화면을 확인합니다. FAQ 화면은 MySQL 접속 없이 `sql/Table07_faq.sql` 파일을 직접 읽습니다.

## 공동작업 규칙

- 저장소 Settings → Collaborators에서 팀원을 초대합니다.
- 작업 전 최신 변경을 Pull하고, 작업별 브랜치에서 수정한 뒤 PR로 합칩니다.
- Streamlit 테마는 `.streamlit/config.toml`에서 관리합니다.
- 이미지 파일은 `assets/`에 저장합니다. 자동차 마커 원본은 `services/parking_marker.py`입니다.
- `assets/car_marker.png`는 원본 마커의 점수 50 상태를 내보낸 이미지입니다. 앱의 점수별 마커는 원본 코드로 계속 생성됩니다.
- `.venv`, `.python`, `.uv-cache`, `__pycache__`, `.env`, `.streamlit/secrets.toml`은 업로드하지 않습니다.
