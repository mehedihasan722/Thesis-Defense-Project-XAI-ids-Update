# Export using Word without letting it rewrite the preserved OOXML package.
$ErrorActionPreference = 'Stop'
$projectDirectory = Split-Path -Parent $PSScriptRoot
$inputDocument = Join-Path $projectDirectory 'output\docx\thesis_xai_ids_preserved.docx'
$outputPdf = Join-Path $projectDirectory 'output\pdf\thesis_xai_ids_preserved.pdf'
$cacheFile = Join-Path $projectDirectory 'results\study\preserved_report\field-values.json'
$wordApp = New-Object -ComObject Word.Application
$wordApp.Visible = $false
$wordApp.DisplayAlerts = 0
try {
    $draftDoc = $wordApp.Documents.Open($inputDocument, $false, $true)
    $draftDoc.Repaginate()
    $draftDoc.Fields.Update() | Out-Null
    $draftDoc.Repaginate()
    $draftDoc.Fields.Update() | Out-Null
    $draftDoc.ExportAsFixedFormat($outputPdf, 17)
    $fieldValues = @{}
    foreach ($field in $draftDoc.Fields) {
        if ($field.Code.Text -match 'PAGEREF (ThesisAnchor\d+)') {
            $fieldValues[$Matches[1]] = $field.Result.Text.Trim()
        }
    }
    $fieldValues | ConvertTo-Json | Set-Content -LiteralPath $cacheFile -Encoding utf8
    $draftDoc.Close(0)
    Write-Output "Exported $outputPdf"
} finally {
    $wordApp.Quit()
}
