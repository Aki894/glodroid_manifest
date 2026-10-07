# Recovery entry before normal A/B slot selection

The pinned U-Boot prints `Android boot failed, error -22` from `cmd/ab_select.c`
when `ab_select_slot()` fails. This is not a kernel boot message. The original
GloDroid boot script performs this selection before inspecting `boot-fastboot`
or `boot-recovery` in misc. Its failure path enters U-Boot fastboot, so an
installation/recovery request can be blocked by normal boot slot metadata.

The new incremental device patch loads the BCB and recognizes recovery
requests before normal slot selection. Normal boots still use `ab_select`
and the original fallback. The function explicitly returns success after
handling the BCB so the caller's `run bootcmd_bcb && ...` can load the image.

Validation: patch reverse applicability after the previous device patches;
macro preprocessing and generated shell syntax; mocked executions of the
actual generated BCB function for boot-fastboot, boot-recovery and normal
boot (normal slot selection fails with -22). Recovery requests skip slot
selection and normal boot still takes the fallback. Actual U-Boot hush and
kernel/recovery startup require board validation.

For a board currently waiting in U-Boot fastboot, interrupt it with Ctrl+C
on the serial console. If the prompt is available and the generated boot
script has already been executed, this temporary override forces loading
recovery without changing saved firmware or partition contents:

```
setenv bootcmd_bcb 'setenv androidrecovery true'
run bootcmd
```

Use this after a successful reboot-fastboot request has set the BCB command.
Do not saveenv. The temporary override is lost on reset. Capture the full
serial output to validate subsequent boot stages. The permanent patch can
be integrated through the normal incremental build, and the updated env.img
flashed later; no full AOSP source resync or output cleanup is required.
