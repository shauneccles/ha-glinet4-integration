"""Unit tests for client interface-type resolution (issue #139).

These tests exercise the pure helpers in ``custom_components/glinet/utils.py``
and require no Home Assistant runtime.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "custom_components" / "glinet"),
)
from utils import (  # noqa: E402
    DeviceInterfaceType,
    interface_type_from_client,
)


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
    assert interface_type_from_client({"iface": iface}) is expected


@pytest.mark.parametrize(
    "dev_info",
    [
        {},  # no iface key at all
        {"iface": ""},
        {"iface": None},
        {"iface": "something-new"},  # future/unknown interface
        {"type": 99},  # out-of-range legacy index must not crash
    ],
)
def test_unknown_iface_is_safe(dev_info: dict) -> None:
    """Unknown/missing interfaces resolve to UNKNOWN, never raise."""
    assert interface_type_from_client(dev_info) is DeviceInterfaceType.UNKNOWN
