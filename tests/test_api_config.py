"""로컬 설정이 실제 API 인증 헤더까지 전달되는지 외부 호출 없이 확인한다."""
import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from services import api_config
from services.kakao_navi import DirectionsError, directions


class APIConfigTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.env_file = Path(directory.name) / ".env"
        self.config_patch = patch.object(api_config, "ENV_FILE", self.env_file)
        self.config_patch.start()
        self.addCleanup(self.config_patch.stop)
        self.environment_patch = patch.dict(os.environ, {}, clear=True)
        self.environment_patch.start()
        self.addCleanup(self.environment_patch.stop)

    def test_dotenv_bom_comments_quotes_and_file_changes(self):
        self.env_file.write_text(
            '# 로컬 키\nKAKAO_REST_API_KEY="  test-file-key  " # 주석\n',
            encoding="utf-8-sig",
        )
        self.assertEqual(api_config.get_kakao_rest_api_key(), "test-file-key")
        self.assertNotIn("KAKAO_REST_API_KEY", os.environ)
        self.env_file.write_text("KAKAO_REST_API_KEY=test-updated-key\n", encoding="utf-8")
        self.assertEqual(api_config.get_kakao_rest_api_key(), "test-updated-key")

    def test_environment_takes_precedence_over_dotenv(self):
        self.env_file.write_text("KAKAO_REST_API_KEY=test-file-key\n", encoding="utf-8")
        os.environ["KAKAO_REST_API_KEY"] = " test-environment-key "
        self.assertEqual(api_config.get_kakao_rest_api_key(), "test-environment-key")
        os.environ["KAKAO_REST_API_KEY"] = ""
        self.assertEqual(api_config.get_kakao_rest_api_key(), "")

    def test_missing_or_blank_key_never_sends_request(self):
        for content in (None, "# 키 없음\n", "KAKAO_REST_API_KEY=\n", "KAKAO_REST_API_KEY\n"):
            with self.subTest(content=content):
                if content is not None:
                    self.env_file.write_text(content, encoding="utf-8")
                self.assertEqual(api_config.get_kakao_rest_api_key(), "")
                with patch("services.kakao_navi.urlopen") as request:
                    with self.assertRaisesRegex(DirectionsError, r"\.env.*KAKAO_REST_API_KEY"):
                        directions((127.0, 37.5), (127.1, 37.6))
                    request.assert_not_called()

    def test_dotenv_key_authenticates_directions_request(self):
        self.env_file.write_text("KAKAO_REST_API_KEY=test-file-key\n", encoding="utf-8")
        payload = {"routes": [{
            "result_code": 0,
            "summary": {"distance": 1200, "duration": 300, "fare": {"toll": 0}},
            "sections": [{"roads": [{"vertexes": [127.0, 37.5, 127.1, 37.6]}]}],
        }]}
        with patch("services.kakao_navi.urlopen", return_value=io.BytesIO(json.dumps(payload).encode())) as request:
            result = directions((127.0, 37.5), (127.1, 37.6), "TIME")
        self.assertEqual(request.call_args.args[0].get_header("Authorization"), "KakaoAK test-file-key")
        self.assertEqual(request.call_args.kwargs["timeout"], 15)
        query = parse_qs(urlparse(request.call_args.args[0].full_url).query)
        self.assertEqual(query["origin"], ["127.0,37.5"])
        self.assertEqual(query["destination"], ["127.1,37.6"])
        self.assertEqual(query["priority"], ["TIME"])
        self.assertEqual(result["distance"], 1200)
        self.assertEqual(result["duration"], 300)
        self.assertEqual(result["paths"], [{"path": [[127.0, 37.5], [127.1, 37.6]]}])


if __name__ == "__main__":
    unittest.main()
