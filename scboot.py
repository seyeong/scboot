#!/usr/bin/env python3
"""scboot — Put Soarer's Converter into bootloader mode."""

import sys
from enum import IntEnum
import hid

VID = 0x16C0
PID = 0x047D
USAGE_PAGE = 0xFF99
USAGE = 0x2468

BOOT_COMMAND = 0x04
BOOT_OK = 0x02
REPORT_SIZE = 64


class ExitCode(IntEnum):
    SUCCESS = 0
    BAD_USAGE = 1
    SEND_FAILED = 2
    NO_RESPONSE = 3
    BAD_RESPONSE = 4
    NOT_FOUND = -1


def find_device():
    for dev in hid.enumerate(VID, PID):
        if dev.get("usage") == USAGE and dev.get("usage_page") == USAGE_PAGE:
            return dev["path"]
    return None


def boot():
    """Enter bootloader mode. Returns 0 on success, error code on failure."""
    print("scboot: looking for Soarer's Converter: ", end="", flush=True)
    path = find_device()
    if path is None:
        print("not found")
        return ExitCode.NOT_FOUND
    print("found")

    device = hid.device()
    device.open_path(path)

    print("scboot: sending boot request: ", end="", flush=True)
    buf = [BOOT_COMMAND] + [0] * (REPORT_SIZE - 1)
    written = device.write(buf)
    if written < 0:
        print("failed")
        device.close()
        return ExitCode.SEND_FAILED

    print("device: ", end="", flush=True)
    response = device.read(REPORT_SIZE, timeout_ms=220)
    if not response:
        print("failed to respond")
        device.close()
        return ExitCode.NO_RESPONSE

    if response[0] != BOOT_OK:
        print("not ok")
        device.close()
        return ExitCode.BAD_RESPONSE

    print("ok")
    device.close()
    return ExitCode.SUCCESS


def main():
    print("scboot v1.10 (Python port)")

    if len(sys.argv) != 1:
        print("usage: scboot")
        return ExitCode.BAD_USAGE

    return boot()


if __name__ == "__main__":
    sys.exit(main())
