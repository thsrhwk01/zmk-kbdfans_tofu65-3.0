/* SPDX-License-Identifier: MIT */
#define DT_DRV_COMPAT kbdfans_unicore_bootloader
#include <zephyr/device.h>
#include <zephyr/init.h>
#include <zephyr/irq.h>
#include <zephyr/sys/util.h>
#include <drivers/behavior.h>
#include <zmk/behavior.h>
#include "unicore_registers.h"

static int pressed(struct zmk_behavior_binding *binding,
                   struct zmk_behavior_binding_event event) {
    ARG_UNUSED(binding);
    ARG_UNUSED(event);
    (void)irq_lock();
    UNICORE_REG(0x20004000u) = 0x9d5bfc2bu;
    __asm__ volatile("dsb sy" ::: "memory");
    UNICORE_REG(0xe000ed0cu) = 0x05fa0004u;
    __asm__ volatile("dsb sy" ::: "memory");
    for (;;) {
        __asm__ volatile("nop");
    }
    return ZMK_BEHAVIOR_OPAQUE;
}

static const struct behavior_driver_api api = {
    .binding_pressed = pressed,
    .locality = BEHAVIOR_LOCALITY_CENTRAL,
#if IS_ENABLED(CONFIG_ZMK_BEHAVIOR_METADATA)
    .get_parameter_metadata = zmk_behavior_get_empty_param_metadata,
#endif
};

#define BOOTLOADER_DEFINE(n)                                                                     \
    BEHAVIOR_DT_INST_DEFINE(n, NULL, NULL, NULL, NULL, POST_KERNEL,                               \
                            CONFIG_KERNEL_INIT_PRIORITY_DEFAULT, &api);
DT_INST_FOREACH_STATUS_OKAY(BOOTLOADER_DEFINE)

