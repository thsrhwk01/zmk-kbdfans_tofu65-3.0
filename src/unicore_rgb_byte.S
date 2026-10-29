/* PB15 serial RGB timing reconstructed from stock 0x08009db4 at 48 MHz.
 * r0: one byte, MSB first. Called with IRQs masked for the complete RGB frame.
 */
.syntax unified
.thumb
.text
.align 2
.global unicore_rgb_byte
.type unicore_rgb_byte, %function
.thumb_func
unicore_rgb_byte:
    push {r4, r5, lr}
    movs r3, #7
    movs r5, #1
    mov.w r1, #32768
    ldr r2, =0x40010c00
1:
    lsl.w r4, r5, r3
    tst r4, r0
    str r1, [r2, #16]
    beq 4f
    movs r4, #3
2:
    .rept 6
    nop
    .endr
    subs r4, #1
    bne 2b
    str r1, [r2, #20]
    .rept 12
    nop
    .endr
3:
    subs r3, #1
    bcs 1b
    pop {r4, r5, pc}
4:
    .rept 12
    nop
    .endr
    movs r4, #3
    str r1, [r2, #20]
5:
    .rept 6
    nop
    .endr
    subs r4, #1
    bne 5b
    b 3b
.size unicore_rgb_byte, .-unicore_rgb_byte
