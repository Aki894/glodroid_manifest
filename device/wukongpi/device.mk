# SPDX-License-Identifier: Apache-2.0
$(call inherit-product, device/glodroid/common/lowram/device-common-1gb.mk)
$(call inherit-product, device/glodroid/common/device-common-sunxi.mk)
# XR819 has no Bluetooth. Add RTL8822CS and its HAL in a later product revision.
$(call inherit-product, device/glodroid/common/bluetooth/no-bluetooth.mk)

PRODUCT_PACKAGES += libGLES_android
PRODUCT_VENDOR_PROPERTIES += \
    ro.opengles.version=131072
PRODUCT_SYSTEM_PROPERTIES += persist.sys.usb.config=adb

PRODUCT_COPY_FILES += \
    device/glodroid/opi_plus2e/audio.opi_plus2e.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio.wukongpi.xml \
    device/glodroid/wukongpi/init.wukongpi.rc:$(TARGET_COPY_OUT_VENDOR)/etc/init/init.wukongpi.rc \
    kernel/firmware/xr819/boot_xr819.bin:$(TARGET_COPY_OUT_VENDOR)/etc/firmware/xr819/boot_xr819.bin \
    kernel/firmware/xr819/fw_xr819.bin:$(TARGET_COPY_OUT_VENDOR)/etc/firmware/xr819/fw_xr819.bin \
    kernel/firmware/xr819/sdd_xr819.bin:$(TARGET_COPY_OUT_VENDOR)/etc/firmware/xr819/sdd_xr819.bin
