<#
Refaz todos os resultados da pesquisa, na ordem certa.

Uso, na raiz do repositório:
    .\scripts\reproduzir_tudo.ps1           # completo, com as sementes do relatório (algumas horas)
    .\scripts\reproduzir_tudo.ps1 -Rapido   # poucas sementes, em reports_teste/, só para conferir que tudo roda
    .\scripts\reproduzir_tudo.ps1 -Refazer  # não reaproveita o progresso salvo das avaliações longas

Com a configuração versionada, o modo completo reproduz os arquivos de reports/
(as sementes são fixas). Cada script grava um *_meta.json com o commit e a
configuração usados. O AMLworld só entra se já tiver sido importado para
data/external/ (ver data/README.md).
#>
param([switch]$Rapido, [switch]$Refazer)

$ErrorActionPreference = "Stop"
$python = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }
$env:PYTHONIOENCODING = "utf-8"

if ($Rapido) {
    $saida, $sementes, $online = "reports_teste", 2, @("--cenarios", "realista", "--sementes", "1")
} else {
    $saida, $sementes, $online = "reports", 10, @("--sementes", "3")
}
# avaliar_deteccao_online.py e avaliar_externo.py reaproveitam cortes e janelas já salvos
# (não use "$x = if ... else { @() }": o PowerShell transforma o vetor vazio em $null)
# (e os nomes de variável não diferenciam maiúsculas: um vetor $refazer seria o próprio $Refazer)
$opcaoRefazer = @()
if ($Refazer) { $opcaoRefazer = @("--refazer") }

function Rodar([string]$descricao, [string[]]$argumentos) {
    Write-Host "`n== $descricao" -ForegroundColor Cyan
    $inicio = Get-Date
    # O Windows PowerShell trata qualquer texto no stderr (até um aviso do SciPy) como erro
    # fatal quando $ErrorActionPreference = "Stop": o que decide é o código de saída.
    $ErrorActionPreference = "Continue"
    & $python @argumentos
    $codigo = $LASTEXITCODE
    $ErrorActionPreference = "Stop"
    if ($codigo -ne 0) { throw "falhou: $descricao (código $codigo)" }
    Write-Host ("   pronto em {0:N0} s" -f ((Get-Date) - $inicio).TotalSeconds)
}

Rodar "dataset sintético" @("scripts/gerar_dataset.py")
Rodar "uma rodada completa" @("scripts/rodar_experimento.py", "--saida", $saida)
Rodar "robustez ($sementes sementes)" @("scripts/avaliar_robustez.py", "--sementes", $sementes, "--saida", $saida)
Rodar "cenários de dificuldade" @("scripts/avaliar_cenarios.py", "--sementes", $sementes, "--saida", $saida)
Rodar "detecção a tempo" (@("scripts/avaliar_deteccao_online.py") + $online + @("--saida", $saida) + $opcaoRefazer)
$poucas = if ($Rapido) { 2 } else { 5 }
Rodar "ablação e teto supervisionado" @("scripts/avaliar_atributos.py", "--sementes", $poucas, "--saida", $saida)
Rodar "culpa por associação" @("scripts/avaliar_propagacao.py", "--sementes", $sementes, "--saida", $saida)

if ($Rapido) {
    Write-Host "`nAMLworld pulado no modo rápido (cada janela leva minutos)."
} else {
    foreach ($nome in @("amlworld_pix", "amlworld")) {
        if (Test-Path "data\external\$nome") {
            Rodar "AMLworld ($nome)" (@("scripts/avaliar_externo.py", "--dados", "data/external/$nome",
                                        "--saida", "$saida/amlworld") + $opcaoRefazer)
        } else {
            Write-Host "`nAMLworld ($nome) não importado: pulado (ver data/README.md)."
        }
    }
}

Write-Host "`nTudo pronto. Resultados em $saida/." -ForegroundColor Green
