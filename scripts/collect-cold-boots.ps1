param(
    [Parameter(Mandatory=$true)][string]$Adb,
    [ValidateRange(1,10)][int]$Cycles=3,
    [ValidateRange(60,900)][int]$TimeoutSeconds=300,
    [string]$Report=(Join-Path $PWD 'wukong-cold-boots.jsonl')
)
$ErrorActionPreference='Stop'
if (!(Test-Path -LiteralPath $Adb -PathType Leaf)) {throw '找不到 adb.exe'}
# One board; preserve application state and phone pairing records.
for ($cycle=1; $cycle -le $Cycles; $cycle++) {
    Read-Host "第 $cycle/$Cycles 次：断开开发板和蓝牙模块的全部供电。回车后立即重新上电；iPhone 保持蓝牙/Wi-Fi 开启" | Out-Null
    $started=[System.Diagnostics.Stopwatch]::StartNew()
    $deadline=(Get-Date).AddSeconds($TimeoutSeconds)
    $connected=$false; $rootRequested=$false; $active=$false; $token=''; $snapshot=$null
    while ((Get-Date) -lt $deadline) {
        $devices=@(& $Adb devices | Where-Object {$_ -match '^\S+\s+device$'})
        if ($devices.Count -gt 1) {throw '请只连接一个 ADB 设备'}
        if ($devices.Count -eq 1) {
            if (!$rootRequested) {
                & $Adb root | Out-Null
                if ($LASTEXITCODE -ne 0) {throw '当前 userdebug 设备无法启用 root adbd'}
                $rootRequested=$true
                Start-Sleep -Seconds 1
                continue
            }
            if (!$connected) {
                & $Adb forward tcp:8765 tcp:8765 | Out-Null
                $connected=$true
            }
            if (!$token) {
                # Requires the current userdebug adbd root configuration.
                $candidate=(& $Adb shell cat /data/user/0/com.shihab.diplay.hudtest/no_backup/web-token 2>$null) -join ''
                if ($candidate.Trim() -match '^[0-9a-f]{64}$') {$token=$candidate.Trim()}
            }
            if ($token) {
                try {
                    $snapshot=Invoke-RestMethod 'http://127.0.0.1:8765/api/v1/status' -Headers @{Authorization="Bearer $token"} -TimeoutSec 5
                    if ($snapshot.state -in @('WirelessActive','active')) {$active=$true;break}
                } catch { }
            }
        }
        Start-Sleep -Seconds 2
    }
    $elapsed=$started.Elapsed.TotalSeconds
    if ($snapshot -and $snapshot.management -and $snapshot.management.maintenanceHotspot) {
        $snapshot.management.maintenanceHotspot.PSObject.Properties.Remove('passphrase')
    }
    $result=[ordered]@{cycle=$cycle;active=$active;observedSeconds=$elapsed;note='人工上电延迟计入 PC 计时；board boot 字段从内核启动计时';status=$snapshot}
    $result | ConvertTo-Json -Depth 12 -Compress | Add-Content -LiteralPath $Report -Encoding utf8
    Write-Host "第 $cycle 次 active=$active, PC 观察用时 $([math]::Round($elapsed,1)) 秒"
    if (!$active) {throw "本轮未连接成功，记录已写入 $Report。先检查启动状态；不继续断电循环。"}
}
Write-Host "三项分别检查：每次自动连接、没有 iw/手动开始、boot.firstCarPlayActiveMs 可比较。记录：$Report"
