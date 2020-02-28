/*****************************************************************************
* startup code for ARM with GNU toolset
*/

/* Constant definitions */

    .equ    MEM_BASE,       0x00000000
    .equ    ROM_BASE,       0x80000000
    .equ    MMIO_BASE,      0xc0000000
    .equ    AHB_BASE,       0xd0000000
    .equ    AHB_REMAP,      0x0088

    .equ    TLB_MEM_BASE,   (MEM_BASE>>18)
    .equ    TLB_MEM_SIZE,   2048
    .equ    TLB_ROM_BASE,   (ROM_BASE>>18)
    .equ    TLB_ROM_SIZE,   1024
    .equ    TLB_MMIO_BASE,  (MMIO_BASE>>18)
    .equ    TLB_MMIO_SIZE,  256
    .equ    TLB_AHB_BASE,   (AHB_BASE>>18)
    .equ    TLB_AHB_SIZE,   256

/* Standard definitions of Mode bits and Interrupt (I & F) flags in PSRs */

    .equ    I_BIT,          0x80      /* when I bit is set, IRQ is disabled */
    .equ    F_BIT,          0x40      /* when F bit is set, FIQ is disabled */

    .equ    USR_MODE,       0x10
    .equ    FIQ_MODE,       0x11
    .equ    IRQ_MODE,       0x12
    .equ    SVC_MODE,       0x13
    .equ    ABT_MODE,       0x17
    .equ    UND_MODE,       0x1B
    .equ    SYS_MODE,       0x1F

    .equ    MMIO_BASE,      0xC0000000

    .extern _tlb_base
    .extern __printbuf_base

/*****************************************************************************
* The starupt code must be linked at the start of ROM, which is NOT
* necessarily address zero.
*/
    .text
    .code 32

    .global _start
    .func   _start

_start:

    /* Vector table
    * NOTE: used only very briefly until RAM is remapped to address zero
    */
    ldr     pc, ResetAddr    /* Reset                 */
    ldr     pc, UndefAddr    /* Undefined instruction */
    ldr     pc, SWIAddr      /* Software interrupt    */
    ldr     pc, PAbortAddr   /* Prefetch abort        */
    ldr     pc, DAbortAddr   /* Data abort            */
    ldr     pc, ReservedAddr /* Reserved              */
    ldr     pc, IRQAddr      /* IRQ interrupt         */
    ldr     pc, FIQAddr      /* FIQ interrupt         */

// ###########################################################################
// ## Remap function
// DO NOT REMOVE or CHANGE the address, it's for booting code
// ###########################################################################
    .org    32
__remap:
    mov     r1, #AHB_BASE
    orr     r1, r1, #AHB_REMAP
    mov     r0, #1
    str     r0, [r1]
    b       _start
    nop                  // 8 delay slots to remap memory.
    nop                  // Fetch+instruction+decode+register+shift+execute+memory+write_back pipeline statge.
    nop
    nop
    nop
    nop
    nop
1:  b       1b           // never here

/*****************************************************************************
* Version Information
*/
    .org    0x54
    .global __version_major
__version_major:
    .word   CFG_VERSION_MAJOR
    .global __version_minor
__version_minor:
    .word   CFG_VERSION_MINOR
    .global __version_patch
__version_patch:
    .word   CFG_VERSION_PATCH
    .global __version_custom
__version_custom:
    .word   CFG_VERSION_CUSTOM
    .global __version_tweak
__version_tweak:
    .word   CFG_VERSION_TWEAK

    .align 4             /* Align to the word boundary */

// For IT9070 and IT9850AX1
// DO NOT REMOVE or CHANGE the address, it's for booting when remap
    .org    0xa0
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

    .align 4             /* Align to the word boundary */

/*****************************************************************************
* _reset
*/
_reset:
    /*
     * set the cpu to SVC32 mode
     */
    mrs     r0,cpsr
    bic     r0,r0,#0x1f
    orr     r0,r0,#0xd3
    msr     cpsr,r0

    /*
     * setup mmu
     */
    mov     r2, #0
    ldr     r1, =_tlb_base
    mcr     p15,0,r1,c2,c0,0        /* set TLB_BASE_ADDR */

# Do not init TLB here, uses static TLB table on tlb.c
#if 0
    mov     r5, #0
    orr     r2, r2, #0x0c10
    orr     r2, r2, #0x000a         /* set domain=4'b0000, c=1'b1, b=1'b0 */
