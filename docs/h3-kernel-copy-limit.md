# H3 Android kernel copy limit

Observed board log: Android kernel size 11959 KiB, destination 0x40080000,
followed by `uncompressed: uncompress error -28` before kernel entry.
The locked U-Boot's `include/configs/sunxi-common.h` sets SYS_BOOTM_LEN only
for ARM64; its ARM H3 build falls back to 8 MiB in `boot/bootm.c`.
`boot/image.c:image_decomp()` applies that bound even to an IH_COMP_NONE
image when copying to a different load address, returning -ENOSPC for a
larger image. ARM zImage's internal decompression does not remove this
outer U-Boot copy bound.

The new incremental U-Boot patch sets SYS_BOOTM_LEN to 32 MiB on SUN8I_H3.
ARM64 retains 64 MiB and other SoCs are unchanged. The copy window starting
at 0x40080000 ends at 0x42080000, below the existing ramdisk destination
0x43300000 and within the board's 512 MiB DRAM.

Validation: the actual conditional header fragment was compiled with
static assertions for H3/ARM64 limits, the reported kernel size and the
H3 copy-window/ramdisk boundary; patch reverse applicability and whitespace
checks passed. Full bootloader compilation and board boot remain server/
board validation steps.

Pull the branch and rerun the normal incremental build. Transfer the updated
bootloader-sd.img and env.img to the existing Windows images directory.
Flash those two files from U-Boot fastboot and reboot, allowing USB to
reconnect before asking it to reboot-fastboot. No partition formatting or
TF card rewrite is needed. The updated env.img also includes the prior
recovery-before-slot-check fix. The existing Android boot.img, boot_dtbo.img
and super.img may be retained if the build did not otherwise change them.
