/* SPDX-License-Identifier: MIT
 * Protocol recovered from stock 0x0800606C / 0x08006168. Hardware untested.
 */
#define DT_DRV_COMPAT kbdfans_unicore_serial
#include <errno.h>
#include <zephyr/device.h>
#include <zephyr/drivers/kscan.h>
#include <zephyr/init.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>
#include <zephyr/sys/util.h>
#include "unicore_registers.h"
#include "unicore_scan_core.h"

struct unicore_config {
    uint32_t poll_ms;
    uint32_t half_us;
    uint32_t settle_us;
};

struct unicore_data {
    const struct device *dev;
    struct k_work_delayable work;
    kscan_callback_t callback;
    atomic_t enabled;
    bool fill_high;
    bool pull_down;
    struct unicore_filter filter;
};

static void data_output(void *context, bool high) {
    ARG_UNUSED(context);
    unicore_gpio_mode(UNICORE_GPIOB, 13, 3);
    unicore_gpio_write(UNICORE_GPIOB, 13, high);
}

static void data_input(void *context) {
    struct unicore_data *data = context;
    const struct unicore_config *config = data->dev->config;
    unicore_gpio_write(UNICORE_GPIOB, 13, !data->pull_down);
    unicore_gpio_mode(UNICORE_GPIOB, 13, 8);
    k_busy_wait(config->settle_us);
}

static void clock_pulse(void *context) {
    struct unicore_data *data = context;
    const struct unicore_config *config = data->dev->config;
    unicore_gpio_write(UNICORE_GPIOB, 12, 1);
    k_busy_wait(config->half_us);
    unicore_gpio_write(UNICORE_GPIOB, 12, 0);
    k_busy_wait(config->half_us);
}

static bool data_read(void *context) {
    ARG_UNUSED(context);
    return (UNICORE_REG(UNICORE_GPIOB + 8) & (1u << 13)) != 0;
}

static void scan_work(struct k_work *work) {
    struct unicore_data *data = CONTAINER_OF(k_work_delayable_from_work(work),
                                            struct unicore_data, work);
    const struct unicore_config *config = data->dev->config;
    bool active[UNICORE_BITS];
    if (!atomic_get(&data->enabled)) {
        return;
    }
    const struct unicore_bus bus = {
        .context = data, .output = data_output, .input = data_input,
        .pulse = clock_pulse, .read = data_read,
    };
    /* Bound the timing-sensitive scan; callbacks run after restoring IRQs. */
    unsigned int key = irq_lock();
    unicore_sample(&bus, data->fill_high, active);
    irq_unlock(key);
    for (unsigned int i = 0; i < UNICORE_BITS; i++) {
        if (unicore_filter_update(&data->filter, i, active[i]) && data->callback &&
            atomic_get(&data->enabled)) {
            data->callback(data->dev, i / UNICORE_COLS, i % UNICORE_COLS,
                           data->filter.pressed[i]);
        }
    }
    /* Serialize disable against rescheduling. */
    key = irq_lock();
    if (atomic_get(&data->enabled)) {
        k_work_reschedule(&data->work, K_MSEC(config->poll_ms));
    }
    irq_unlock(key);
}

static int configure(const struct device *dev, kscan_callback_t callback) {
    if (!callback) {
        return -EINVAL;
    }
    struct unicore_data *data = dev->data;
    data->callback = callback;
    return 0;
}

static int enable(const struct device *dev) {
    struct unicore_data *data = dev->data;
    if (!data->callback) {
        return -EINVAL;
    }
    atomic_set(&data->enabled, 1);
    k_work_reschedule(&data->work, K_NO_WAIT);
    return 0;
}

static int disable(const struct device *dev) {
    struct unicore_data *data = dev->data;
    atomic_clear(&data->enabled);
    k_work_cancel_delayable(&data->work);
    return 0;
}

static int init(const struct device *dev) {
    struct unicore_data *data = dev->data;
    data->dev = dev;
    k_work_init_delayable(&data->work, scan_work);
    unsigned int key = irq_lock();
    UNICORE_REG(UNICORE_RCC + 0x18) |= (1u << 2) | (1u << 3);
    (void)UNICORE_REG(UNICORE_RCC + 0x18);
    /* Sample the stock polarity strap before the USB connection hook. */
    unicore_gpio_write(UNICORE_GPIOB, 9, 1);
    unicore_gpio_mode(UNICORE_GPIOB, 9, 8);
    unicore_gpio_write(UNICORE_GPIOB, 8, 1);
    unicore_gpio_mode(UNICORE_GPIOB, 8, 8);
    irq_unlock(key);
    k_busy_wait(1000);
    key = irq_lock();
    data->fill_high = (UNICORE_REG(UNICORE_GPIOB + 8) & (1u << 9)) != 0;
    unicore_gpio_write(UNICORE_GPIOB, 12, 0);
    unicore_gpio_mode(UNICORE_GPIOB, 12, 3);
    data_output(data, data->fill_high);
    for (unsigned int i = 0; i < UNICORE_BITS; i++) {
        clock_pulse(data);
    }
    /* Stock probe: input pull-down, then select pull based on external level. */
    data->pull_down = true;
    data_input(data);
    irq_unlock(key);
    k_busy_wait(500);
    key = irq_lock();
    data->pull_down = data_read(data);
    data_input(data);
    irq_unlock(key);
    return 0;
}

static const struct kscan_driver_api api = {
    .config = configure, .enable_callback = enable, .disable_callback = disable,
};

#define UNICORE_DEFINE(n)                                                                        \
    BUILD_ASSERT(DT_INST_PROP(n, poll_interval_ms) > 0, "Poll interval must be positive");         \
    BUILD_ASSERT(DT_INST_PROP(n, half_period_us) <= 2, "Keep IRQ-off scan bounded");                \
    BUILD_ASSERT(DT_INST_PROP(n, settle_us) <= 4, "Keep IRQ-off scan bounded");                     \
    static struct unicore_data data_##n;                                                         \
    static const struct unicore_config config_##n = {                                            \
        .poll_ms = DT_INST_PROP(n, poll_interval_ms),                                             \
        .half_us = DT_INST_PROP(n, half_period_us),                                               \
        .settle_us = DT_INST_PROP(n, settle_us),                                                  \
    };                                                                                          \
    DEVICE_DT_INST_DEFINE(n, init, NULL, &data_##n, &config_##n, POST_KERNEL, 90, &api);

DT_INST_FOREACH_STATUS_OKAY(UNICORE_DEFINE)
