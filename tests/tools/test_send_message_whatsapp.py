
import pytest
from tools.send_message_tool import _parse_target_ref

def test_whatsapp_e164_target_gets_jid_suffix():
    # Simulate an E.164 phone number as target_ref
    target_ref = "+1234567890"
    platform_name = "whatsapp"

    # Call the parsing function
    chat_id, thread_id, is_explicit = _parse_target_ref(platform_name, target_ref)

    # ASSERT (RED): The desired output for the fix is '1234567890@s.whatsapp.net'.
    # The current code returns '+1234567890', which will cause this assertion to fail.
    assert chat_id == "1234567890@s.whatsapp.net", "Expected E.164 target to be converted to JID format"
    assert thread_id is None
    assert is_explicit is True
