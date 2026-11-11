# GitHub 업로드 및 공동작업

## 처음 업로드

1. GitHub에서 새 저장소를 만듭니다.
2. 저장소의 **Add file → Upload files**를 엽니다.
3. 이 프로젝트 폴더 안의 파일과 폴더를 선택해 올립니다. ZIP 파일 자체를 올리지 마세요.
4. 숨김 파일인 `.gitignore`와 `.streamlit/config.toml`도 포함됐는지 확인합니다.
5. **Commit changes**로 저장합니다.

대량 업로드나 이후 공동작업에는 GitHub Desktop에서 저장소를 Clone한 뒤, 이 폴더의 내용을 복사하여 Commit하고 Push하는 방법이 편합니다. `.gitignore`가 적용되어 로컬 환경과 실제 키 파일은 제외됩니다.

## 팀원 실행

저장소를 Clone하거나 Code → Download ZIP으로 내려받아 압축을 풉니다. Python 3.10 이상을 설치한 뒤 Windows에서는 `실행.bat`을 실행하세요. 다른 환경은 [README의 설치 명령](../README.md#실행)을 따릅니다.

기본 지도는 API 키 없이 사용할 수 있습니다. 현재 비활성인 카카오 길찾기에 쓰는 키는 환경 변수 `KAKAO_REST_API_KEY`로 읽습니다. 실제 키는 공유하지 않습니다.

## 공동작업 규칙

- 저장소 Settings → Collaborators에서 팀원을 초대합니다.
- 작업 전 최신 변경을 Pull하고, 작업별 브랜치에서 수정한 뒤 PR로 합칩니다.
- Streamlit 테마는 `.streamlit/config.toml`에서 관리합니다.
- 이미지 파일은 `assets/`에 저장합니다. 자동차 마커 원본은 `services/parking_marker.py`입니다.
- `assets/car_marker.png`는 원본 마커의 점수 50 상태를 내보낸 이미지입니다. 앱의 점수별 마커는 원본 코드로 계속 생성됩니다.
- `.venv`, `.python`, `.uv-cache`, `__pycache__`, `.env`, `.streamlit/secrets.toml`은 업로드하지 않습니다.
