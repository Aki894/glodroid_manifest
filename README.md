# WukongPi GloDroid bring-up, revision 1

这是悟空派 **512 MB、ARMv7、无显示器** Android 启动移植的第一版源码工程。
基线锁定 GloDroid v0.7.2，保留板载 **XR819**。现阶段不安装 DiPlay 或 CarProjection。

**范围：已经编译验证板级组件；完整 Android 镜像和真机启动尚未验证。**
`build-bsp.sh` 输出的 `artifacts/` 是组件，不是可直接烧录的 Android 系统。

## 当前配置

| 项目 | 配置 |
|---|---|
| AOSP | GloDroid v0.7.2 锁定的 2022-03-12 master 快照 |
| 内核 | GloDroid kernel-stable-v0.7.1，Linux 5.15.21 |
| U-Boot | GloDroid uboot-v0.7.1，2022.04-rc4 |
| CPU/ABI | H2+/H3 家族，32-bit ARMv7 / NEON |
| DRAM | 使用悟空派 BSP 的 408 MHz、ZQ=3881979、ODT 参数；容量由 SPL 检测 |
| XR819 | MMC1/SDIO，PA20 供电使能，PL7 复位，PG10 host-wake |
| XR819 驱动 | fifteenhex/xradio，锁定与当前悟空派 BSP 相同提交 |
| 固件 | 从原 GloDroid manifest 锁定的 armbian/firmware 复制三份 XR819 文件 |
| USB OTG | peripheral，保留 ADB 与 AOA configfs 支持 |
| UART0 | 115200 8N1，串口日志与 earlycon |
| 内存 | low_ram、PSI、memory cgroup、256 MiB zram，CMA 从 256 改为 32 MiB |
| 图形 | 保留 Lima/minigbm；禁用实体 DE/HDMI；HWC headless 降为 640×480 |
| 蓝牙 | 目前不启用；XR819 本身无蓝牙 |

v0.7.2 **不是正式 Android 12/12L release 分支**。其 README 写明基于当时 AOSP master，
内核 localversion 也包含 android13。准确版本以最终镜像的 `ro.build.version.*` 为准。
上游 Orange Pi PC 产品在此 tag 标注 temporarily unsupported；保留配置不等于已验证支持。

## GitHub Actions

先只 fork <https://github.com/GloDroid/glodroid_manifest> 到自己的账号。
将本工程文件加入 fork 的独立 `wukongpi-bringup` 分支，保留原来的 `aosp.xml`、
`glodroid.xml`、`default.xml` 和 `lightweight.xml`。不需要分别 fork 内核或 XR819。

- `bsp.yml`：推送相关源码或手动运行即可在 `ubuntu-22.04` 构建 U-Boot、内核、DTB、XR819 模块。
- `android.yml`：手动运行，在有足够磁盘、RAM 和 Docker 的 runner 中构建 `images.tar.gz`。
  默认标签为 `["self-hosted","linux","x64","android-build"]`。
  推荐至少 **300 GiB 空闲磁盘、32 GiB RAM**，最好准备 400 GiB / 64 GiB。
  工作流不会自行购买或创建 runner。普通 BSP runner 与完整 AOSP 构建的资源需求不同。
- 两个工作流均上传产物及失败日志；未安装运行本工程前，不会远程刷写开发板。

当前交付包含工作流文件，**不代表 GitHub 已经运行过它们**。

## 本地仅构建 BSP

Ubuntu 22.04 x86-64：

```bash
sudo apt-get update
sudo apt-get install -y build-essential bison flex bc cpio libssl-dev libelf-dev \
  libgmp-dev libmpc-dev libmpfr-dev device-tree-compiler swig python3-dev \
  python3-setuptools python3-pyelftools
python3 scripts/fetch-bsp.py /path/to/bsp-source
scripts/build-bsp.sh /path/to/bsp-source /path/to/bsp-output 4
```

脚本先核对提交及补丁冲突，再应用全部补丁。重复执行会识别已应用状态；
不会替你重置已有仓库。BSP 构建不需要完整 AOSP 源码。

## 完整 Android 构建

使用 Ubuntu 20.04 x86-64 或提供的 Actions 容器。依赖列表见 `android.yml`，
安装 Android 的 `repo` 工具后执行：

```bash
scripts/sync-source.sh /path/to/glodroid-wukongpi 4
scripts/build.sh /path/to/glodroid-wukongpi 8
```

同步脚本使用 GloDroid 的历史 `lightweight.xml`，所有 AOSP 项目都有明确提交。
构建脚本通过 `lunch wukongpi-userdebug` 和上游 `make images` 生成
`out/target/product/wukongpi/images.tar.gz`，并保存解析后的 manifest。
本版本固定用原 GloDroid ARM GCC 编译内核，与 BSP 编译验证一致。

刷卡及验收见 [docs/bringup.md](docs/bringup.md)。不要将组件包或 `images.tar.gz` 直接作为磁盘镜像写入 TF 卡。

## 工程结构

- `patches/`：对四个锁定源码仓库的完整补丁，XR819 源码已随内核补丁提供。
- `device/wukongpi/`：产品、低内存、init 与 VINTF 配置的可读副本。
- `kernel/`、`uboot/`：适配历史树的 DTS 和 DRAM 配置副本。
- 内核补丁中包含 XR819 驱动；功能未改，修正 Kconfig help 和移除强制模块赋值。
- `scripts/`：预检、同步、构建、有效配置核验和 ADB 日志收集。
- `sources.lock.json`：全部基线提交与来源。
- `validation/`：实际构建日志及验证结果。

## 来源与许可

GloDroid 产品/脚本继承 Apache-2.0；Linux 与 XR819 继承其 GPL 许可；
悟空派 DTS 保留原双许可头；U-Boot 继承其源码许可。新文件使用 Apache-2.0，
对既有文件的修改遵循该文件原许可。固件不重新授权，完整镜像中的固件沿用
armbian/firmware 的原许可条件。本工程不包含 CarPlay 认证密钥或第三方 APK。

源码依据及修改理由见 [docs/source-audit.md](docs/source-audit.md)。
