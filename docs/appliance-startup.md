# 悟空派：自动启动、现场管理与启动提速

本阶段从“已验证有线/无线 CarPlay、网页按钮和蓝牙配对”推进到可断电恢复的设备。车机画面、Remote Touch、音乐、导航提示、Siri 和通话仍是后续实车验收项。

## 本次实现

1. **无线自动恢复**：init 在 zygote 启动时运行固定助手，先准备 XR819 的第二个 managed 接口 `p2p0`，不改动已存在的 GO；接口消失后再次准备。用户数据解锁后才启动依赖 CE 的 root helper。应用遵循开机连接选项，等待 Wi-Fi/蓝牙/接口就绪时每 2 秒检查，准备阶段不消耗传输错误的指数重试次数。会话失败后原有有界退避继续工作；用户停止仍停止当前会话。
2. **冷启动和稳定性检查**：应用每 15 秒记录状态、PSS、堆、CPU 时间、线程、文件描述符和帧计数，内存保留最近一小时，磁盘轮换两个约 512 KiB 文件。诊断导出带健康样本。Windows 三次冷启动采集脚本，以及通过盒子 Wi-Fi 运行的一小时只读采集工具已加入。
3. **现场网页管理**：在原网页勾选“允许本地网络访问”，确认配置后可即时使用，不再重启服务。状态的 `management.urls` 给出当前真实 IPv4 地址；连接盒子 CarPlay Wi-Fi 的另一台手机/笔记本即可访问该地址的 8765 端口，沿用管理令牌。没有路由器、网线要求。增加维护热点按钮，暂停手机 CarPlay，创建可由普通 Wi-Fi 客户端加入的 P2P GO，状态显示 SSID/密码/地址。它共用 XR819，无法在 Wi-Fi 驱动自身失败时保证救援；维护热点建立失败会报告错误。结束维护恢复 CarPlay。维护热点和 CarPlay 不同时抢占无线组。
4. **缩短启动**：关闭启动动画；U-Boot 倒计时设为 0，保留串口中断入口；内核 `loglevel=4` 降低 115200 串口输出，完整 dmesg 仍保留；助手不等 `sys.boot_completed` 才开始准备接口；权限和电池白名单已满足时跳过命令，根进程维护循环与初始化分开。删除旧安装脚本里的 `am force-stop`，避免已出现的 AppOps 时间异常路径。记录服务就绪及第一次 CarPlay 活跃的内核相对时间。

这些是已实施的优化，不是已测得的秒数。旧日志约 127 秒完成系统启动、129 秒启动助手；更新后需要比较三次冷启动。512 MiB 上保留 zram、显示合成和必要的 Android 服务，未进行超频。

## 更新顺序

先从 DiPlay 的 `integration/wukongpi-headless` 最新成功的 **WukongPi headless bridge** 构建下载 `DiPlay-wukongpi-apk`，解压为 `board-debug.apk`。版本 `0.2.11-wukongpi.3`、versionCode 39。APK 同签名，覆盖安装保留手机配对和配置；无需更新 CarProjection APK。

```powershell
& $Adb install -r .\board-debug.apk
& $Adb shell am start-foreground-service -n com.shihab.diplay.hudtest/com.shilapi.xcertplay.board.BoardService --es command restore
& $Adb forward tcp:8765 tcp:8765
```

APK 更新后旧 root app_process 仍可能运行旧代码。完成下面镜像更新后做一次真正断电上电，一并切换助手。

服务器编译：

```bash
source /data/ccc/wukong-build/env.sh
cd /data/ccc/wukong-build/port
git pull --ff-only
set -o pipefail
bash scripts/build.sh /data/ccc/wukong-build/aosp 4 \
  2>&1 | tee /data/ccc/wukong-build/logs/build-appliance.log
```

下载 `/data/ccc/wukong-build/aosp/out/target/product/wukongpi/images.tar.gz`，解压至 Windows images 目录。本次需要系统侧改动，因此只更新 APK 不足以完成自动接口准备和全部提速。

保持既有 `fb` 失败即抛异常函数，先进入 U-Boot fastboot：

```powershell
& $Adb reboot bootloader
fb devices
fb getvar is-userspace
```

确认 `is-userspace: no`，然后按顺序运行：

```powershell
& {
    fb flash bootloader bootloader-sd.img
    fb flash uboot-env env.img
    fb flash recovery_boot boot.img
    fb flash dtbo_a boot_dtbo.img
    fb reboot-fastboot
}
fb getvar is-userspace
```

等设备重新出现并确认 `is-userspace: yes`，再运行：

```powershell
& {
    fb flash boot boot.img
    fb flash super super.img
    fb reboot
}
```

这是已有可用分区表的更新，不运行 `oem format`、GPT 重建或 userdata/metadata 格式化。全部镜像来自同一轮构建。冷启动测试必须断开开发板及蓝牙模块全部供电：模块 EN 当前上拉，没有可控复位 GPIO，暖重启的旧波特率问题不能靠这次软件改动保证消除。

## 三次冷启动

在手机保持蓝牙/Wi-Fi 开启、开机连接勾选、无线模式 WIFI_P2P/2.4 GHz/Auto、配对已保存时运行：

```powershell
.\collect-cold-boots.ps1 -Adb $Adb -Cycles 3
```

该脚本不控制电源；每轮提示后人工断电再上电。需要当前 userdebug 的 root adbd 读取管理令牌。记录 PC 观察时间和内核相对 `boot.serviceReadyMs`、`boot.firstCarPlayActiveMs`。上电到内核之前的 SPL/U-Boot 时间不包含在应用字段中。每次必须无需 `iw`、点击开始、重新授权就连接；出现失败立即保留记录，不继续循环。

## 一小时稳定性与车内网页

先在 ADB 转发页面勾选 LAN 管理并确认，保存私有管理令牌。将另一台设备加入盒子热点，使用状态中给出的地址；不要假定固定 `192.168.*.*`。关闭 scrcpy，关闭预览，停止网页轮询，用可访问盒子 Wi-Fi 的电脑运行 DiPlay 仓库脚本：

```bash
python3 scripts/collect-board-health.py http://盒子实际IP:8765 --minutes 60
```

工具仅每 15 秒读取一次状态，不执行连接命令，不保存管理令牌或维护热点密码。没有电脑时，关闭网页后应用仍会自行记录资源数据，稍后重新打开网页导出诊断即可。

通过条件：持续活跃、正常画面期间帧数增长、没有持续增多的线程/FD、没有无界 PSS/堆增长、`videoDecoders=0`、没有反复重连。静止画面帧数不增长本身不是失败。状态里 `carTarget=not connected` 表示尚未完成车机端验收。

维护热点须先在仍能访问的网页开启；或在 ADB 可用时启动：

```powershell
& $Adb shell am start-foreground-service -n com.shihab.diplay.hudtest/com.shilapi.xcertplay.board.BoardService --es command maintenance-ap
```

记录 SSID/密码/令牌后，切换普通 Wi-Fi 客户端访问网页。不是默认无密码救援热点。浏览器和令牌依赖同网连接，若该客户端无法加入当前 CarPlay 热点，应使用维护模式。

## 验证边界

提交前已检查追加补丁、所有升级前缀、重复预检、拒绝冲突且保留本地编辑、缺失/现存/创建失败后的 P2P 接口处理，以及网页请求回归。APK 的单元测试、lint、缩包和签名由 GitHub Actions 验证。三次真实断电、一小时板端运行和实测启动缩短量必须由上述板端采集完成；目前不能标成已通过。
