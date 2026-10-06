# Oracle AI Copilot — Dang ky Task Scheduler tu dong khoi dong khi bat may
# Chay file nay 1 LAN DUY NHAT voi quyen Administrator:
#   Right-click > "Run with PowerShell" (hoac "Run as Administrator")

$taskName  = "OracleAICopilot_Startup"
$batFile   = "d:\2026\oracle_ai\start_all_services.bat"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Dang ky Task Scheduler cho Oracle AI Copilot" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Kiem tra quyen Admin
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[!!] Ban can chay file nay voi quyen Administrator!" -ForegroundColor Red
    Write-Host "     Right-click file .ps1 > 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

# Xoa task cu neu ton tai
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "[..] Tim thay task cu, dang xoa..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Tao action va trigger
$action  = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$batFile`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet `
    -RunOnlyIfNetworkAvailable:$false `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

# Dang ky task voi quyen cao nhat (HIGHEST — de net start hoat dong)
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName  $taskName `
    -Action    $action `
    -Trigger   $trigger `
    -Settings  $settings `
    -Principal $principal `
    -Force | Out-Null

Write-Host ""
Write-Host "[OK] Da dang ky Task Scheduler thanh cong!" -ForegroundColor Green
Write-Host "     Ten task : $taskName" -ForegroundColor White
Write-Host "     Trigger  : Khi dang nhap (At Logon)" -ForegroundColor White
Write-Host "     Quyen    : HIGHEST (de khoi dong Windows Services)" -ForegroundColor White
Write-Host "     File bat : $batFile" -ForegroundColor White
Write-Host ""
Write-Host "  Lan sau bat may, tat ca dich vu se tu dong khoi dong." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Nhan Enter de dong cua so nay"
