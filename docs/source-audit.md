# 源码核对与取舍

全部确切提交记录在 `sources.lock.json`。本页对应 2026-10-07 第一版。

| 源码 | 核对结果 |
|---|---|
| GloDroid/glodroid_manifest v0.7.2 | README 明确写 2022-03-12 Android master；opi_pc 暂不支持；AOSP 的 1119 个项目均有明确 revision |
| GloDroid/glodroid_device v0.7.2 | opi_pc 是 ARMv7，继承低 RAM；包含 256 MiB zram；USB rc 包含 accessory/ADB PID 切换 |
| GloDroid/glodroid_forks kernel-stable-v0.7.1 | Linux 5.15.21；包含 AOA configfs 代码；没有 fifteenhex XR819 驱动 |
| GloDroid/glodroid_forks uboot-v0.7.1 | 有 Orange Pi Zero DTS/defconfig，可以派生；版本为 2022.04-rc4 |
| GloDroid drm_hwcomposer-v0.7.2 | headless 默认 1024×768；使用产品 Soong 开关仅对 WukongPi 选择 640×480 |
| guimoyun/wukongpi-build | H2+、256/512 MB、无视频输出；DTS 与 Orange Pi Zero 基本同源；DRAM 使用 408 MHz，非 Zero 默认 624 MHz |
| fifteenhex/xradio | 当前悟空派 BSP 同样锁定 3ce657a…；驱动依赖 xradio,xr819 节点与 PG10 host-wake |
| armbian/firmware | 原 GloDroid manifest 的锁定提交中已有三份 XR819 固件 |

## 第一版修改

1. 保留悟空派兼容字符串和供电/复位/SDIO，适配 5.15 和 2022 U-Boot 的 DTS include。
2. U-Boot 从 Zero 派生，使用悟空派 DRAM 参数，继续运行 GloDroid 原 Android bootscript。
3. 不改 U-Boot 默认 512 MB 适用的加载地址；不声称兼容 256 MB SKU。
4. 基于 opi_pc 的 Android 产品结构，但不继承其不同硬件 DTS。
5. XR819 导入内核编译系统，固件在 vendor 可见时加载；未导入新版内核才需要的 timer_delete_sync 补丁。
6. CMA 从 256 改为 32 MiB，启用新版名称 MEMCG/MEMCG_SWAP。
   原 Android fragment 中旧 CGROUP_MEM_RES_CTLR 名称不能保证启用新版 cgroup 功能。
7. 为本产品跳过相机 HAL 与附加预装 APK；保留 Launcher、Settings、Wi-Fi 和 USB framework，
   先减少 32-bit 相机配置冲突及不必要内存占用，不在初版大规模裁剪 framework。
8. 相机 VINTF 声明与被排除的 HAL 一同移除；公共产品修改受 TARGET_PRODUCT 条件约束。
9. U-Boot pylibfdt 的版本字符串改成 PEP 440 可接受格式，便于在当前 setuptools 上构建。
   不改变其二进制版本或启动行为。

## 尚未证明的部分

完整 AOSP/Soong/VINTF 构建是否通过、640×480 headless userspace 是否正常、ADB USB 实机枚举、
Android Wi-Fi HAL 是否能管理 XR819、512 MB 的运行余量、反复启动稳定性、AOA 实车识别。
这是下一轮 Actions 构建与真机日志需要回答的问题。

## 公开原始资料

- <https://github.com/GloDroid/glodroid_manifest/tree/v0.7.2>
- <https://github.com/GloDroid/glodroid_device/tree/v0.7.2>
- <https://github.com/GloDroid/glodroid_forks/tree/kernel-stable-v0.7.1>
- <https://github.com/GloDroid/glodroid_forks/tree/uboot-v0.7.1>
- <https://github.com/GloDroid/glodroid_forks/tree/drm_hwcomposer-v0.7.2>
- <https://github.com/guimoyun/wukongpi-build>
- <https://github.com/fifteenhex/xradio>
- <https://github.com/armbian/firmware/tree/4df7fecf02b2940150277a3daa40078e49fbd88c/xr819>
