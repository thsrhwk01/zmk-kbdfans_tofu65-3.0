/* SPDX-License-Identifier: MIT */
#include <zephyr/init.h>
#include "unicore_registers.h"

/* Runs before .data/.bss initialization: no globals or kernel services here. */
void z_arm_platform_init(void) {
    __asm__ volatile("cpsid i" ::: "memory");
    UNICORE_REG(0xe000e010u) = 0; /* SysTick CTRL */
    UNICORE_REG(0xe000e014u) = 0;
    UNICORE_REG(0xe000e018u) = 0;
    UNICORE_REG(0xe000ed04u) = (1u << 27) | (1u << 25);
    UNICORE_REG(UNICORE_RCC + 0x10) |= 1u << 23; /* USB peripheral reset */
    UNICORE_REG(UNICORE_RCC + 0x10) &= ~(1u << 23);
    UNICORE_REG(UNICORE_RCC + 0x18) |= (1u << 2) | (1u << 3);
    (void)UNICORE_REG(UNICORE_RCC + 0x18);
    /* Match stock PA12 detach before pinctrl restores USB ownership. */
    unicore_gpio_write(UNICORE_GPIOA, 12, 0);
    unicore_gpio_mode(UNICORE_GPIOA, 12, 3);
    for (volatile unsigned int i = 0; i < 800000; i++) {
        __asm__ volatile("nop");
    }
    __asm__ volatile("dsb sy\n\tisb sy" ::: "memory");
}

static int usb_connect(void) {
    /* Stock USB init ends with PB9 ODR low; keep scanner's input-pull mode. */
    unicore_gpio_write(UNICORE_GPIOB, 9, 0);
    return 0;
}
SYS_INIT(usb_connect, APPLICATION, 0);

