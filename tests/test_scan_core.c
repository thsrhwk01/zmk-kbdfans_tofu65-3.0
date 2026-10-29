/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "unicore_scan_core.h"

struct fake_bus {
    unsigned int clocks;
    unsigned int reads;
    bool output;
    bool high;
    bool fill;
    bool samples[UNICORE_BITS];
};

static void output(void *context, bool high) {
    struct fake_bus *bus = context;
    bus->output = true;
    bus->high = high;
}

static void input(void *context) {
    struct fake_bus *bus = context;
    assert(bus->output);
    bus->output = false;
}

static void pulse(void *context) {
    struct fake_bus *bus = context;
    assert(bus->output);
    /* First 112 flush clocks, one injected bit, then 112 advance clocks. */
    assert(bus->high == (bus->clocks == 112 ? !bus->fill : bus->fill));
    bus->clocks++;
}

static bool read_pin(void *context) {
    struct fake_bus *bus = context;
    assert(!bus->output);
    assert(bus->reads < UNICORE_BITS);
    assert(bus->clocks == 113 + bus->reads);
    return !bus->samples[bus->reads++];
}

static void test_serial(bool fill) {
    struct fake_bus bus = {.fill = fill};
    const struct unicore_bus api = {&bus, output, input, pulse, read_pin};
    bool sampled[UNICORE_BITS];
    /* Exercise every serial index independently, including unused positions. */
    for (unsigned int key = 0; key < UNICORE_BITS; key++) {
        memset(&bus, 0, sizeof(bus));
        bus.fill = fill;
        bus.samples[key] = true;
        unicore_sample(&api, fill, sampled);
        assert(bus.clocks == 225 && bus.reads == 112 && !bus.output);
        for (unsigned int i = 0; i < UNICORE_BITS; i++) {
            assert(sampled[i] == (i == key));
        }
    }
}

static void test_filter(void) {
    struct unicore_filter f = {0};
    /* A short bounce must not emit a key event. */
    assert(!unicore_filter_update(&f, 0, true));
    assert(!unicore_filter_update(&f, 0, false));
    memset(&f, 0, sizeof(f));
    for (unsigned int i = 0; i < 3; i++) {
        assert(!unicore_filter_update(&f, 0, true));
    }
    assert(unicore_filter_update(&f, 0, true));
    assert(f.pressed[0]);
    for (unsigned int i = 0; i < 8; i++) {
        assert(!unicore_filter_update(&f, 0, true));
    }
    for (unsigned int i = 0; i < 5; i++) {
        assert(!unicore_filter_update(&f, 0, false));
    }
    assert(unicore_filter_update(&f, 0, false));
    assert(!f.pressed[0]);
    /* Independent states across the complete chain. */
    for (unsigned int i = 1; i < UNICORE_BITS; i++) {
        assert(!f.pressed[i] && !f.history[i]);
    }
}

int main(void) {
    test_serial(false);
    test_serial(true);
    test_filter();
    puts("PASS: both polarities x 112 positions, 225-clock protocol, press/release/bounce filtering");
    return 0;
}