1:  lsl     r6, r5, #2              /* set TLB_MEM */
    lsl     r7, r5, #20
    add     r5, r5, #1
    add     r6, r6, #TLB_MEM_BASE
    add     r7, r7, #MEM_BASE
    orr     r3, r1, r6
    orr     r4, r2, r7
    cmp     r5, #TLB_MEM_SIZE
    str     r4, [r3]
    bne     1b
    mov     r5, #0
    bic     r2, r2, #0x0000000c     /* set domain=4'b0000, clean c=1'b0, b=1'b0 */
1:  lsl     r6, r5, #2              /* set TLB_ROM */
    lsl     r7, r5, #20
    add     r5, r5, #1
    add     r6, r6, #TLB_ROM_BASE
    add     r7, r7, #ROM_BASE
    orr     r3, r1, r6
    orr     r4, r2, r7
    cmp     r5, #TLB_ROM_SIZE
    str     r4, [r3]
    bne     1b
    mov     r5, #0
    bic     r2, r2, #0x0000000c     /* set domain=4'b0000, clean c=1'b0, b=1'b0 */
1:  lsl     r6, r5, #2              /* set TLB_MMIO */
    lsl     r7, r5, #20
    add     r5, r5, #1
    add     r6, r6, #TLB_MMIO_BASE
    add     r7, r7, #MMIO_BASE
    orr     r3, r1, r6
    orr     r4, r2, r7
    cmp     r5, #TLB_MMIO_SIZE
    str     r4, [r3]
    bne     1b
    mov     r5, #0
    bic     r2, r2, #0x0000000c     /* set domain=4'b0000, clean c=1'b0, b=1'b0 */
1:  lsl     r6, r5, #2              /* set TLB_AHB */
    lsl     r7, r5, #20
    add     r5, r5, #1
    add     r6, r6, #TLB_AHB_BASE
    add     r7, r7, #AHB_BASE
    orr     r3, r1, r6
    orr     r4, r2, r7
    cmp     r5, #TLB_AHB_SIZE
    str     r4, [r3]
    bne     1b
#endif

    /*
     * Reset co-processor
     */
    mov     r1, #0
    mcr     p15,0,r1,c7,c14,0   /* clean&invalidate D-Cache all */
    mcr     p15,0,r1,c7,c10,4   /* drain write buffer */
    mcr     p15,0,r1,c7,c5,0    /* invalidate I-Cache all */
    mcr     p15,0,r1,c7,c5,6    /* invalidate BTB All */
    mcr     p15,0,r1,c8,c7,0    /* invalidate v1 TLB */

    /*
     * setup domain access
     */
    ldr     r0, =0xffffffff
    mcr     p15,0,r0,c3,c0,0        /* set all domain can access */

    /*
     * setup peripheral port
     */
    mov     r1, #MMIO_BASE          /* set peripheral port base address size */
    orr     r1, r1, #0x14           /* set peripheral port size =512MB */
    mcr     p15,0,r1,c15,c2,4

    /*
     * setup CR1-0 Configuration Register
     */
    mrc     p15,0,r2,c1,c0,0
    bic     r2,r2,#0x00002B00   /* clear bits 13, 11, 9:8 (--V- B-RS) */
    bic     r2,r2,#0x0000008F   /* clear bits 7, 3:0 (B--- WCAM) */

    orr     r2,r2,#0x00000001   /* set bit  0 (M) MMU */
    orr     r2,r2,#0x00000002   /* set bit  1 (A) Align */
    orr     r2,r2,#0x00001000   /* set bit 12 (I) I-Cache */
    orr     r2,r2,#0x00000004   /* set bit  2 (D) D-Cache */

#ifdef CFG_CPU_WRITE_BUFFER
    orr     r2,r2,#0x00000008   /* set bit  3 (W) Write-Buffer */

#else
// Workaround solution to bypass the bug of AHB-Mem wrapper.
// Disable the write buffer.
    bic     r2,r2,#0x00000008   /* clear bit 3 (W) Write-Buffer */

