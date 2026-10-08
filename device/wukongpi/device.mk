# SPDX-License-Identifier: Apache-2.0
$(call inherit-product, device/glodroid/common/lowram/device-common-1gb.mk)
$(call inherit-product, device/glodroid/common/device-common-sunxi.mk)
# External RTL8761BTV on UART2, initialized by the kernel H5 serdev driver.
$(call inherit-product, device/glodroid/common/bluetooth/bluetooth.mk)

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

# UART firmware/config (not the similarly named RTL8761BU USB firmware).
PRODUCT_COPY_FILES += \
    vendor/realtek/rtkbt/rtkbt-firmware/lib/firmware/rtlbt/rtl8761b_fw:$(TARGET_COPY_OUT_VENDOR)/etc/firmware/rtl_bt/rtl8761b_fw.bin \
    vendor/realtek/rtkbt/rtkbt-firmware/lib/firmware/rtlbt/rtl8761b_config:$(TARGET_COPY_OUT_VENDOR)/etc/firmware/rtl_bt/rtl8761b_config.bin

# Fixed root provisioning entry point for the two headless board APKs.
PRODUCT_COPY_FILES += \
    device/glodroid/wukongpi/board/wukong-bootlog.sh:$(TARGET_COPY_OUT_VENDOR)/bin/wukong-bootlog.sh \
    device/glodroid/wukongpi/board/wukong-bridge.sh:$(TARGET_COPY_OUT_VENDOR)/bin/wukong-bridge.sh \
    device/glodroid/wukongpi/board/init.wukong-bridge.rc:$(TARGET_COPY_OUT_VENDOR)/etc/init/init.wukong-bridge.rc


# Dedicated forwarding appliance: do not render a boot animation on the H3.
PRODUCT_SYSTEM_PROPERTIES += debug.sf.nobootanimation=1
