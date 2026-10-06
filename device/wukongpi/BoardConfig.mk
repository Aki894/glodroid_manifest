# SPDX-License-Identifier: Apache-2.0
include device/glodroid/common/boardconfig-common.mk

TARGET_ARCH := arm
TARGET_ARCH_VARIANT := armv7-a-neon
TARGET_CPU_VARIANT := generic
TARGET_CPU_ABI := armeabi-v7a
TARGET_CPU_ABI2 := armeabi
TARGET_SUPPORTS_32_BIT_APPS := true
TARGET_SUPPORTS_64_BIT_APPS := false
TARGET_BOARD_INFO_FILE := device/glodroid/wukongpi/board-info.txt
DEVICE_MANIFEST_FILE := device/glodroid/wukongpi/manifest.xml

SOONG_CONFIG_NAMESPACES += wukongpi
SOONG_CONFIG_wukongpi += lowram
SOONG_CONFIG_wukongpi_lowram := true

BOARD_KERNEL_CMDLINE += console=ttyS0,115200 earlycon psi=1 cma=32M
