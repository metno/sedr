import pytest
import util

def test_parse_landing_json():
    landingpage_json = None
    with open("../testdata/landingpage.json", "r", encoding="utf-8") as f:
        landingpage_json = json.loads(f.read())

    landing, landing_message = util.parse_landing_json(landingpage_json)
    assert landing
