#!/system/bin/sh
# Prepare the second XR819 interface before asking Android to create a P2P GO.
# Never change an existing interface's type or interrupt a running group.
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
    # app_process needs installed packages and CE storage; network preparation does not.
    if [ "$(getprop sys.user.0.ce_available)" = "true" ] || [ "$(getprop sys.boot_completed)" = "1" ]; then
        phone_apk=$(pm path "$phone" | sed -n 's/^package://p' | head -n 1)
        car_apk=$(pm path "$car" | sed -n 's/^package://p' | head -n 1)
        if [ -n "$phone_apk" ] && [ -n "$car_apk" ] && [ -r "$phone_apk" ]; then
            CLASSPATH="$phone_apk" /system/bin/app_process /system/bin com.shilapi.xcertplay.board.BoardProvisioner &
            helper=$!
            # Keep the fixed interface preparation alive if Wi-Fi is re-enabled.
            while kill -0 "$helper" 2>/dev/null; do
                if [ "$(getprop persist.wukong.bridge.enabled)" = "0" ]; then kill "$helper"; break; fi
                prepare_network
                sleep 5
            done
            wait "$helper"
        fi
    fi
    sleep 2
done
