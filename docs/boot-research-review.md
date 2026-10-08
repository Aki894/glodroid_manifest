# 启动研究评估与第四版实施

## 证据和边界

报告对应当前 Tiramisu 预览系统：GloDroid v0.7.2、SDK 32、Linux 5.15.21、U-Boot 2022.04-rc4。不能按正式 Android 13/现代主线内核推导全部行为。

同一次启动的服务对象创建时间 152415 ms，第一次 CarPlay active 为 186415 ms，差值 34000 ms；约 82% 的时间在服务创建之前，但这不能定位为某个 Android 服务、内核或存储故障。历史上约 127 秒启动完成的记录不能代替本轮分段时间。

`generation=4` 不证明重复建链，关闭也会递增 generation。新增 `sessionStarts` 统计真正调用 controller.start 的次数，并记录车机目标尺寸变化及是否请求重建。首次对象创建时间继续保留在兼容字段 `serviceReadyMs`；新增 `onCreateReadyMs` 表示创建流程完成。

## 本轮实施顺序

| 阶段 | 已实施内容 | 验证与下一步 |
| --- | --- | --- |
| P0 | init 在 post-fs-data 启动固定日志采集，保留本次/上次启动；网页可请求 root 导出 | 不依赖现场 ADB；回收三次冷启动日志定位 152 秒之前的慢段 |
| P1 | 软件包服务可用时启动 root helper；Wi-Fi/蓝牙独立请求；CE 解锁后先完成手机所需权限并请求手机服务，再做维护及车端初始化 | 关键命令非零退出不再视为成功；记录命令耗时、错误输出、超时和实际 radio ON |
| P2 | 悟空派调用者声明仅 2.4 GHz；过滤旧记忆、STA 对齐及默认列表中的 5 GHz | 保留 2.4 GHz 6/1/11 和 system default；普通双频设备保持原行为 |
| P3 | 暂未启用 RFCOMM 与 GO 并行 | 已验证无线流程保持顺序；先用分段记录判断收益，再增加带取消互锁的实验开关 |
| P4 | 暂未延迟车机尺寸变化或移除 Android 服务 | 尚未得到实车目标变化频率和系统慢段；不凭 generation 推导重连原因 |

APEX 激活、fsck、FBE/CE 解锁、PMS 扫描、ART/JIT 是待验证方向。没有直接删除系统模块、修改磁盘布局、关闭 zram/显示服务或超频。第一次启动和已完成初始化的后续启动要分开比较。本轮没有硬件测得的提速秒数。

## 自动日志与断电后的回收

固定位置 `/data/vendor/wukong-boot/current` 和 `previous`，仅 root 可读。新 boot ID 才轮换；最多两次启动。采集从 post-fs-data 开始，连接活跃后约 30 秒结束；失败时最多采集 10 分钟。

- `stages.tsv`：每 5 秒观察 zygote、bridge、CE、sys.boot_completed；精确时间以事件/助手日志为准。
- `logcat.txt[.1,.2]`：selected system/events logcat，monotonic 格式，每次启动最多约 3 MiB；`logcat-first.txt` 保留最早可用片段。
- `kernel-first/final.txt`、`properties-first/final.txt`：有界快照。
- `provision.jsonl`：助手相对启动时间、grant/服务命令耗时与退出码；一行一个 JSON 事件。
- `startup-summary.json`：同 boot ID 的应用时间轴，包括对象创建、onCreate 完成、第一次 session、GO 和 active、sessionStarts。

采集结束一次性 sync，不在启动过程中循环刷盘。突然断电可能丢失最近尚未落盘的尾部；要保留完整现场记录，趁车机仍供电时导出。断电后接回电脑重新启动，上一轮目录仍可导出；再经历两次新启动会覆盖更早记录。

应用文件中仍保留原有 board.log 与健康轮换日志。只更新 APK 的旧镜像能导出 live 快照和应用日志，`collectorPresent=false`；安装包含新 vendor 脚本的镜像后才有自动离线系统记录。

