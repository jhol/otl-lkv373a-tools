OUTPUT_FORMAT("elf32-littlearm", "elf32-bigarm", "elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(_start)
INPUT(crti.o crtbegin.o crtend.o crtn.o)
GROUP(-lopenrtos -litp_boot -lith -lith_platform -lboot -lmalloc -lc -lm -lgcc)

#define ALIGN64(n)          (((n)+63) & 0xffffffc0)
#define C_STACK_SIZE        ALIGN64(4096)
#define IRQ_STACK_SIZE      ALIGN64(4096)
#define FIQ_STACK_SIZE      ALIGN64(4096)
#define SVC_STACK_SIZE      ALIGN64(4096)
#define ABT_STACK_SIZE      ALIGN64(512)
#define UND_STACK_SIZE      ALIGN64(512)
#define TLB_ALIGN           (0x4000)
#define TLB_SIZE            ALIGN64(4096 * 4)
#define SUSPEND_REGS_SIZE   ALIGN64(4 * 4)
#define LCD_SIZE            ALIGN64(CFG_LCD_PITCH * CFG_LCD_HEIGHT)
#define LCDC_SIZE           ALIGN64(CFG_LCDC_PITCH * CFG_LCDC_HEIGHT)
#define LCD_GAP_SIZE        0

MEMORY {    /* memory map of Castor3 */
  RAM (rwx) : ORIGIN = 0x00000000, LENGTH = CFG_RAM_SIZE - LCD_SIZE * 2 - LCDC_SIZE - LCD_GAP_SIZE - ALIGN64(CFG_WT_SIZE)
}

SECTIONS
{
  .reset : {
    *startup.o (.text)  /* startup code (ARM vectors and reset handler) */
    . = ALIGN(0x4);
  } >RAM

  .bootimage_func :
  {
    . = ALIGN (4);
    __bootimage_func_start = .;
    KEEP(*(.bootimage_func))
    . = ALIGN (4);
    __bootimage_func_end = .;
  } >RAM

  .power_sleep_func :
  {
    . = ALIGN (4);
    __power_sleep_func_start = .;
    KEEP(*(.power_sleep_func))
    . = ALIGN (4);
    __power_sleep_func_end = .;
  } >RAM

  .power_suspend_func :
  {
    . = ALIGN (4);
    __power_suspend_func_start = .;
    KEEP(*(.power_suspend_func))
    . = ALIGN (4);
    __power_suspend_func_end = .;
  } >RAM

  /* Read-only sections, merged into text segment: */
  .interp         : { *(.interp) }
  .note.gnu.build-id : { *(.note.gnu.build-id) }
  .hash           : { *(.hash) }
  .gnu.hash       : { *(.gnu.hash) }
  .dynsym         : { *(.dynsym) }
  .dynstr         : { *(.dynstr) }
  .gnu.version    : { *(.gnu.version) }
  .gnu.version_d  : { *(.gnu.version_d) }
  .gnu.version_r  : { *(.gnu.version_r) }
  .rel.init       : { *(.rel.init) }
  .rela.init      : { *(.rela.init) }
  .rel.text       : { *(.rel.text .rel.text.* .rel.gnu.linkonce.t.*) }
  .rela.text      : { *(.rela.text .rela.text.* .rela.gnu.linkonce.t.*) }
  .rel.fini       : { *(.rel.fini) }
  .rela.fini      : { *(.rela.fini) }
  .rel.rodata     : { *(.rel.rodata .rel.rodata.* .rel.gnu.linkonce.r.*) }
  .rela.rodata    : { *(.rela.rodata .rela.rodata.* .rela.gnu.linkonce.r.*) }
  .rel.data.rel.ro   : { *(.rel.data.rel.ro .rel.data.rel.ro.* .rel.gnu.linkonce.d.rel.ro.*) }
  .rela.data.rel.ro  : { *(.rela.data.rel.ro .rela.data.rel.ro.* .rela.gnu.linkonce.d.rel.ro.*) }
  .rel.data       : { *(.rel.data .rel.data.* .rel.gnu.linkonce.d.*) }
  .rela.data      : { *(.rela.data .rela.data.* .rela.gnu.linkonce.d.*) }
  .rel.tdata      : { *(.rel.tdata .rel.tdata.* .rel.gnu.linkonce.td.*) }
  .rela.tdata     : { *(.rela.tdata .rela.tdata.* .rela.gnu.linkonce.td.*) }
  .rel.tbss       : { *(.rel.tbss .rel.tbss.* .rel.gnu.linkonce.tb.*) }
  .rela.tbss      : { *(.rela.tbss .rela.tbss.* .rela.gnu.linkonce.tb.*) }
  .rel.ctors      : { *(.rel.ctors) }
  .rela.ctors     : { *(.rela.ctors) }
  .rel.dtors      : { *(.rel.dtors) }
  .rela.dtors     : { *(.rela.dtors) }
  .rel.got        : { *(.rel.got) }
  .rela.got       : { *(.rela.got) }
  .rel.bss        : { *(.rel.bss .rel.bss.* .rel.gnu.linkonce.b.*) }
  .rela.bss       : { *(.rela.bss .rela.bss.* .rela.gnu.linkonce.b.*) }
  .rel.iplt       :
    {
      PROVIDE_HIDDEN (__rel_iplt_start = .);
      *(.rel.iplt)
      PROVIDE_HIDDEN (__rel_iplt_end = .);
    }
  .rela.iplt      :
    {
      PROVIDE_HIDDEN (__rela_iplt_start = .);
      *(.rela.iplt)
      PROVIDE_HIDDEN (__rela_iplt_end = .);
    }
  .rel.plt        :
    {
      *(.rel.plt)
    }
  .rela.plt       :
    {
      *(.rela.plt)
    }
  .init           :
  {
    KEEP (*(SORT_NONE(.init)))
  } >RAM
  .plt            : { *(.plt) } >RAM
  .iplt           : { *(.iplt) } >RAM
  .text           :
  {
    _codec_end_addr = .;
    codec_end_addr  = .;
    _text_start = .;
    *(.text.unlikely .text.*_unlikely)
    *(.text.exit .text.exit.*)
    *(.text.startup .text.startup.*)
    *(.text.hot .text.hot.*)
    basic_op2.o(.text)
    cfft_64.o(.text)
    fdsr.o(.text)
    HowlingCtrl.o(.text)
    *(.text .stub .text.* .gnu.linkonce.t.*)
    /* .gnu.warning sections are handled specially by elf32.em.  */
    *(.gnu.warning)
    *(.glue_7t) *(.glue_7) *(.vfp11_veneer) *(.v4_bx)
    _text_end = .;
  } >RAM
  .fini           :
  {
    KEEP (*(.fini))
  } >RAM
  PROVIDE (__etext = .);
  PROVIDE (_etext = .);
  PROVIDE (etext = .);
  .rodata         : { *(.rodata .rodata.* .gnu.linkonce.r.*) } >RAM
  .rodata1        : { *(.rodata1) } >RAM
  .ARM.extab   : { *(.ARM.extab* .gnu.linkonce.armextab.*) } >RAM
   PROVIDE_HIDDEN (__exidx_start = .);
  .ARM.exidx   : { *(.ARM.exidx* .gnu.linkonce.armexidx.*) } >RAM
   PROVIDE_HIDDEN (__exidx_end = .);
  .eh_frame_hdr : { *(.eh_frame_hdr) } >RAM
  .eh_frame       : ONLY_IF_RO { KEEP (*(.eh_frame)) } >RAM
  .gcc_except_table   : ONLY_IF_RO { *(.gcc_except_table .gcc_except_table.*) } >RAM
  /* These sections are generated by the Sun/Oracle C++ compiler.  */
  .exception_ranges   : ONLY_IF_RO { *(.exception_ranges .exception_ranges*) } >RAM
  /* Adjust the address for the data segment.  We want to adjust up to
     the same address within the page on the next page up.  */
  . = ALIGN(CONSTANT (MAXPAGESIZE)) + (. & (CONSTANT (MAXPAGESIZE) - 1));
  /* Exception handling  */
  .eh_frame       : ONLY_IF_RW { KEEP (*(.eh_frame)) } >RAM
  .gcc_except_table   : ONLY_IF_RW { *(.gcc_except_table .gcc_except_table.*) } >RAM
  .exception_ranges   : ONLY_IF_RW { *(.exception_ranges .exception_ranges*) } >RAM
  /* Thread Local Storage sections  */
  .tdata          : { *(.tdata .tdata.* .gnu.linkonce.td.*) } >RAM
  .tbss           : { *(.tbss .tbss.* .gnu.linkonce.tb.*) *(.tcommon) } >RAM
  .preinit_array     :
  {
    PROVIDE_HIDDEN (__preinit_array_start = .);
    KEEP (*(.preinit_array))
    PROVIDE_HIDDEN (__preinit_array_end = .);
  } >RAM
  .init_array     :
  {
    PROVIDE_HIDDEN (__init_array_start = .);
    KEEP (*(SORT(.init_array.*)))
    KEEP (*(.init_array))
    PROVIDE_HIDDEN (__init_array_end = .);
  } >RAM
  .fini_array     :
  {
    PROVIDE_HIDDEN (__fini_array_start = .);
    KEEP (*(SORT(.fini_array.*)))
    KEEP (*(.fini_array))
    PROVIDE_HIDDEN (__fini_array_end = .);
  } >RAM
  .ctors          :
  {
    /* gcc uses crtbegin.o to find the start of
       the constructors, so we make sure it is
       first.  Because this is a wildcard, it
       doesn't matter if the user does not
       actually link against crtbegin.o; the
       linker won't look for a file to match a
       wildcard.  The wildcard also means that it
       doesn't matter which directory crtbegin.o
       is in.  */
    KEEP (*crtbegin.o(.ctors))
    KEEP (*crtbegin?.o(.ctors))
    /* We don't want to include the .ctor section from
       the crtend.o file until after the sorted ctors.
       The .ctor section from the crtend file contains the
       end of ctors marker and it must be last */
    KEEP (*(EXCLUDE_FILE (*crtend.o *crtend?.o ) .ctors))
    KEEP (*(SORT(.ctors.*)))
    KEEP (*(.ctors))
  } >RAM
  .dtors          :
  {
    KEEP (*crtbegin.o(.dtors))
    KEEP (*crtbegin?.o(.dtors))
    KEEP (*(EXCLUDE_FILE (*crtend.o *crtend?.o ) .dtors))
    KEEP (*(SORT(.dtors.*)))
    KEEP (*(.dtors))
  } >RAM
  .jcr            : { KEEP (*(.jcr)) }
  .data.rel.ro : { *(.data.rel.ro.local* .gnu.linkonce.d.rel.ro.local.*) *(.data.rel.ro .data.rel.ro.* .gnu.linkonce.d.rel.ro.*) } >RAM
  .dynamic        : { *(.dynamic) } >RAM
  .got            : { *(.got.plt) *(.igot.plt) *(.got) *(.igot) } >RAM
  .data           :
  {
    __data_start = . ;
    *(.data .data.* .gnu.linkonce.d.*)
    HowlingCtrl.o(.data)
    SORT(CONSTRUCTORS)
  } >RAM
  .data1          : { *(.data1) } >RAM
  _edata = .; PROVIDE (edata = .);

  .tlb : {
    . = ALIGN (TLB_ALIGN);
    _tlb_base = .;
    KEEP(*(.tlb*));
  } >RAM

  .bss : {
   __bss_start = .;
   __bss_start__ = .;
   *(.dynbss)
   *(.bss .bss.* .gnu.linkonce.b.*)
   *(COMMON)
   /* Align here to ensure that the .bss section occupies space up to
      _end.  Align after .bss to ensure correct alignment even if the
      .bss section disappears because there are no input sections.
      FIXME: Why do we need it? When there is no .bss section, we don't
      pad the .data section.  */
   . = ALIGN(. != 0 ? 32 / 8 : 1);
   . = ALIGN(8);
   _bss_end__ = . ;
   __bss_end__ = . ;
   __end__ = . ;
   _end = .; PROVIDE (end = .);
  } >RAM

  .mmap : {
    . = ALIGN(8);
    __mmap_start__ = . ;
    *(.mmap)
    . += ALIGN64(CFG_MMAP_SIZE);
    __mmap_end__ = .;
  } >RAM

  .stack : {
    . = ALIGN(8);
    __stack_start__ = . ;

    . += IRQ_STACK_SIZE;
    __irq_stack_top__ = . ;

    . += FIQ_STACK_SIZE;
    __fiq_stack_top__ = . ;

    . += SVC_STACK_SIZE;
    __svc_stack_top__ = . ;

    . += ABT_STACK_SIZE;
    __abt_stack_top__ = . ;

    . += UND_STACK_SIZE;
    __und_stack_top__ = . ;

    . += C_STACK_SIZE;
    __c_stack_top__ = . ;
    __stack_end__ = .;
  } >RAM

  .reserved : {
    . = ALIGN(8);
    __suspend_regs_base = .;
    . += SUSPEND_REGS_SIZE;

    __printbuf_base = .;
    . += ALIGN64(CFG_DBG_PRINTBUF_SIZE);

    __cmdq_base = .;
    . += ALIGN64(CFG_CMDQ_SIZE);
  } >RAM

  .heap : {
    . = ALIGN(8);
    __heap_start__ = . ;
    *(.heap)
  } >RAM

  /* Stabs debugging sections.  */
  .stab          0 : { *(.stab) }
  .stabstr       0 : { *(.stabstr) }
  .stab.excl     0 : { *(.stab.excl) }
  .stab.exclstr  0 : { *(.stab.exclstr) }
  .stab.index    0 : { *(.stab.index) }
  .stab.indexstr 0 : { *(.stab.indexstr) }
  .comment       0 : { *(.comment) }
  /* DWARF debug sections.
     Symbols in the DWARF debugging sections are relative to the beginning
     of the section so we begin them at 0.  */
  /* DWARF 1 */
  .debug          0 : { *(.debug) }
  .line           0 : { *(.line) }
  /* GNU DWARF 1 extensions */
  .debug_srcinfo  0 : { *(.debug_srcinfo) }
  .debug_sfnames  0 : { *(.debug_sfnames) }
  /* DWARF 1.1 and DWARF 2 */
  .debug_aranges  0 : { *(.debug_aranges) }
  .debug_pubnames 0 : { *(.debug_pubnames) }
  /* DWARF 2 */
  .debug_info     0 : { *(.debug_info .gnu.linkonce.wi.*) }
  .debug_abbrev   0 : { *(.debug_abbrev) }
  .debug_line     0 : { *(.debug_line) }
  .debug_frame    0 : { *(.debug_frame) }
  .debug_str      0 : { *(.debug_str) }
  .debug_loc      0 : { *(.debug_loc) }
  .debug_macinfo  0 : { *(.debug_macinfo) }
  /* SGI/MIPS DWARF 2 extensions */
  .debug_weaknames 0 : { *(.debug_weaknames) }
  .debug_funcnames 0 : { *(.debug_funcnames) }
  .debug_typenames 0 : { *(.debug_typenames) }
  .debug_varnames  0 : { *(.debug_varnames) }
  /* DWARF 3 */
  .debug_pubtypes 0 : { *(.debug_pubtypes) }
  .debug_ranges   0 : { *(.debug_ranges) }
  /* DWARF Extension.  */
  .debug_macro    0 : { *(.debug_macro) }
  .ARM.attributes 0 : { KEEP (*(.ARM.attributes)) KEEP (*(.gnu.attributes)) }
  .note.gnu.arm.ident 0 : { KEEP (*(.note.gnu.arm.ident)) }
  /DISCARD/ : { *(.note.GNU-stack) *(.gnu_debuglink) *(.gnu.lto_*) }

  __heap_end__        = CFG_RAM_SIZE - ALIGN64(CFG_WT_SIZE) - LCD_SIZE * 2 - LCDC_SIZE - LCD_GAP_SIZE;
  __lcd_base_a        = CFG_RAM_SIZE - ALIGN64(CFG_WT_SIZE) - LCD_SIZE * 2 - LCDC_SIZE - LCD_GAP_SIZE;
  __lcd_base_b        = CFG_RAM_SIZE - ALIGN64(CFG_WT_SIZE) - LCD_SIZE - LCDC_SIZE - LCD_GAP_SIZE;
  __lcd_base_c        = CFG_RAM_SIZE - ALIGN64(CFG_WT_SIZE) - LCDC_SIZE - LCD_GAP_SIZE;
  __wt_base           = CFG_RAM_SIZE - ALIGN64(CFG_WT_SIZE) - LCD_GAP_SIZE;
  __mem_end           = CFG_RAM_SIZE;

}

