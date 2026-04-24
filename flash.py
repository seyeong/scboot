#!/usr/bin/env python3
"""Flash firmware to Soarer's Converter via bootloadHID."""

import sys
import time
import subprocess
import hid
from scboot import boot, ExitCode

BOOTLOADER_VID = 0x16C0
BOOTLOADER_PID = 0x05DF


def wait_for_bootloader(timeout=15):
    print("waiting for bootloader: ", end="", flush=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        for dev in hid.enumerate(BOOTLOADER_VID, BOOTLOADER_PID):
            if "HIDBoot" in dev.get("product_string", "") or dev.get("manufacturer_string", "") == "obdev.at":
                print("found")
                return True
        time.sleep(0.5)
    print("timeout")
    return False


def flash(hex_file):
    print("flashing: ", end="", flush=True)
    r = subprocess.run(
        ["sudo", "bootloadHID", "-r", hex_file],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print("failed")
        if r.stderr:
            print(r.stderr)
        if r.stdout:
            print(r.stdout)
        return False
    print("ok")
    if r.stderr:
        print(r.stderr.strip())
    return True


def main():
    if len(sys.argv) != 2:
        print("usage: flash <firmware.hex>")
        return 1

    hex_file = sys.argv[1]

    rc = boot()
    if rc != ExitCode.SUCCESS:
        return rc

    if not wait_for_bootloader():
        return 2

    if not flash(hex_file):
        return 3

    print("done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