#endif // CFG_CPU_WRITE_BUFFER

    orr     r2,r2,#0x00000800   /* set bit 11 (B) Branch predict */
    mcr     p15,0,r2,c1,c0,0

    @Turn off IRQ/FIQ bit of CPU
    mrs     r0, cpsr
    orr     r0,r0,#(I_BIT|F_BIT)
    msr     cpsr_c,r0

    /* Initialize stack pointers for all ARM modes */
    msr     CPSR_c,#(IRQ_MODE | I_BIT | F_BIT)
    ldr     sp,=__irq_stack_top__                /* set the IRQ stack pointer */

    msr     CPSR_c,#(FIQ_MODE | I_BIT | F_BIT)
    ldr     sp,=__fiq_stack_top__                /* set the FIQ stack pointer */

    msr     CPSR_c,#(SVC_MODE | I_BIT | F_BIT)
    ldr     sp,=__svc_stack_top__                /* set the SVC stack pointer */

    msr     CPSR_c,#(ABT_MODE | I_BIT | F_BIT)
    ldr     sp,=__abt_stack_top__                /* set the ABT stack pointer */

    msr     CPSR_c,#(UND_MODE | I_BIT | F_BIT)
    ldr     sp,=__und_stack_top__                /* set the UND stack pointer */

    msr     CPSR_c,#(SYS_MODE | I_BIT | F_BIT)
    ldr     sp,=__c_stack_top__                  /* set the C stack pointer */

    /* switch to supervisor mode*/
    msr     CPSR_c,#(SVC_MODE | I_BIT | F_BIT)

_cstartup:
    /* Clear the .bss section (zero init) */
    ldr     r1,=__bss_start__
    ldr     r2,=__bss_end__
    mov     r3,#0
1:
    cmp     r1,r2
    stmltia r1!,{r3}
    blt     1b

    /* Call the platform-specific low-level initialization routine */
    ldr     r12,=BootInit
    mov     lr,pc           /* set the return address */
    bx      r12             /* the target code can be ARM or THUMB */

    /* Enter the C/C++ code */
    ldr     r12,=main
    mov     lr,pc           /* set the return address */
    bx      r12             /* the target code can be ARM or THUMB */

ExitFunction:
    nop
    nop
    nop
    b       ExitFunction

    .size   _start, . - _start
    .endfunc

    .weak ExitFunction

/*****************************************************************************
* Suspend Restore, function itpSuspendRestore is static address which callig
* from booting script when the system resume from RAM. If the address is changed,
* it also needs to modify the calling address in the booting script.
*/
    .org    0x1c0
    .text
    .align 0
    .type itpSuspendRestore %function
    .global itpSuspendRestore

