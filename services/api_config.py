"""프로젝트 루트의 .env와 실행 환경에서 API 키를 읽는다."""
import os
from pathlib import Path

from dotenv import dotenv_values

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


def get_kakao_rest_api_key():
    """운영 환경 변수가 있으면 우선하며, 파일 값은 요청할 때 다시 읽는다."""
    value = os.environ.get("KAKAO_REST_API_KEY")
    if value is None:
        value = dotenv_values(ENV_FILE, encoding="utf-8-sig").get("KAKAO_REST_API_KEY")
    return (value or "").strip()
