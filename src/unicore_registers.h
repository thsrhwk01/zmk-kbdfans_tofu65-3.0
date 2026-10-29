/* SPDX-License-Identifier: MIT */
#ifndef UNICORE_REGISTERS_H
#define UNICORE_REGISTERS_H
#include <stdint.h>

#define UNICORE_GPIOA 0x40010800u
#define UNICORE_GPIOB 0x40010c00u
#define UNICORE_RCC 0x40021000u
#define UNICORE_REG(address) (*(volatile uint32_t *)(uintptr_t)(address))

static inline void unicore_gpio_write(uint32_t port, unsigned int pin, int high) {
    UNICORE_REG(port + (high ? 0x10 : 0x14)) = 1u << pin;
}

/* Caller serializes CRL/CRH updates with irq_lock (early startup has IRQs off). */
static inline void unicore_gpio_mode(uint32_t port, unsigned int pin, uint32_t mode) {
    uint32_t address = port + (pin < 8 ? 0 : 4);
    unsigned int shift = (pin % 8) * 4;
    UNICORE_REG(address) = (UNICORE_REG(address) & ~(0xfu << shift)) | (mode << shift);
}
#endif

