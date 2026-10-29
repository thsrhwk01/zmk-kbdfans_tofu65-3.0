/* SPDX-License-Identifier: MIT */
#include <zephyr/init.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/util.h>
#include <zmk/event_manager.h>
#include <zmk/events/hid_indicators_changed.h>
#include "unicore_registers.h"

BUILD_ASSERT(CONFIG_SYS_CLOCK_HW_CYCLES_PER_SEC == 48000000,
             "Recovered RGB pulse timing requires 48 MHz");

extern void unicore_rgb_byte(uint8_t value);

static void set_caps(bool on) {
    /* Start/end with a latch interval. USB IRQs remain enabled during waits. */
    k_busy_wait(300);
    unsigned int key = irq_lock();
    /* Stock uses GRB byte order, one RGB LED, and a PB14 discrete indicator. */
    unicore_gpio_write(UNICORE_GPIOB, 14, on);
    unicore_rgb_byte(on ? 32 : 0); /* green: modest white brightness */
    unicore_rgb_byte(on ? 32 : 0); /* red */
    unicore_rgb_byte(on ? 32 : 0); /* blue */
    irq_unlock(key);
    k_busy_wait(300);
}

static int caps_init(void) {
    unsigned int key = irq_lock();
    /* Match stock's PA8/PB14 off initialization; PB15 carries RGB data. */
    unicore_gpio_write(UNICORE_GPIOA, 8, 0);
    unicore_gpio_mode(UNICORE_GPIOA, 8, 3);
    unicore_gpio_write(UNICORE_GPIOB, 14, 0);
    unicore_gpio_mode(UNICORE_GPIOB, 14, 3);
    unicore_gpio_write(UNICORE_GPIOB, 15, 0);
    unicore_gpio_mode(UNICORE_GPIOB, 15, 3);
    irq_unlock(key);
    set_caps(false); /* Explicit black frame clears a bootloader-latched color. */
    return 0;
}

/* Scanner GPIO init is POST_KERNEL 90; USB connects at APPLICATION 94. */
SYS_INIT(caps_init, POST_KERNEL, 91);

static int caps_changed(const zmk_event_t *event) {
    const struct zmk_hid_indicators_changed *changed =
        as_zmk_hid_indicators_changed(event);
    if (changed) {
        /* HID LED output report bit 1 is Caps Lock, not Num/Scroll Lock. */
        set_caps((changed->indicators & BIT(1)) != 0);
    }
    return ZMK_EV_EVENT_BUBBLE;
}

ZMK_LISTENER(tofu_caps_indicator, caps_changed);
ZMK_SUBSCRIPTION(tofu_caps_indicator, zmk_hid_indicators_changed);
