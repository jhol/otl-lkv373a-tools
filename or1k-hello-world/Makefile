
AS=or1k-elf-as
CC=or1k-elf-gcc
CFLAGS=-ffreestanding
LDFLAGS=-nostdlib -lc -lgcc -lm -lor1k -Wl,--gc-sections -Wl,-S

all: mod-fw.bin 

clean:
	rm -f *.o u2_patch mod-fw.bin

%.o: %.s
	$(AS) -o $@ $^

main.o: main.c

u2_patch: main.o startup.o
	$(CC) -T u2_patch.ld -o $@ $^ $(LDFLAGS)

mod-fw.bin: LKV373A_TX_V3.0c_d_20161116_bin.bin u2_patch 
	python3 overlay_patch.py $@ $^

.PHONY: clear
