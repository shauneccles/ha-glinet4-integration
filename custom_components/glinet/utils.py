"""Utility functions for GL-iNet routers."""

from __future__ import annotations

from enum import StrEnum


class DeviceInterfaceType(StrEnum):
    """The interface a client is connected to the router through."""

    WIFI_24 = "2.4GHz"
    WIFI_5 = "5GHz"
    WIFI_6 = "6GHz"
    WIFI_24_GUEST = "2.4GHz Guest"
    WIFI_5_GUEST = "5GHz Guest"
    WIFI_6_GUEST = "6GHz Guest"
    MLO = "MLO"
    MLO_GUEST = "MLO Guest"
    LAN = "LAN"
    DONGLE = "Dongle"
    BYPASS_ROUTE = "Bypass Route"
    UNKNOWN = "Unknown"


# Maps the self-describing ``iface`` string the router reports for each client
# to a DeviceInterfaceType. Keys are lower-cased for case-insensitive matching.
# Known values come from observed API responses ("2.4G", "5G", "cable") plus
# GL-iNet's documented band names. Anything not listed falls through to the
# heuristics in interface_type_from_client() and ultimately to UNKNOWN.
_IFACE_MAP: dict[str, DeviceInterfaceType] = {
    "2.4g": DeviceInterfaceType.WIFI_24,
    "5g": DeviceInterfaceType.WIFI_5,
    "6g": DeviceInterfaceType.WIFI_6,
    "mlo": DeviceInterfaceType.MLO,
    "cable": DeviceInterfaceType.LAN,
    "wired": DeviceInterfaceType.LAN,
    "lan": DeviceInterfaceType.LAN,
}


def interface_type_from_client(dev_info: dict) -> DeviceInterfaceType:
    """Best-effort resolution of the interface a client is connected through.

    Prefers the human-readable ``iface`` string the router returns (e.g.
    "2.4G", "5G", "6G", "MLO", "cable"). Previously the integer ``type`` field
    was used as a positional index into the enum, which silently mislabelled -
    or with an out-of-range value crashed - newer interfaces such as MLO and
    6GHz. Unrecognised interfaces resolve to UNKNOWN so that a device is always
    tracked, never dropped, regardless of how it is connected.
    """
    iface = str(dev_info.get("iface") or "").strip().lower()
    if iface in _IFACE_MAP:
        return _IFACE_MAP[iface]
    # Guest networks are reported with a "guest" qualifier on some firmware.
    if "guest" in iface:
        if "2.4" in iface:
            return DeviceInterfaceType.WIFI_24_GUEST
        if "6" in iface:
            return DeviceInterfaceType.WIFI_6_GUEST
        if "mlo" in iface:
            return DeviceInterfaceType.MLO_GUEST
        if "5" in iface:
            return DeviceInterfaceType.WIFI_5_GUEST
    if "mlo" in iface:
        return DeviceInterfaceType.MLO
    return DeviceInterfaceType.UNKNOWN


def adjust_mac(mac: str, delta: int, sep: str = ":") -> str:
    """Increment a MAC address by 1.

    This is helpful because GL-iNet devices' LAN ports have a mac of factory_mac + 1
    but this is not found in the API
    :param mac: Original MAC address (e.g. "00:1A:2B:3C:4D:5E" or "00-1A-2B-3C-4D-5E").
    :param sep: Separator to use in the output (default is ':').
    :return: Incremented MAC address as a string.
    """
    # Remove common separators and convert to integer
    hex_str = mac.replace(sep, "").replace("-", "").lower()
    value = int(hex_str, 16)

    # Increment and wrap around at 48 bits
    value = (value + delta) & ((1 << 48) - 1)

    # Format back to hexadecimal, ensuring six bytes (12 hex digits)
    new_hex = f"{value:012x}"

    # Reinsert the separator every two hex digits
    return sep.join(new_hex[i : i + 2] for i in range(0, 12, 2)).lower()
