import pytest

from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


@pytest.mark.parametrize(
    ("text", "marker"),
    [
        ("Call 0987654321", "REDACTED_PHONE_VN"),
        ("CCCD 001201123456", "REDACTED_CCCD"),
        ("Card 4111 1111 1111 1111", "REDACTED_CREDIT_CARD"),
        ("Passport B1234567", "REDACTED_PASSPORT"),
        ("Address: 12 Nguyen Trai Street", "REDACTED_ADDRESS_VN"),
    ],
)
def test_scrub_supported_pii(text: str, marker: str) -> None:
    assert marker in scrub_text(text)
