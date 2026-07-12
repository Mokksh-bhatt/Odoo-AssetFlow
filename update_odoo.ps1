$conf = "C:\Program Files\Odoo 19.0.20260711\server\odoo.conf"
$log = "C:\Users\mokks\Desktop\AssetFlow_Project\setup_log.txt"
"Starting Odoo Config Update" | Out-File $log

try {
    $content = [System.IO.File]::ReadAllText($conf)
    $content = $content.Replace("addons_path = c:\program files\odoo 19.0.20260711\server\odoo\addons", "addons_path = c:\program files\odoo 19.0.20260711\server\odoo\addons,C:\Users\mokks\Desktop\AssetFlow_Project")
    [System.IO.File]::WriteAllText($conf, $content)
    "Updated odoo.conf successfully." | Out-File -Append $log

    Restart-Service -Name "odoo-server-19.0" -Force
    "Restarted odoo-server-19.0 successfully." | Out-File -Append $log
} catch {
    "Error: $_" | Out-File -Append $log
}
