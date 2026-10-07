# Reboot to recovery after boot completion

Both complete Android boot cycles in wukong-reboot-logcat.txt show the same
sequence: vold prepares user 0's credential-encrypted storage, default ACL
creation on /data/media/0 fails with EOPNOTSUPP, UserDataPreparer destroys and
retries the user storage, and the retry fails. uncrypt then writes:

```
--prompt_and_wipe_data
--reason=prepareUserData failed
```

system_server requests reboot,recovery. The earlier sys.boot_completed=1 is
not evidence that user 0 completed unlocking. SQLite and application-directory
errors after the failed preparation are consequences of destroyed user storage.

The saved effective kernel configuration has CONFIG_EXT4_FS=y but explicitly
disables CONFIG_EXT4_FS_POSIX_ACL. F2FS and tmpfs ACL support do not provide
ACLs for /data's ext4 filesystem. Enable ext4 POSIX ACLs in the final board
fragment and require them in verify-config.py. Keep vold's error handling and
the framework's recovery behavior unchanged.

Both Android and standalone BSP build drivers safely upgrade the exact old
board fragment; revisions and hashes protect custom edits. Rebuild boot.img
and flash it to boot and recovery_boot. No super.img update or filesystem
reformat is part of this fix. Existing user storage needs hardware validation:
the framework previously attempted to remove it during error recovery.

Check /proc/config.gz for CONFIG_EXT4_FS_POSIX_ACL=y, then confirm user 0 is
RUNNING_UNLOCKED in dumpsys user and uptime continues increasing past boot
completion without another prepareUserData failure or reboot request.
