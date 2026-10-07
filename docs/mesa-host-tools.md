# Mesa host tools in the Android build

The pinned GloDroid Mesa fork is `c24db960c40e483687258585674ae5a9dc4053ec`
(`mesa3d-v0.7.2`). Its `android/mesa3d_cross.mk` invokes a bare `meson`
command after prepending system directories to Android's restricted PATH.
A Meson installed only in the caller's Python virtualenv is reached through
Android's PATH interposer and is rejected as an unlisted host tool.
Separately, Mesa discovers `python3` by name and tests its Mako installation;
selecting the system Python can lose the virtualenv dependencies.

The build driver captures `sys.executable` before envsetup changes PATH,
checks Meson 0.61.5 and Mako in that interpreter, and passes the interpreter
as a Make command-line variable. It deliberately does not canonicalize the
Python symlink: doing so would lose virtualenv activation. The Mesa recipe
starts `python -m mesonbuild.mesonmain` with this absolute interpreter path,
puts that interpreter's directory first for Python helper discovery, and
uses an absolute path to the AOSP prebuilt Ninja for the build. Tool paths
are encoded in the generated recipe rather than relying on arbitrary
environment variables being inherited by Ninja. The global tool allowlist
is unchanged. pkg-config remains `/usr/bin/pkg-config` as in the upstream
cross file; the driver now checks for it before building.

Validation: forward/reverse patch applicability on the exact Mesa commit,
Python and shell syntax, and a minimal real Meson 0.61.5 project using the
new recipe prefixes with a rejecting bare `meson` on PATH. Configuration,
virtualenv Python/Mako discovery and a Ninja custom target passed. The
probe used a test Ninja in the prebuilt location; it does not validate the
actual Android prebuilt binary or Mesa cross compilation. Final validation
requires the user's incremental Android build. No output cleanup is needed.

Pull `wukongpi-bringup`, activate the existing wukong-build virtualenv and
rerun `scripts/build.sh`. The Mesa patch is applied idempotently; it is
excluded from BSP-only fetching and patching.
