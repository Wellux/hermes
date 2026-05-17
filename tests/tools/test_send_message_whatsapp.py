import pytest
import json
from unittest.mock import AsyncMock, patch
from tools.send_message_tool import send_message_tool, _parse_target_ref
from gateway.config import Platform, PlatformConfig

@pytest.fixture(autouse=True)
def mock_dependencies():
    """Mock external dependencies to isolate send_message_tool."""
    with patch("tools.send_message_tool._send_to_platform", new_callable=AsyncMock) as mock_send_to_platform, \
         patch("tools.send_message_tool._handle_list", new_callable=AsyncMock) as mock_handle_list, \
         patch("gateway.channel_directory.format_directory_for_display", return_value=[]) as mock_format_directory, \
         patch("gateway.channel_directory.resolve_channel_name", return_value=None) as mock_resolve_channel_name, \
         patch("gateway.config.load_gateway_config") as mock_load_gateway_config, \
         patch("gateway.whatsapp_identity.normalize_whatsapp_identifier", side_effect=lambda x: x) as mock_normalize_whatsapp_identifier, \
         patch("gateway.status.is_gateway_running", return_value=True) as mock_is_gateway_running, \
         patch("tools.send_message_tool.tool_error") as mock_tool_error, \
         patch("tools.send_message_tool._error") as mock_error_builder: # Mock the internal _error helper

        # Configure mock_send_to_platform to return a dict for successful calls
        mock_send_to_platform.return_value = {"success": True, "message_id": "mock_message_id"}

        # Configure _error to return a dict as expected by json.dumps
        mock_error_builder.side_effect = lambda msg: {"error": msg}

        # Mock load_gateway_config to return a simple config with WhatsApp enabled
        mock_config_instance = AsyncMock()
        mock_config_instance.platforms = {
            Platform.WHATSAPP: PlatformConfig(enabled=True, extra={"bridge_port": 3000})
        }
        mock_config_instance.get_home_channel.return_value = None
        mock_load_gateway_config.return_value = mock_config_instance

        yield mock_send_to_platform, mock_handle_list, mock_format_directory, mock_resolve_channel_name, mock_load_gateway_config, mock_normalize_whatsapp_identifier, mock_is_gateway_running, mock_tool_error, mock_error_builder

@pytest.mark.asyncio
async def test_whatsapp_send_bare_phone_produces_jid(mock_dependencies):
    mock_send_to_platform, _, _, _, _, mock_normalize_whatsapp_identifier, _, _, _ = mock_dependencies

    # Simulate normalize_whatsapp_identifier returning the bare number (which _parse_target_ref should then convert to JID)
    mock_normalize_whatsapp_identifier.side_effect = lambda x: x.replace('+', '') if x.startswith('+') else x

    # Test with a bare phone number that _parse_target_ref should convert to a JID internally
    args = {"action": "send", "target": "whatsapp:491629001708", "message": "Test message"}
    result = send_message_tool(args)
    result_dict = json.loads(result)

    assert "success" in result_dict
    assert result_dict["success"] is True
    platform_arg = mock_send_to_platform.call_args[0][0]
    chat_id_arg = mock_send_to_platform.call_args[0][2]
    assert platform_arg == Platform.WHATSAPP
    assert chat_id_arg == "491629001708@s.whatsapp.net"

    # Test with an E.164 phone number
    args_e164 = {"action": "send", "target": "whatsapp:+491629001708", "message": "Test message E.164"}
    result_e164 = send_message_tool(args_e164)
    result_dict_e164 = json.loads(result_e164)

    assert "success" in result_dict_e164
    assert result_dict_e164["success"] is True
    platform_arg_e164 = mock_send_to_platform.call_args[0][0]
    chat_id_arg_e164 = mock_send_to_platform.call_args[0][2]
    assert platform_arg_e164 == Platform.WHATSAPP
    assert chat_id_arg_e164 == "491629001708@s.whatsapp.net"


@pytest.mark.asyncio
async def test_whatsapp_send_explicit_jid_passes(mock_dependencies):
    mock_send_to_platform, _, _, _, _, _, _, _, _ = mock_dependencies

    # Test with an explicit JID
    args = {"action": "send", "target": "whatsapp:491629001708@s.whatsapp.net", "message": "Test message JID"}
    result = send_message_tool(args)
    result_dict = json.loads(result)

    assert "success" in result_dict
    assert result_dict["success"] is True

    # Check that Platform.WHATSAPP was passed and chat_id was correct.
    platform_arg = mock_send_to_platform.call_args[0][0]
    chat_id_arg = mock_send_to_platform.call_args[0][2]
    assert platform_arg == Platform.WHATSAPP # Direct comparison with Enum member
    assert chat_id_arg == "491629001708@s.whatsapp.net"


@pytest.mark.asyncio
async def test_whatsapp_send_bare_phone_with_correct_normalization_mock(mock_dependencies):
    mock_send_to_platform, _, _, _, _, mock_normalize_whatsapp_identifier, _, _, _ = mock_dependencies

    # Simulate normalize_whatsapp_identifier returning a JID for bare numbers
    def mock_normalize(x):
        if x == "491629001708":
            return "491629001708@s.whatsapp.net"
        elif x == "+491629001708":
            return "491629001708@s.whatsapp.net"
        return x # For other cases, return as is (e.g. explicit JID already)
    mock_normalize_whatsapp_identifier.side_effect = mock_normalize

    # Test with a bare phone number
    args = {"action": "send", "target": "whatsapp:491629001708", "message": "Test message normalized"}
    result = send_message_tool(args)
    result_dict = json.loads(result)

    assert "success" in result_dict
    assert result_dict["success"] is True
    platform_arg = mock_send_to_platform.call_args[0][0]
    chat_id_arg = mock_send_to_platform.call_args[0][2]
    assert platform_arg == Platform.WHATSAPP
    assert chat_id_arg == "491629001708@s.whatsapp.net"

    # Test with an E.164 phone number
    args_e164 = {"action": "send", "target": "whatsapp:+491629001708", "message": "Test message E.164 normalized"}
    result_e164 = send_message_tool(args_e164)
    result_dict_e164 = json.loads(result_e164)

    assert "success" in result_dict_e164
    assert result_dict_e164["success"] is True
    platform_arg_e164 = mock_send_to_platform.call_args[0][0]
    chat_id_arg_e164 = mock_send_to_platform.call_args[0][2]
    assert platform_arg_e164 == Platform.WHATSAPP
    assert chat_id_arg_e164 == "491629001708@s.whatsapp.net"
