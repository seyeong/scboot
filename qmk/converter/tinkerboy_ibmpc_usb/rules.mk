MCU = atmega32u4
BOOTLOADER = atmel-dfu

SRC += ibmpc_usb.cpp
SRC += ibmpc.cpp

NKRO_ENABLE = yes
MOUSEKEY_ENABLE = yes
EXTRAKEY_ENABLE = yes
CONSOLE_ENABLE = no
COMMAND_ENABLE = yes
VIAL_ENABLE = yes
VIA_ENABLE = yes
