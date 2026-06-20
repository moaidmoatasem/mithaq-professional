$f = 'C:\Users\moaid\AppData\Roaming\Qoder\SharedClientCache\mcp.json'
$c = Get-Content $f -Raw
$c = $c.Replace('"REDIS_URL"', '"redis://localhost:6379"')
Set-Content -Path $f -Value $c -NoNewline

$f2 = 'C:\Users\moaid\AppData\Roaming\Qoder\SharedClientCache\extension\local\mcp.json'
$c2 = Get-Content $f2 -Raw
$c2 = $c2.Replace('"REDIS_URL"', '"redis://localhost:6379"')
Set-Content -Path $f2 -Value $c2 -NoNewline
