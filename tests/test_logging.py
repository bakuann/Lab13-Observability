from app.logging_config import scrub_event


def test_scrub_event_redacts_nested_values() -> None:
    event = {
        "event": "request_received",
        "payload": {
            "contact": "student@vinuni.edu.vn",
            "nested": ["4111 1111 1111 1111", {"phone": "0987654321"}],
        },
    }

    scrubbed = scrub_event(None, "info", event)
    rendered = str(scrubbed)

    assert "student@" not in rendered
    assert "4111" not in rendered
    assert "0987654321" not in rendered
    assert "REDACTED_EMAIL" in rendered