### 车内无需路由器和网线

1. 在电脑旁通过 ADB 转发页面勾选“允许本地网络访问”并确认，保存管理令牌。已有明确 LAN 设置不会被更新擅自改变。
2. 在车内保持盒子供电，将另一台手机/电脑连接盒子 Wi-Fi；打开 `management.urls` 给出的地址，通常为 `http://192.168.49.1:8765/`，使用同一个令牌登录。无法加入当前组时使用已验证的维护热点入口。
3. 点击“保存并下载系统启动日志”。页面请求一次采集、按请求 ID 等待完成，然后下载 ZIP。采集不停止 CarPlay。
4. 确认浏览器已保存 `wukong-boot-diagnostics.zip` 再拔电。Safari 中若未自动保存，使用下载列表/文件 app 保存到“文件”；不要仅凭按钮文字认为下载完成。

导出位于应用私有 `files/boot-diagnostics.zip`，固定白名单输入、每条目最多 256 KiB、没有任意路径/命令接口。导出处理隐藏密码、令牌、私钥字段及 MAC，保留 boot ID、阶段、频率、接口和时间。可用目录缺失会跳过；manifest 标明是否有自动采集器。应用日志和健康日志也包含在 ZIP。

### 断电后在 Windows 导出上次启动

把盒子接回电脑供电，等 ADB 可用；随后使用网页导出（ZIP 含 previous），或读取 root 私有原始日志：

```powershell
& $Adb root
& $Adb wait-for-device
& $Adb pull /data/vendor/wukong-boot/previous .\wukong-previous-boot
```

后者是未脱敏原始日志，仅用于私下排查。不需要同一轮启动保持 ADB，亦不需要几十米网线。当前 Type-C 同时供电/OTG，不建议用未知 Y 线维持供电。

## 安装第四版

最新成功构建 APK 为 `0.2.11-wukongpi.4`，versionCode 40。同签名 `adb install -r board-debug.apk` 保留已有配对/配置；不更新 CarProjection。

服务器保持原目录，`git pull --ff-only` 后运行：

```bash
source /data/ccc/wukong-build/env.sh
cd /data/ccc/wukong-build/port
git pull --ff-only
set -o pipefail
bash scripts/build.sh /data/ccc/wukong-build/aosp 4 \
  2>&1 | tee /data/ccc/wukong-build/logs/build-startup-v4.log
```

下载同次输出 `out/target/product/wukongpi/images.tar.gz`。本轮只新增 vendor 启动/日志脚本，没有新 kernel/DT/U-Boot 修改；已完整安装第三版的板子只需本轮 `super.img` 和第四版 APK，保留 boot、bootloader、env、userdata、metadata：

```powershell
& $Adb install -r .\board-debug.apk
& $Adb reboot fastboot
# 等 fastboot 再次出现，并确认：
fb getvar is-userspace
# 必须返回 yes 后才执行：
fb flash super super.img
fb reboot
```

如果还未完整安装第三版或 recovery 不能进入 fastbootd，按 appliance-startup.md 的同次镜像完整更新顺序操作。本轮不要 `oem format`、重建 GPT 或格式化 userdata/metadata。更新 APK 不会替换正在运行的旧 root app_process；更新结束做一次真正断电再上电，蓝牙模块也一起断电。

## 三次冷启动的比较

保持同一 TF 卡、手机和自动连接配置，不开 scrcpy/视频预览。每次首次 active 后等约 30 秒再导出。比较对象创建、onCreate 完成、权限就绪、radio ON、第一 session、P2P start/ready、RFCOMM/iAP2、first active；以同一 boot ID 对齐，不使用变化的 RTC 墙钟。报告核心慢段后，再挑最大的可验证等待优化。所有三次都应自动连接且不需要手动 iw/按钮，实际车机画面/触摸/音频另行验收。
