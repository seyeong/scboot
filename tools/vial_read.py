#!/usr/bin/env python3
"""Read Vial keyboard config from a connected device."""

import sys
import json
import struct
import lzma
import zlib
import hid

VID = 0xFEED
PID = 0x6536
USAGE_PAGE = 0xFF60
USAGE = 0x61
MSG_LEN = 32

# Vial protocol commands
CMD_VIA_GET_PROTOCOL_VERSION = 0x01
CMD_VIA_GET_KEYBOARD_VALUE = 0x02
CMD_VIA_DYNAMIC_KEYMAP_GET_KEYCODE = 0x04
CMD_VIA_DYNAMIC_KEYMAP_GET_LAYER_COUNT = 0x11
CMD_VIA_DYNAMIC_KEYMAP_GET_BUFFER = 0x12
CMD_VIAL_PREFIX = 0xFE
VIAL_GET_KEYBOARD_ID = 0x00
VIAL_GET_SIZE = 0x01
VIAL_GET_DEFINITION = 0x02


def find_device():
    for dev in hid.enumerate(VID, PID):
        if dev.get("usage_page") == USAGE_PAGE and dev.get("usage") == USAGE:
            return dev["path"]
    return None


def send(device, data):
    msg = [0x00] + list(data) + [0x00] * (MSG_LEN - len(data))
    device.write(msg)
    return device.read(MSG_LEN, timeout_ms=1000)


def get_protocol_version(device):
    resp = send(device, [CMD_VIA_GET_PROTOCOL_VERSION])
    if resp:
        return (resp[1] << 8) | resp[2]
    return None


def get_vial_keyboard_id(device):
    resp = send(device, [CMD_VIAL_PREFIX, VIAL_GET_KEYBOARD_ID])
    if resp:
        vial_protocol = struct.unpack("<I", bytes(resp[0:4]))[0]
        uid = struct.unpack("<Q", bytes(resp[4:12]))[0]
        return vial_protocol, uid
    return None, None


def get_vial_definition(device):
    resp = send(device, [CMD_VIAL_PREFIX, VIAL_GET_SIZE])
    if not resp:
        return None
    size = struct.unpack("<I", bytes(resp[0:4]))[0]
    print(f"  Compressed definition size: {size} bytes")

    data = b""
    page = 0
    while len(data) < size:
        resp = send(device, [CMD_VIAL_PREFIX, VIAL_GET_DEFINITION, page & 0xFF, (page >> 8) & 0xFF])
        if not resp:
            print(f"  Failed at page {page}")
            break
        data += bytes(resp)
        page += 1

    data = data[:size]
    print(f"  Fetched {len(data)} bytes in {page} pages")

    # Try XZ/LZMA first (magic: fd 37 7a 58 5a 00)
    if data[:6] == b'\xfd7zXZ\x00':
        try:
            decompressed = lzma.decompress(data)
            return json.loads(decompressed.decode('utf-8'))
        except Exception as e:
            print(f"  XZ decompress failed: {e}")

    # Try zlib
    for wbits in [15, -15, 31, 47]:
        try:
            decompressed = zlib.decompress(data, wbits)
            return json.loads(decompressed.decode('utf-8'))
        except:
            pass

    with open("vial_definition_raw.bin", "wb") as f:
        f.write(data)
    print(f"  Saved raw data to vial_definition_raw.bin")
    return None


def get_layer_count(device):
    resp = send(device, [CMD_VIA_DYNAMIC_KEYMAP_GET_LAYER_COUNT])
    if resp:
        return resp[1]
    return None


def get_keymap_buffer(device, offset, size):
    resp = send(device, [CMD_VIA_DYNAMIC_KEYMAP_GET_BUFFER,
                         (offset >> 8) & 0xFF, offset & 0xFF, size])
    if resp:
        return bytes(resp[4:4 + size])
    return None


