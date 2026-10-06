# 真机启动与验收

本版目标是先看到串口、Android init、zygote/system_server、headless SurfaceFlinger 和 ADB，
随后验证 XR819 STA。512 MB 内存是否足够，需要在板上测量，编译不能证明运行稳定。

## 连接与刷卡

1. 准备单独的 TF 卡，保留现在能工作的 Linux 卡。
2. 接 UART0 的 **3.3 V TTL** 串口，115200 8N1。TX/RX 交叉，GND 共地。
   引脚位置按你的板卡丝印/原理图确认；不要接电脑 RS-232 电平。
3. 完整 `make images` 成功后，解压 `images.tar.gz`。把其中的 **deploy-sd.img**
   写入选定 TF 卡，这是会清除该卡原内容的步骤。
4. TF 卡插板，OTG 接电脑，供电并记录串口。进入 U-Boot fastboot 或 recovery fastbootd 后，
   在解压目录执行上游生成的 `flash-sd.sh`。该脚本写 Android 分区并重启。
   悟空派没有显示输出，进度通过串口与 fastboot 观察。
5. 本机本版未完成上述实机流程。GloDroid 旧 README 仍要求显示器，
   需要验证该板的 headless recovery 与 fastbootd 是否成立；不要把文档步骤当作已通过测试。

这里保留上游 USB 启动和 AOA 状态机，不在 boot_completed 时反复设置 `sys.usb.config`，
防止后续车机切换 accessory 后又被强制拉回 ADB。

## 第一次启动

```bash
adb devices
adb shell getprop sys.boot_completed
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.sdk
adb shell getprop ro.config.low_ram
adb shell cat /proc/meminfo
adb shell cat /proc/pressure/memory
adb shell cat /sys/block/zram0/mm_stat
adb shell dumpsys SurfaceFlinger
adb shell dumpsys usb
```

首次 dex 优化与数据分区初始化可能很久，必须用串口辨别是在初始化还是崩溃循环。
`MemTotal` 小于 512 MiB 是正常的，记录保留内存和 CMA；不要将 `used` 单独当作可用性判断。

## XR819

本版加载点在 `post-fs`，固件已放入 `/vendor/etc/firmware/xr819/`。
cfg80211/mac80211 为 built-in，XR819 为模块，避免依赖动态模块自动加载。

```bash
adb shell 'ls -l /sys/bus/sdio/devices; cat /proc/modules'
adb shell 'ls /sys/class/net; dmesg | grep -iE "xradio|xr819|firmware|mmc1"'
adb shell 'ls -l /vendor/etc/firmware/xr819/'
adb shell cmd wifi status
adb shell dumpsys wifi
```

先验证 SDIO 设备、固件加载、`wlan0`、2.4 GHz STA 扫描与连接。Android Wi-Fi HAL、
SELinux 权限及上层连接尚需真机验证。XR819 保留是当前调试/联网路径，
不代表它提供 5 GHz 或 Bluetooth；RTL8822CS 接入阶段再增加另一版硬件配置。
现有 XR819 驱动的运行、重启和吞吐可靠性需要测试。

## G1 / G2 记录

- G1：串口从 SPL 到 Android 连续；ADB 可用；`sys.boot_completed=1`；
  headless 640×480 可见于 SurfaceFlinger；连续 10 次启动，不发生 watchdog/内核异常。
- G2：512 MB 检测正确，idle 30 分钟；记录 memory PSI、zram、LMKD，
  无 system_server/zygote 重启。既有 260 MB 等数值是目标，不是实测成绩。
- 后续安装 APK 前，再做 AOA 单独验收。当前仅检查 accessory gadget 功能编译存在，
  未证明 Lexus 已识别该系统。

```bash
scripts/collect-debug.sh ./first-boot-debug
```

收集脚本在电脑上保存当前日志；开发板掉电前未传出的 logcat 仍可能丢失。
本版本未增加逐行刷卡或改变现有 Linux 的日志机制。
