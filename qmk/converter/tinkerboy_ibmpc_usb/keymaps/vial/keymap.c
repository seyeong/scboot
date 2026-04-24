/*
 * Keymap verified against live device via Vial HID protocol.
 * Matrix: 8 rows x 16 cols, 2 layers.
 */
#include QMK_KEYBOARD_H

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [0] = LAYOUT(
        KC_INT4, KC_WSTP, KC_WFWD, KC_WBAK, KC_A,    KC_B,    KC_C,    KC_D,    KC_E,    KC_F,    KC_G,    KC_H,    KC_I,    KC_J,    KC_K,    KC_L,
        KC_M,    KC_N,    KC_O,    KC_P,    KC_Q,    KC_R,    KC_S,    KC_T,    KC_U,    KC_V,    KC_W,    KC_X,    KC_Y,    KC_Z,    KC_1,    KC_2,
        KC_3,    KC_4,    KC_5,    KC_6,    KC_7,    KC_8,    KC_9,    KC_0,    KC_ENT,  KC_ESC,  KC_BSPC, KC_TAB,  KC_SPC,  KC_MINS, KC_EQL,  KC_LBRC,
        KC_RBRC, KC_BSLS, KC_NUHS, KC_SCLN, KC_QUOT, KC_GRV,  KC_COMM, KC_DOT,  KC_SLSH, KC_CAPS, KC_F1,   KC_F2,   KC_F3,   KC_F4,   KC_F5,   KC_F6,
        KC_F7,   KC_F8,   KC_F9,   KC_F10,  KC_F11,  KC_F12,  KC_PSCR, KC_SCRL, KC_PAUS, KC_INS,  KC_HOME, KC_PGUP, KC_DEL,  KC_APP,  KC_PGDN, KC_RGHT,
        KC_LEFT, KC_DOWN, KC_UP,   KC_NUM,  KC_PSLS, KC_PAST, KC_PMNS, KC_PPLS, KC_PENT, KC_P1,   KC_P2,   KC_P3,   KC_P4,   KC_P5,   KC_P6,   KC_P7,
        KC_P8,   KC_P9,   KC_P0,   KC_PDOT, KC_NUBS, KC_END,  KC_INT1, KC_PEQL, KC_F13,  KC_F14,  KC_F15,  KC_F16,  KC_F17,  KC_F18,  KC_F19,  KC_F20,
        KC_F21,  KC_F22,  KC_F23,  KC_F24,  KC_INT5, KC_INT3, KC_LNG1, KC_LNG2, KC_LCTL, KC_LSFT, KC_LALT, KC_RCTL, KC_LGUI, KC_RSFT, KC_RALT, KC_RGUI
    ),

    [1] = LAYOUT(
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______
    ),
};
