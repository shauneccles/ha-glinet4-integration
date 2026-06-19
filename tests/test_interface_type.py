"""Unit tests for client interface-type resolution (issue #139).

These tests exercise the pure helpers in ``custom_components/glinet/utils.py``
and require no Home Assistant runtime.
"""

from __future__ import annotations

import pytest

# Importable via the path set up in conftest.py (no Home Assistant required).
from utils import DeviceInterfaceType, interface_type_from_client


def test_enum_has_no_aliased_members() -> None:
    """Every member must have a unique value.

    A duplicate value previously collapsed ``UNKNOWN``/``UNKNOWN2`` into an
    alias, which shifted the positional index used for MLO/6GHz and either
    mislabelled or crashed on those interfaces.
    """
    values = [member.value for member in DeviceInterfaceType]
    assert len(values) == len(set(values))
    assert len(list(DeviceInterfaceType)) == 12


@pytest.mark.parametrize(
    ("iface", "expected"),
    [
        ("2.4G", DeviceInterfaceType.WIFI_24),
        ("5G", DeviceInterfaceType.WIFI_5),
        ("6G", DeviceInterfaceType.WIFI_6),
        ("MLO", DeviceInterfaceType.MLO),
        ("cable", DeviceInterfaceType.LAN),
        ("CABLE", DeviceInterfaceType.LAN),  # case-insensitive
        (" 5G ", DeviceInterfaceType.WIFI_5),  # whitespace tolerant
    ],
)
def test_known_ifaces(iface: str, expected: DeviceInterfaceType) -> None:
    """Known iface strings map to the expected interface type."""
    assert interface_type_from_client({"iface": iface}) is expected


@pytest.mark.parametrize(
    ("iface", "expected"),
    [
        ("guest-2.4G", DeviceInterfaceType.WIFI_24_GUEST),
        ("guest5G", DeviceInterfaceType.WIFI_5_GUEST),
        ("guest-6G", DeviceInterfaceType.WIFI_6_GUEST),
        ("guest-mlo", DeviceInterfaceType.MLO_GUEST),
    ],
)
def test_guest_ifaces(iface: str, expected: DeviceInterfaceType) -> None:
    """Guest-network iface strings map to the matching guest interface type."""
    assert interface_type_from_client({"iface": iface}) is expected


@pytest.mark.parametrize(
    "dev_info",
    [
        {},  # no iface key at all
        {"iface": ""},
        {"iface": None},
        {"iface": "something-new"},  # future/unknown interface
        {"type": 99},  # out-of-range legacy index must not crash
        {"type": "not-an-int"},  # non-numeric legacy code must not crash
        {"type": None},
    ],
)
def test_unknown_iface_is_safe(dev_info: dict) -> None:
    """Unknown/missing interfaces resolve to UNKNOWN, never raise."""
    assert interface_type_from_client(dev_info) is DeviceInterfaceType.UNKNOWN


@pytest.mark.parametrize(
    ("type_code", "expected"),
    [
        (0, DeviceInterfaceType.WIFI_24),
        (1, DeviceInterfaceType.WIFI_5),
        (2, DeviceInterfaceType.LAN),
        (9, DeviceInterfaceType.MLO),
        (11, DeviceInterfaceType.WIFI_6),
        (12, DeviceInterfaceType.WIFI_6_GUEST),  # the index #143 crashed on
    ],
)
def test_legacy_type_code_fallback(
    type_code: int, expected: DeviceInterfaceType
) -> None:
    """When no iface string is present, the integer code is used (issues #143/#144)."""
    assert interface_type_from_client({"type": type_code}) is expected


def test_iface_takes_precedence_over_type_code() -> None:
    """A recognised iface string wins over the legacy integer code."""
    # iface says 5GHz, stale/contradictory type code says LAN -> trust iface.
    assert (
        interface_type_from_client({"iface": "5G", "type": 2})
        is DeviceInterfaceType.WIFI_5
    )
