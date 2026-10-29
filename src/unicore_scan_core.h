/* SPDX-License-Identifier: MIT */
#ifndef UNICORE_SCAN_CORE_H
#define UNICORE_SCAN_CORE_H

#include <stdbool.h>
#include <stdint.h>

#define UNICORE_BITS 112
#define UNICORE_COLS 8

struct unicore_filter {
    uint8_t history[UNICORE_BITS];
    bool pressed[UNICORE_BITS];
};

/* Stock thresholds at 0x0800FF00: >239 press, <=4 release. */
static inline bool unicore_filter_update(struct unicore_filter *filter, unsigned int i,
                                        bool active) {
    uint8_t history = (filter->history[i] >> 1) | (active ? 0x80 : 0);
    bool before = filter->pressed[i];
    filter->history[i] = history;
    if (history > 239) {
        filter->pressed[i] = true;
    } else if (history <= 4) {
        filter->pressed[i] = false;
    }
    return before != filter->pressed[i];
}

/* Injectable bus lets the exact clock/data sequence be tested without hardware. */
struct unicore_bus {
    void *context;
    void (*output)(void *context, bool high);
    void (*input)(void *context);
    void (*pulse)(void *context);
    bool (*read)(void *context);
};

static inline void unicore_sample(const struct unicore_bus *bus, bool fill_high,
                                  bool active[UNICORE_BITS]) {
    bus->output(bus->context, fill_high);
    for (unsigned int i = 0; i < UNICORE_BITS; i++) {
        bus->pulse(bus->context);
    }
    bus->output(bus->context, !fill_high);
    bus->pulse(bus->context);
    bus->input(bus->context);
    for (unsigned int i = 0; i < UNICORE_BITS; i++) {
        active[i] = !bus->read(bus->context);
        bus->output(bus->context, fill_high);
        bus->pulse(bus->context);
        bus->input(bus->context);
    }
}
#endif

