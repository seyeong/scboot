# scboot

Cross-platform Python port of `scboot.exe` — puts Soarer's Converter into bootloader mode for firmware flashing.

The original `scboot.exe` is a Windows-only CLI tool. This Python port works on macOS, Linux, and Windows.

This repo also contains the QMK/Vial firmware and config files for the [tinkerBOY IBM PC keyboard to USB converter](https://www.tinkerboy.xyz/updating-the-soarers-converteratmega32u4-to-qmk-firmware-with-vial-support/) (ATmega32U4). The boot tool (`scboot.py`, `flash.py`) is generic and works with any Soarer's Converter.

## Requirements

- Python 3
- [hidapi](https://pypi.org/project/hidapi/)
- [bootloadHID](https://www.obdev.at/products/vusb/bootloadhid.html) (for flashing, [source](https://github.com/whiteneon/bootloadHID))

```
pip install hidapi
brew install bootloadhid  # macOS only
```

## Flashing QMK/Vial Firmware (macOS)

### 1. Enter bootloader mode and flash

```bash
python flash.py firmware/converter_tinkerboy_ibmpc_usb_atmega32u4_atmel_dfu_vial.hex
```

Expected output:

```
scboot v1.10 (Python port)
scboot: looking for Soarer's Converter: found
scboot: sending boot request: device: ok
waiting for bootloader: found
flashing: ok
Page size   = 128 (0x80)
Device size = 32768 (0x8000); 30720 bytes remaining
Uploading 28160 (0x6e00) bytes starting at 0 (0x0)
0x06d80 ... 0x06e00
done!
```

Or manually:

```bash
python scboot.py && sleep 2 && sudo bootloadHID -r firmware/converter_tinkerboy_ibmpc_usb_atmega32u4_atmel_dfu_vial.hex
```

### 2. Verify

After flashing, the adapter should re-enumerate as the new firmware. Check with:

```bash
system_profiler SPUSBDataType | grep -A5 "tinkeBOY\|TINKERBOY"
```

### 3. Customize keymap

Open [Vial](https://get.vial.today/) to customize the keymap live over USB.

## Bootloader Notes

Soarer's Converter uses the **bootloadHID** bootloader (`16C0:05DF`), not Atmel DFU. The `scboot` command enters this bootloader — the adapter re-enumerates as "HIDBoot" by obdev.at.

- `scboot` enters **Soarer's bootloader** (for Soarer firmware updates via `scwr`)
- The Soarer bootloader then jumps to **bootloadHID** (the chip's USB bootloader)
- Use `bootloadHID` (not `dfu-programmer`) to flash

`sudo` is required on macOS to detach the kernel HID driver.

### Flashing on Windows

Use the original `scboot.exe` to enter bootloader mode, then flash with [Atmel Flip](https://www.microchip.com/en-us/development-tool/flip) or the bootloadHID Windows tool.

### Going back to Soarer's firmware

Flash the original Soarer firmware hex the same way. The bootloadHID bootloader is not overwritten during flashing.

## How It Works

The script communicates with Soarer's Converter over USB HID:

| Parameter  | Value    |
|------------|----------|
| VID        | `0x16C0` |
| PID        | `0x047D` |
| Usage Page | `0xFF99` |
| Usage      | `0x2468` |

It sends a 64-byte HID report with byte 0 set to `0x04` (boot command) and expects a response with byte 0 set to `0x02` (success). The adapter then resets into bootloadHID mode.

## Files

```
scboot/
├── scboot.py                  # Enter bootloader mode
├── flash.py                   # Boot + flash in one step
├── README.md
├── REVERSE_ENGINEERING.md
├── firmware/
│   ├── *.hex                  # QMK/Vial firmware
│   └── ibmpckb.json           # Vial keyboard definition
├── original/
│   ├── scboot.exe             # Original Windows binary (v1.10)
│   └── rawhid.dll             # PJRC raw HID library
├── tools/
│   └── vial_read.py           # Read config from live device
└── qmk/                       # QMK config files for rebuilding
    └── converter/tinkerboy_ibmpc_usb/
```
