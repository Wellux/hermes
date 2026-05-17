
import pytest
from gateway.platforms.whatsapp import _normalize_outgoing_chat_id

@pytest.mark.parametrize(
    "input_chat_id,expected_output",
    [
        ("1234567890", "1234567890@s.whatsapp.net"),
        ("+1234567890", "1234567890@s.whatsapp.net"),
        ("123-456-7890", "1234567890@s.whatsapp.net"),
        ("1234567890@s.whatsapp.net", "1234567890@s.whatsapp.net"),
        ("user@lid", "user@lid"),
        ("group@g.us", "group@g.us"),
        ("", ""),
        (None, ""),
        ("not_a_phone_number", "not_a_phone_number"), # Should not be modified
        ("short", "short"), # Too short for phone number
        ("verylongphonenumber123456789012345", "verylongphonenumber123456789012345"), # Too long for phone number
        ("1234567890abc", "1234567890abc"), # Contains non-digits after cleaning
    ]
)
def test_normalize_outgoing_chat_id(input_chat_id, expected_output):
    """
    Test _normalize_outgoing_chat_id to ensure bare phone numbers are correctly
    converted to JID format, and other JIDs/non-phone strings are preserved.
    """
    assert _normalize_outgoing_chat_id(input_chat_id) == expected_output
