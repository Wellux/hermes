
import pytest
from gateway.platforms.whatsapp import _normalize_outgoing_chat_id

class TestWhatsAppNormalization:
    def test_already_valid_jid_is_returned_as_is(self):
        jid = "12345678901@s.whatsapp.net"
        assert _normalize_outgoing_chat_id(jid) == jid

    def test_e164_phone_number_is_normalized(self):
        phone = "+1234567890"
        expected = "1234567890@s.whatsapp.net"
        assert _normalize_outgoing_chat_id(phone) == expected

    def test_bare_digits_phone_number_is_normalized(self):
        phone = "1234567890"
        expected = "1234567890@s.whatsapp.net"
        assert _normalize_outgoing_chat_id(phone) == expected

    def test_short_phone_number_is_not_normalized(self):
        phone = "123456" # Less than 7 digits
        assert _normalize_outgoing_chat_id(phone) == phone

    def test_long_phone_number_is_not_normalized(self):
        phone = "1234567890123456" # More than 15 digits
        assert _normalize_outgoing_chat_id(phone) == phone

    def test_phone_number_with_spaces_is_normalized(self):
        phone_with_spaces = "123 456 7890"
        expected = "1234567890@s.whatsapp.net"
        assert _normalize_outgoing_chat_id(phone_with_spaces) == expected

    def test_phone_number_with_hyphens_is_normalized(self):
        phone_with_hyphens = "123-456-7890"
        expected = "1234567890@s.whatsapp.net"
        assert _normalize_outgoing_chat_id(phone_with_hyphens) == expected

