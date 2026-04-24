# scboot.exe v1.10 — Reverse Engineering

## Overview

`scboot.exe` is a Windows CLI tool that puts **Soarer's Converter** (a USB keyboard protocol converter) into bootloader mode for firmware updates.

- **Binary**: PE32 (32-bit x86), built with Microsoft Visual C++
- **Dependency**: `rawhid.dll` — PJRC raw USB HID library (source path: `d:\xtkbk\pjrc\usb_raw_hid\`)

## USB Device Identification

| Parameter  | Value            | Notes                        |
|------------|------------------|------------------------------|
| VID        | `0x16C0` (5824)  | Teensy/PJRC vendor-specific       |
| PID        | `0x047D` (1149)  | Soarer's Converter product ID     |
| Usage Page | `0xFF99` (65433) | Vendor-defined usage page         |
| Usage      | `0x2468` (9320)  | Soarer's Converter usage          |

## Protocol

### Boot Request

A 64-byte USB HID report is sent to the device:

```
Byte[0] = 0x04   (boot command)
Byte[1..63] = 0x00
```

Timeout: 100ms

### Boot Response

A 64-byte USB HID report is expected back:

```
Byte[0] = 0x02   (success)
```

Timeout: 220ms

If `response[0] != 0x02`, the boot request is considered failed.

## Program Flow

```
1. Print "scboot v1.10"
2. Validate no arguments are passed (argc == 1)
3. Print "scboot: looking for Soarer's Converter: "
4. Call rawhid_open(1, vid=0x16C0, pid=0x047D, usage_page=0xFF99, usage=0x2468)
   - If not found → print "not found", exit -1
   - If found → print "found"
5. Print "scboot: sending boot request: "
6. Send 64-byte packet [0x04, 0x00...] via rawhid_send (timeout 100ms)
   - If send fails → print "failed", set error code 2
7. Print "device: "
8. Receive 64-byte response via rawhid_recv (timeout 220ms)
   - If recv fails → print "failed to respond", set error code 3
9. Check response[0] == 0x02
   - If not 0x02 → print "not ok", set error code 4
   - If 0x02 → print "ok"
10. Call rawhid_close(0), exit
```

## rawhid.dll API

Exported functions used by scboot.exe:

| Function       | Signature (reconstructed)                                              |
|----------------|------------------------------------------------------------------------|
| `rawhid_open`  | `int rawhid_open(int max, int vid, int pid, int usage_page, int usage)` |
| `rawhid_send`  | `int rawhid_send(int num, void *buf, int len, int timeout)`            |
| `rawhid_recv`  | `int rawhid_recv(int num, void *buf, int len, int timeout)`            |
| `rawhid_close` | `void rawhid_close(int num)`                                           |

The DLL uses Windows HID APIs (`HID.DLL`, `SETUPAPI.dll`) to enumerate and communicate with USB HID devices.

## Error Codes

| Code | Meaning                                  |
|------|------------------------------------------|
| 0    | Success                                  |
| 2    | Failed to send boot request              |
| 3    | Device failed to respond                 |
| 4    | Device responded with unexpected status  |
