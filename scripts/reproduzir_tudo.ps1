<#
Atalho para scripts/reproduzir_tudo.py, que refaz todos os resultados na ordem certa.

Uso, na raiz do repositório:
    .\scripts\reproduzir_tudo.ps1           # = python scripts/reproduzir_tudo.py
    .\scripts\reproduzir_tudo.ps1 -Rapido   # = --rapido
    .\scripts\reproduzir_tudo.ps1 -Refazer  # = --refazer

Outras opções (--etapas, --listar...) vão direto: .\scripts\reproduzir_tudo.ps1 --listar
#>
param([switch]$Rapido, [switch]$Refazer, [Parameter(ValueFromRemainingArguments)] $Resto)

$python = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }
$opcoes = @()
if ($Rapido) { $opcoes += "--rapido" }
if ($Refazer) { $opcoes += "--refazer" }
if ($Resto) { $opcoes += $Resto }
& $python scripts/reproduzir_tudo.py @opcoes
exit $LASTEXITCODE