KC = {
    0x0000: "____", 0x0001: "TRNS",
    0x0004: "A", 0x0005: "B", 0x0006: "C", 0x0007: "D",
    0x0008: "E", 0x0009: "F", 0x000A: "G", 0x000B: "H",
    0x000C: "I", 0x000D: "J", 0x000E: "K", 0x000F: "L",
    0x0010: "M", 0x0011: "N", 0x0012: "O", 0x0013: "P",
    0x0014: "Q", 0x0015: "R", 0x0016: "S", 0x0017: "T",
    0x0018: "U", 0x0019: "V", 0x001A: "W", 0x001B: "X",
    0x001C: "Y", 0x001D: "Z",
    0x001E: "1", 0x001F: "2", 0x0020: "3", 0x0021: "4",
    0x0022: "5", 0x0023: "6", 0x0024: "7", 0x0025: "8",
    0x0026: "9", 0x0027: "0",
    0x0028: "ENT", 0x0029: "ESC", 0x002A: "BSPC", 0x002B: "TAB",
    0x002C: "SPC", 0x002D: "MINS", 0x002E: "EQL", 0x002F: "LBRC",
    0x0030: "RBRC", 0x0031: "BSLS", 0x0032: "NUHS", 0x0033: "SCLN",
    0x0034: "QUOT", 0x0035: "GRV", 0x0036: "COMM", 0x0037: "DOT",
    0x0038: "SLSH", 0x0039: "CAPS",
    0x003A: "F1", 0x003B: "F2", 0x003C: "F3", 0x003D: "F4",
    0x003E: "F5", 0x003F: "F6", 0x0040: "F7", 0x0041: "F8",
    0x0042: "F9", 0x0043: "F10", 0x0044: "F11", 0x0045: "F12",
    0x0046: "PSCR", 0x0047: "SCRL", 0x0048: "PAUS",
    0x0049: "INS", 0x004A: "HOME", 0x004B: "PGUP",
    0x004C: "DEL", 0x004D: "END", 0x004E: "PGDN",
    0x004F: "RGHT", 0x0050: "LEFT", 0x0051: "DOWN", 0x0052: "UP",
    0x0053: "NUM", 0x0054: "PSLS", 0x0055: "PAST", 0x0056: "PMNS",
    0x0057: "PPLS", 0x0058: "PENT",
    0x0059: "P1", 0x005A: "P2", 0x005B: "P3", 0x005C: "P4",
    0x005D: "P5", 0x005E: "P6", 0x005F: "P7", 0x0060: "P8",
    0x0061: "P9", 0x0062: "P0", 0x0063: "PDOT",
    0x0064: "NUBS", 0x0065: "APP", 0x0067: "PEQL",
    0x0068: "F13", 0x0069: "F14", 0x006A: "F15", 0x006B: "F16",
    0x006C: "F17", 0x006D: "F18", 0x006E: "F19", 0x006F: "F20",
    0x0070: "F21", 0x0071: "F22", 0x0072: "F23", 0x0073: "F24",
    0x00E0: "LCTL", 0x00E1: "LSFT", 0x00E2: "LALT", 0x00E3: "LGUI",
    0x00E4: "RCTL", 0x00E5: "RSFT", 0x00E6: "RALT", 0x00E7: "RGUI",
}


def kc_name(val):
    if val in KC:
        return KC[val]
    if (val & 0xFF00) == 0x5D00:
        return f"MO({val & 0xFF})"
    if (val & 0xFF00) == 0x5C00:
        return f"TG({val & 0xFF})"
    return f"0x{val:04X}"


def main():
    print("Looking for Vial device: ", end="", flush=True)
    path = find_device()
    if not path:
        print("not found")
        return 1
    print("found")

    device = hid.device()
    device.open_path(path)

    # Protocol version
    ver = get_protocol_version(device)
    print(f"\nVIA protocol version: {ver}")

    # Vial info
    vial_proto, uid = get_vial_keyboard_id(device)
    print(f"Vial protocol version: {vial_proto}")
    print(f"Vial UID: 0x{uid:016X}")

    # Keyboard definition
    print(f"\nFetching keyboard definition...")
    definition = get_vial_definition(device)
    if definition:
        print(f"  Name: {definition.get('name', '?')}")
        print(f"  VID:PID: {definition.get('vendorId', '?')}:{definition.get('productId', '?')}")
        matrix = definition.get('matrix', {})
        rows = matrix.get('rows', '?')
        cols = matrix.get('cols', '?')
        print(f"  Matrix: {rows} x {cols}")
        labels = definition.get('layouts', {}).get('labels', [])
        if labels:
            print(f"  Layout options:")
            for group in labels:
                if isinstance(group, list):
                    print(f"    {group[0]}: {', '.join(group[1:])}")

        with open("vial_definition_live.json", "w") as f:
            json.dump(definition, f, indent=2)
        print(f"  Saved to vial_definition_live.json")
    else:
        print("  Failed to fetch definition")
        rows, cols = 8, 16

    # Layer count
    layers = get_layer_count(device)
    print(f"\nDynamic keymap layers: {layers}")

    # Read keymap
    if isinstance(rows, int) and isinstance(cols, int) and layers:
        print(f"\nReading keymap ({layers} layers x {rows} rows x {cols} cols)...")
        layer_size = rows * cols * 2

        for layer in range(layers):
            print(f"\n  Layer {layer}:")
            keymap = b""
            offset = layer * layer_size
            remaining = layer_size
            while remaining > 0:
                chunk = min(28, remaining)
                buf = get_keymap_buffer(device, offset, chunk)
                if buf is None:
                    print("    Error reading keymap")
                    break
                keymap += buf
                offset += chunk
                remaining -= chunk

            if len(keymap) >= layer_size:
                all_trns = all(keymap[i] | (keymap[i+1] << 8) == 0x0001
                               for i in range(0, layer_size, 2)
                               if i+1 < len(keymap))
                if all_trns and layer > 0:
                    print("    (all transparent)")
                    continue

                for r in range(rows):
                    row_str = f"    R{r:<2} |"
                    for c in range(cols):
                        idx = (r * cols + c) * 2
                        val = (keymap[idx] << 8) | keymap[idx + 1]
                        row_str += f" {kc_name(val):>6}"
                    print(row_str)

    device.close()
    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
