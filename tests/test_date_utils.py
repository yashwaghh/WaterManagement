from src.date_utils import DateUtils

def test_get_date_from_timestamp():
    iso_string = "2026-05-07T12:34:56.789012"
    result = DateUtils.get_date_from_timestamp(iso_string)
    assert result == "2026-05-07"

    # Fallback parsing
    bad_string = "2026-05-07_BAD"
    result = DateUtils.get_date_from_timestamp(bad_string)
    assert result == "2026-05-07"

def test_get_week_number():
    # May 7, 2026 is week 19
    iso_string = "2026-05-07T12:34:56"
    assert DateUtils.get_week_number(iso_string) == 19
