#!/system/bin/sh
# Fixed package entry point. Never run a shell command received from the Web UI.
while true; do
    if [ "$(getprop persist.wukong.bridge.enabled)" = "0" ]; then
        sleep 30
        continue
    fi
    phone_apk=$(pm path com.shihab.diplay.hudtest 2>/dev/null | sed -n 's/^package://p' | head -n 1)
    car_apk=$(pm path com.projection.car 2>/dev/null | sed -n 's/^package://p' | head -n 1)
    if [ -n "$phone_apk" ] && [ -n "$car_apk" ] && [ -r "$phone_apk" ]; then
        CLASSPATH="$phone_apk" /system/bin/app_process /system/bin com.shilapi.xcertplay.board.BoardProvisioner
    fi
    sleep 5
done
