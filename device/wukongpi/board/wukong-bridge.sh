#!/system/bin/sh
# Prepare the second XR819 interface before asking Android to create a P2P GO.
# Never change an existing interface's type or interrupt a running group.
stage() {
    /system/bin/log -t WuKongBridge "BOOT_STAGE $1"
}
stage bridge_started
phone=com.shihab.diplay.hudtest
car=com.projection.car
prepare_network() {
    if [ -d /sys/class/net/wlan0 ] && [ ! -d /sys/class/net/p2p0 ]; then
        /system/bin/iw dev wlan0 interface add p2p0 type managed && /system/bin/ip link set p2p0 up
    fi
}
while true; do
    if [ "$(getprop persist.wukong.bridge.enabled)" = "0" ]; then sleep 5; continue; fi
    prepare_network
    # The root helper can request radios before CE unlock. It gates all private
    # files, grants and app launch on UserManager.isUserUnlocked() itself.
    if service check package 2>/dev/null | grep -q ": found$"; then
        phone_apk=$(timeout 8 pm path "$phone" | sed -n 's/^package://p' | head -n 1)
        car_apk=$(timeout 8 pm path "$car" | sed -n 's/^package://p' | head -n 1)
        if [ -n "$phone_apk" ] && [ -n "$car_apk" ] && [ -r "$phone_apk" ]; then
            stage helper_spawn
            CLASSPATH="$phone_apk" /system/bin/app_process /system/bin com.shilapi.xcertplay.board.BoardProvisioner &
            helper=$!
            # Keep the fixed interface preparation alive if Wi-Fi is re-enabled.
            while kill -0 "$helper" 2>/dev/null; do
                if [ "$(getprop persist.wukong.bridge.enabled)" = "0" ]; then kill "$helper"; break; fi
                prepare_network
                sleep 5
            done
            wait "$helper"
            stage helper_exit
        fi
    fi
    sleep 2
done
