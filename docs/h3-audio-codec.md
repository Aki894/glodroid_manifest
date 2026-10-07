# Enable the H3 internal audio codec

The hardware diagnostic capture reported no ALSA soundcards and an uninitialized
AudioPolicyManager. The effective kernel configuration already enabled
SND_SUN4I_CODEC and SND_SUN8I_CODEC_ANALOG, but the inherited H3 codec device-tree
node remained disabled.

Enable that node and connect the Line Out DAPM endpoint to LINEOUT. Both endpoint
names and the existing audio.wukongpi.xml mixer controls match the pinned kernel
1105b4a935d6e5986b6c8858dd08c2c4bee88ef2. No external microphone route is added:
board wiring and actual playback/capture require hardware verification.

The DTS migration accepts only the exact pre-KMS and pre-codec board files at the
locked kernel revision. Custom changes remain untouched. The effective kernel
configuration audit now also requires the digital and analog codec drivers.

Validation: compiled the board DTS with pinned kernel includes; checked the
resulting codec status, audio route and analog-control reference. Checked fresh
patch application, reverse-check after migration, repeated migration, wrong
revision refusal and custom-edit preservation. The saved baseline configuration
contains both audio drivers. This is not an on-board audio test or a full build.

Rebuild with scripts/build.sh. Update boot.img in boot and recovery_boot, and
boot_dtbo.img in dtbo_a. No super.img rebuild deployment or data formatting is
needed for this DTS change. After reboot inspect /proc/asound/cards,
/proc/asound/pcm and dumpsys media.audio_policy. The expected internal card is
H3 Audio Codec; confirm its index matches the configured card 0 before playback.
