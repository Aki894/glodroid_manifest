#!/system/bin/sh
# Fixed early boot recorder. No network, CE dependency, shell input or permanent tracing.
umask 077
root=/data/vendor/wukong-boot
[ ! -L "$root" ] || exit 1
mkdir -p "$root" || exit 1
chmod 700 "$root"
boot_id=$(cat /proc/sys/kernel/random/boot_id) || exit 1
[ -n "$boot_id" ] || exit 1
[ ! -L "$root/current" ] && [ ! -L "$root/previous" ] || exit 1
old_id=$(cat "$root/current/boot-id" 2>/dev/null)
if [ "$old_id" != "$boot_id" ]; then
    rm -rf "$root/previous"
    [ ! -d "$root/current" ] || mv "$root/current" "$root/previous" || exit 1
    mkdir "$root/current" || exit 1
    echo "$boot_id" > "$root/current/boot-id"
fi
out=$root/current
# Re-entering this oneshot on the same boot never discards completed evidence.
[ ! -f "$out/capture-finished" ] || exit 0
stage() {
    read elapsed rest < /proc/uptime
    printf '%s\t%s\n' "$elapsed" "$1" >> "$out/stages.tsv"
}
snapshot() {
    dmesg | head -c 262144 > "$out/kernel-$1.txt"
    getprop | head -c 131072 > "$out/properties-$1.txt"
}
stage collector_started
snapshot first
# Keep selected system timing and errors, with at most 3 x 1 MiB per boot.
logcat -b main -b system -b events -v monotonic -f "$out/logcat.txt" -r 1024 -n 2 \
    '*:W' SystemServerTiming:V SystemServerInitThreadPool:V UserController:I \
    ActivityManager:I PackageManager:I WuKongProvision:V WuKongBridge:V \
    WuKongBoard:V WifiP2pService:V WifiP2pManager:V BluetoothManagerService:I \
    boot_progress_start:I boot_progress_preload_start:I boot_progress_preload_end:I \
    boot_progress_system_run:I boot_progress_pms_start:I boot_progress_pms_system_scan_start:I \
    boot_progress_pms_data_scan_start:I boot_progress_pms_scan_end:I boot_progress_pms_ready:I \
    boot_progress_ams_ready:I boot_progress_enable_screen:I > /dev/null 2>&1 &
logger=$!
trap 'kill "$logger" 2>/dev/null; wait "$logger" 2>/dev/null' EXIT
trap 'exit 0' TERM INT
seen_ce=0
seen_boot=0
last_zygote=
last_bridge=
active_seen=0
# 10 minutes from collector launch, or 30 seconds after the first active session.
for tick in $(seq 1 120); do
    zygote=$(getprop init.svc.zygote)
    bridge=$(getprop init.svc.wukong_bridge)
    if [ "$zygote" != "$last_zygote" ]; then stage "zygote=$zygote"; last_zygote=$zygote; fi
    if [ "$bridge" != "$last_bridge" ]; then stage "wukong_bridge=$bridge"; last_bridge=$bridge; fi
    if [ "$seen_ce" = 0 ] && [ "$(getprop sys.user.0.ce_available)" = true ]; then stage user_ce_available; seen_ce=1; fi
    if [ "$seen_boot" = 0 ] && [ "$(getprop sys.boot_completed)" = 1 ]; then stage boot_completed; seen_boot=1; fi
    startup=/data/user/0/com.shihab.diplay.hudtest/files/board-startup.json
    if [ "$active_seen" = 0 ] && [ -f "$startup" ] && [ ! -L "$startup" ] &&
        grep -q "$boot_id" "$startup" && grep -Eq '"firstCarPlayActiveMs"[[:space:]]*:[[:space:]]*[1-9][0-9]*' "$startup"; then
        active_seen=$tick
        stage first_active_observed
    fi
    if [ "$active_seen" != 0 ] && [ "$tick" -ge "$((active_seen + 6))" ]; then break; fi
    sleep 5
done
stage collector_finished
snapshot final
if [ -f "$startup" ] && [ ! -L "$startup" ] && grep -q "$boot_id" "$startup"; then
    head -c 4096 "$startup" > "$out/startup-summary.json"
fi
kill "$logger" 2>/dev/null
wait "$logger" 2>/dev/null
trap - EXIT
# The exporter keeps bounded tails; preserve the oldest available timing prefix too.
for oldest in "$out/logcat.txt.2" "$out/logcat.txt.1" "$out/logcat.txt"; do
    if [ -f "$oldest" ] && [ ! -L "$oldest" ]; then head -c 262144 "$oldest" > "$out/logcat-first.txt"; break; fi
done
stage flush_started
# One flush after connection settles; no repeated sync during boot.
sync
echo complete > "$out/capture-finished"
