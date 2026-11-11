"""Server-side Kakao Mobility directions client configured from .env."""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from services.api_config import get_kakao_rest_api_key


class DirectionsError(Exception):
    pass


def directions(origin, destination, priority="RECOMMEND"):
    """Coordinates use (longitude, latitude), distances meters, duration seconds."""
    api_key = get_kakao_rest_api_key()
    if not api_key:
        raise DirectionsError("프로젝트 루트 .env 파일의 KAKAO_REST_API_KEY에 REST API 키를 입력하세요.")
    if priority not in {"RECOMMEND", "TIME", "DISTANCE"}:
        raise DirectionsError("지원하지 않는 경로 옵션입니다.")
    for longitude, latitude in (origin, destination):
        if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
            raise DirectionsError("출발지와 목적지 좌표를 확인하세요.")
    params = urlencode({
        "origin": f"{origin[0]},{origin[1]}",
        "destination": f"{destination[0]},{destination[1]}",
        "priority": priority, "summary": "false", "alternatives": "false",
        "road_details": "false", "roadevent": 0,
    })
    request = Request(
        "https://apis-navi.kakaomobility.com/v1/directions?" + params,
        headers={"Authorization": "KakaoAK " + api_key.strip(),
                 "Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.load(response)
    except HTTPError as error:
        messages = {
            400: "출발지·목적지 또는 요청 조건을 확인하세요.",
            401: "REST API 키 인증에 실패했습니다. 키 설정을 확인하세요.",
            403: "카카오모빌리티 길찾기 API 사용 권한과 서비스 활성화를 확인하세요.",
            429: "API 호출 한도를 초과했습니다. 잠시 후 다시 시도하세요.",
        }
        raise DirectionsError(messages.get(error.code, "카카오 길찾기 서버 오류입니다. 잠시 후 다시 시도하세요.")) from None
    except (URLError, TimeoutError, OSError):
        raise DirectionsError("길찾기 서버에 연결하지 못했습니다. 인터넷 연결을 확인하고 다시 시도하세요.") from None
    except (ValueError, UnicodeError):
        raise DirectionsError("길찾기 응답을 읽지 못했습니다. 다시 시도하세요.") from None
    try:
        route = payload["routes"][0]
        if route["result_code"] != 0:
            raise DirectionsError("해당 좌표의 자동차 경로를 찾지 못했습니다. 출발지와 목적지를 확인하세요.")
        summary = route["summary"]
        result = {"distance": float(summary["distance"]),
                  "duration": float(summary["duration"]),
                  "toll": summary.get("fare", {}).get("toll"), "paths": []}
        for section in route.get("sections", []):
            for road in section.get("roads", []):
                vertices = road.get("vertexes", [])
                if len(vertices) >= 4 and len(vertices) % 2 == 0:
                    result["paths"].append({"path": [vertices[i:i+2] for i in range(0, len(vertices), 2)]})
        return result
    except (KeyError, IndexError, TypeError, ValueError):
        raise DirectionsError("길찾기 응답 정보가 올바르지 않습니다. 다시 시도하세요.") from None