itpSuspendRestore:
    /* invalidate I-Cache all */
    mov     r1, #0
    mcr     p15,0,r1,c7,c5,0

    /*
     * disable mmu
     */
    mrc     p15,0,r0,c1,c0,0
    bic     r0,r0,#0x00000001   /* disable bit  0 (M) MMU */
    mcr     p15,0,r0,c1,c0,0
    nop
    nop
    nop
    nop

    /*
     * remap setting & jump to memory
     */
    mov     r2, pc
    add     r2, r2, #0x18
    sub     r2, r2, #0x80000000
    mov     r0, #0xd0000000
    orr     r0, r0, #0x88
    mov     r1, #1
    str     r1, [r0]
    mov     pc, r2

    /*
     * set the cpu to SVC32 mode and Turn off IRQ/FIQ bit of CPU
     */
    mrs     r0,cpsr
    bic     r0,r0,#0x1f
    orr     r0,r0,#0xd3
    msr     cpsr,r0

    /*
     * setup mmu
     */
    ldr     r0, =__suspend_regs_base
    ldr     r0, [r0]                /* set peripheral port base address size */
    mcr     p15,0,r0,c2,c0,0        /* set TLB_BASE_ADDR */

    /*
     * Reset co-processor
     */
    mov     r0, #0
    mcr     p15,0,r0,c7,c14,0   /* clean&invalidate D-Cache all */
    mcr     p15,0,r0,c7,c10,4   /* drain write buffer */
    mcr     p15,0,r0,c7,c5,0    /* invalidate I-Cache all */
    mcr     p15,0,r0,c7,c5,6    /* invalidate BTB All */
    mcr     p15,0,r0,c8,c7,0    /* invalidate v1 TLB */

    /*
     * setup domain access
     */
    ldr     r0, =0xffffffff
    mcr     p15,0,r0,c3,c0,0        /* set all domain can access */

    /*
     * setup peripheral port
     */
    ldr     r0, =__suspend_regs_base
    ldr     r0, [r0,#0x4]           /* set peripheral port base address size */
    orr     r0, r0, #0x14           /* set peripheral port size =512MB */
    mcr     p15,0,r0,c15,c2,4

    /*
     * setup CR1-0 Configuration Register
     */
    ldr     r0, =__suspend_regs_base
    ldr     r0, [r0,#0x8]
    mcr     p15,0,r0,c1,c0,0

    /* Initialize stack pointers for all ARM modes */
    msr     CPSR_c,#(IRQ_MODE | I_BIT | F_BIT)
    ldr     sp,=__irq_stack_top__                /* restore the IRQ stack pointer */

    msr     CPSR_c,#(FIQ_MODE | I_BIT | F_BIT)
    ldr     sp,=__fiq_stack_top__                /* restore the FIQ stack pointer */

    msr     CPSR_c,#(ABT_MODE | I_BIT | F_BIT)
    ldr     sp,=__abt_stack_top__                /* restore the ABT stack pointer */

    msr     CPSR_c,#(UND_MODE | I_BIT | F_BIT)
    ldr     sp,=__und_stack_top__                /* restore the UND stack pointer */

    msr     CPSR_c,#(SVC_MODE| I_BIT | F_BIT)
    ldr     sp, =__suspend_regs_base             /* restore the SVC stack pointer */
    ldr     sp, [sp,#0xc]
    ldmia   sp!, {sp}^
    ldmia   sp!, {lr}^
    ldmia   sp!, {r0}
    msr     SPSR, r0

    ldmia   sp!, {r0-r12,lr}
    movs    pc, lr

/*****************************************************************************
* Vector pointer
*/
        .org    0x1000 - 64
ResetAddr:     .word _reset
UndefAddr:     .word itpErrorUndef
               .global SWIAddr
SWIAddr:       .word vPortYieldProcessor
PAbortAddr:    .word itpErrorPrefetchAbort
DAbortAddr:    .word itpErrorDataAbort
ReservedAddr:  .word 0
               .global IRQAddr
IRQAddr:       .word ithIntrDoIrq
FIQAddr:       .word ithIntrDoFiq

/*****************************************************************************
* Saved Frame Pointer
*/
.org    0x1000 - 20
    .global __return_addr
__return_addr:
    .word   __return_addr
    .global __frame_ptr
__frame_ptr:
    .word   __frame_ptr

/*****************************************************************************
* Pointers of Print Buffer
*/
    .org    0x1000 - 12
    .global __printbuf_addr
__printbuf_addr:
    .word   __printbuf_base
    .global __printbuf_size
__printbuf_size:
    .word   CFG_DBG_PRINTBUF_SIZE
    .global __printbuf_ptr
__printbuf_ptr:
    .word   0

    .org    0x1000
#ifdef CFG_XCPU_MSGQ
/*****************************************************************************
* _xcpu_msgq
*/
_xcpu_msgq:
    .global _xcpu_msgq
    .fill CFG_XCPU_MSGQ_SIZE

#endif // CFG_XCPU_MSGQ

/*****************************************************************************
* Suspend Save
*/
    .text
    .align 0
    .type itpSuspendSave %function
    .global itpSuspendSave

itpSuspendSave:
    stmdb   sp!, {r0-r12, lr}
    mrs     r0, SPSR
    stmdb   sp!, {r0}
    stmdb   sp!, {sp, lr}^

    ldr     r0, =__suspend_regs_base
    str     sp, [r0, #0xc]
    mrc     p15,0,r1,c2,c0,0
    str     r1, [r0, #0x0]
    mrc     p15,0,r1,c15,c2,4
    str     r1, [r0, #0x4]
    mrc     p15,0,r1,c1,c0,0
    str     r1, [r0, #0x8]

    movs    pc, lr

/*****************************************************************************
* Divide By Zero
*/
    .text
    .align 0
    .type __aeabi_idiv0 %function
    .global __aeabi_idiv0

__aeabi_idiv0:
    ldr     r12,=itpErrorDivideByZero
    mov     lr,pc                       /* set the return address */
    bx      r12                         /* the target code can be ARM or THUMB */

    .text
    .code 32
    .align 0
    .global umul_64to128_arm9e

umul_64to128_arm9e:
    stmfd   r13!, {r4-r6, r14} @ 16B
    mov     r6, r0
    ldrd    r0, [r13, #16]

    umull   r4, r5, r0, r2
    mov     r12, #0
    umlal   r5, r12, r0, r3
    mov     r14, #0
    umlal   r5, r14, r1, r2
    mov     r0, #0
    adds    r12, r12, r14
    adc     r14, r0, #0
    umlal   r12, r14, r1, r3

    mov     r0, r6
    str     r4, [r0, #0]
    str     r5, [r0, #4]
    str     r12, [r0, #8]
    str     r14, [r0, #12]

    ldmfd   r13!, {r4-r6, r15}
    .end
