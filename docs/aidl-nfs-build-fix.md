# AIDL API checking on NFS

The pinned AIDL compiler (`e43c97ebcf9a9ce69311080115e1e093a04c1ec7`)
recursively enumerates API snapshots using `dirent.d_type`. It silently skips
`DT_UNKNOWN`, even though some filesystems do not provide entry types. If an
API file is omitted from enumeration but imported by another file, its types
can be present without its default constant references being fully resolved
before API comparison. This is a plausible explanation for the reported
`OperandPerformance.aidl` / `OperandType.FLOAT32` internal assertion on NFS;
the user's actual directory-entry types and failing compiler invocation have
not been reproduced locally.

The patch falls back to `lstat` for unknown types, handles regular files and
directories, and reports lookup errors. It preserves the existing exclusion of
symlinks (including directory cycles). It does not modify AIDL interfaces,
API snapshots, hashes, or equality/compatibility checks.

Validation: the exact directory enumeration function was compiled in an
isolated C++17 harness with a simulated `readdir` that returns unknown types
for one file or every entry. Original: 1/0 of 2 files found; patched: 2/2.
Normal enumeration, symlink-cycle exclusion, missing-directory errors, patch
reverse applicability, and Python syntax checks also passed. This is not a
full AIDL compiler or Android build test. The server rebuild is the final
validation for the reported failure.

Pull the bring-up branch and run the normal `scripts/build.sh` command again.
It applies the compiler patch idempotently and the Android build rebuilds the
host AIDL compiler incrementally. Do not delete `out`, regenerate API dumps,
or bypass API checks. BSP-only fetch/application excludes this host patch.
