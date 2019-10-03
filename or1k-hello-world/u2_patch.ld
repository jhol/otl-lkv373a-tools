
SECTIONS
{
  . = 0x2000;
  .ro : {
    *(.text)
    *(.rodata)
  }
  . = ALIGN(4);
  .rw : {
    *(.data)
    *(.bss)
  }

  /* Heap */
  . = ALIGN(4);
  start = .;
  . = . + 0x10000;
  end = .;

  /* Entry Point */
  . = 0x7d6f0;
  .patch : {
    *(.init)
    KEEP(*(.init))
  }
}
