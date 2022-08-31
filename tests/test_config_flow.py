"""Test integration_blueprint config flow."""
from unittest.mock import patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_HOST, CONF_PORT

from custom_components.eta.const import (
    DOMAIN, CHOOSEN_ENTITIES, FLOAT_DICT
)
from .const import MOCK_CONFIG, FLOAT_DICT_CONFIG


# This fixture bypasses the actual setup of the integration
# since we only want to test the config flow. We test the
# actual functionality of the integration in other test modules.
@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with patch("custom_components.eta.async_setup", return_value=True, ), patch(
            "custom_components.eta.async_setup_entry",
            return_value=True,
    ), patch(
        "custom_components.eta.config_flow.EtaFlowHandler._get_possible_endpoints",
        return_value=FLOAT_DICT_CONFIG):
        yield


@pytest.fixture()
def bypass_test_url_fixture():
    with patch(
            "custom_components.eta.config_flow.EtaFlowHandler._test_url",
            return_value=True,
    ):
        yield


@pytest.fixture()
def throw_error_test_url_fixture():
    with patch(
        "custom_components.eta.config_flow.EtaFlowHandler._test_url",
        return_value=False,
    ):
        yield
# Here we simiulate a successful config flow from the backend.
# Note that we use the `bypass_get_data` fixture here because
# we want the config flow validation to succeed during the test.


async def test_successful_config_flow(hass, bypass_test_url_fixture):
    """Test a successful config flow."""
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    # If a user were to enter `host` for host and `port`
    # for port, it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG
    )
    # Check that the config flow shows the select_entities form as the second step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "select_entities"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CHOOSEN_ENTITIES: ["sensor1", "sensor3"]}
    )
    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == "ETA at 192.168.178.68"
    print(result["data"])
    result_data_dict = MOCK_CONFIG
    result_data_dict[FLOAT_DICT] = FLOAT_DICT_CONFIG
    result_data_dict[CHOOSEN_ENTITIES] = ["sensor1", "sensor3"]

    assert result["data"] == result_data_dict
    assert result["result"]


# In this case, we want to simulate a failure during the config flow.
async def test_failed_config_flow(hass, throw_error_test_url_fixture):
    """Test a failed config flow due to credential validation failure."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: "host", CONF_PORT: "port"}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["errors"] == {"base": "url_broken"}

# Our config flow also has an options flow, so we must test it as well.
# async def test_options_flow(hass):
#     """Test an options flow."""
#     # Create a new MockConfigEntry and add to HASS (we're bypassing config
#     # flow entirely)
#     entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
#     entry.add_to_hass(hass)
#
#     # Initialize an options flow
#     result = await hass.config_entries.options.async_init(entry.entry_id)
#
#     # Verify that the first options step is a user form
#     assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
#     assert result["step_id"] == "user"
#
#     # Enter some fake data into the form
#     result = await hass.config_entries.options.async_configure(
#         result["flow_id"],
#         user_input={platform: platform != SENSOR for platform in PLATFORMS},
#     )
#
#     # Verify that the flow finishes
#     assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
#     assert result["title"] == "test_username"
#
#     # Verify that the options were updated
#     assert entry.options == {BINARY_SENSOR: True, SENSOR: False, SWITCH: True}
