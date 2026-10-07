# Headless Lima buffer allocation

The boot log reports `Found GPU lima`, then `Failed to find/open /dev/card node
with KMS capabilities`, followed by failed GraphicBuffer allocations and
SurfaceFlinger aborting with `output buffer not gpu writeable`.

GloDroid minigbm-v0.7.2 treats Lima as a GPU with a separate display controller.
Its allocator requires a KMS card with CRTCs, connectors and encoders, even
when drm_hwcomposer uses its headless display. Disabling both DE and HDMI in
the board DTS removed that card. Mesa itself successfully initialized Mali400.

Enable DE and HDMI and provide the reciprocal connector endpoints, using the
pinned kernel's sun8i-h3-orangepi-one.dts as the controller graph reference.
This exposes the internal sun4i-drm card. The board does not need an HDMI socket
or connected monitor; drm_hwcomposer can still use its 640x480 headless display.
The older config fragment comment about keeping DE/HDMI disabled is superseded
by this DTS fix.

The build driver upgrades an already-applied DTS only if its SHA-256 matches
the exact previous project version and the kernel HEAD matches the source lock.
Custom edits are preserved and cause a review error. Fresh sources receive the
updated kernel patch normally. No userdata or Android system changes are needed.

Rebuild images, then update boot.img in both boot and recovery_boot plus
boot_dtbo.img in dtbo_a. The boot image embeds the DTBO table used by boot.scr;
flashing only dtbo_a does not replace that embedded table.

On hardware, verify sun4i-drm is registered, KMS allocation errors disappear,
SurfaceFlinger remains running, system_server appears and sys.boot_completed
reaches 1. This change has not yet been tested on the user's board.
