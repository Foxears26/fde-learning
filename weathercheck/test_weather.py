from unittest.mock import patch, MagicMock
import weather

def test_get_coords_ok():
    fake_resp = MagicMock()  # 假 response
    fake_resp.json.return_value = {"results": [{"latitude": 43.7, "longitude": -79.4}]}
    fake_resp.raise_for_status.return_value = None
    with patch("weather.requests.get", return_value=fake_resp):
        assert weather.get_coords("Toronto") == (43.7, -79.4)

def test_get_coords_not_found():
    fake_resp = MagicMock()
    fake_resp.json.return_value = {}  # 没有 results 键
    fake_resp.raise_for_status.return_value = None
    with patch("weather.requests.get", return_value=fake_resp):
        assert weather.get_coords("火星") is None