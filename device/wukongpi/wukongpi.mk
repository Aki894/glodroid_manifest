# SPDX-License-Identifier: Apache-2.0
$(call inherit-product, device/glodroid/wukongpi/device.mk)

PRODUCT_BOARD_PLATFORM := sunxi
PRODUCT_NAME := wukongpi
PRODUCT_DEVICE := wukongpi
PRODUCT_BRAND := WukongPi
PRODUCT_MODEL := WuKong Pi
PRODUCT_MANUFACTURER := WukongPi

UBOOT_DEFCONFIG := wukongpi_defconfig
KERNEL_SRC := kernel/glodroid-stable
BUILD_KERNEL_USING_GCC := true
KERNEL_DEFCONFIG := $(KERNEL_SRC)/arch/arm/configs/sunxi_defconfig
KERNEL_FRAGMENTS += \
    device/glodroid/platform/common/sunxi/sunxi-common.config \
    device/glodroid/wukongpi/wukongpi.config

KERNEL_DTB_FILE := sun8i-h2-plus-wukongpi.dtb
PRODUCT_COPY_FILES += \
    device/glodroid/platform/tools/gensdimg.sh:$(TARGET_COPY_OUT)/gensdimg.sh

UBOOT_FRAGMENTS += device/glodroid/platform/common/sunxi/uboot.config
