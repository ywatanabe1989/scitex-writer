# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
param(
    [string]$inputFilePath,
    [string]$outputFilePath
)

try {
    $powerpoint = New-Object -ComObject PowerPoint.Application
    if (-not $powerpoint) {
        throw "Failed to start PowerPoint. Make sure it is installed on this system."
    }

    $powerpoint.Presentations | ForEach-Object { $_.Close() }

    $presentation = $powerpoint.Presentations.Open($inputFilePath, [Microsoft.Office.Core.MsoTriState]::msoFalse)

    $presentation.Slides[1].Export($outputFilePath, "TIF")

    $presentation.Close()
    $powerpoint.Quit()

} catch {
    $ErrorMessage = "An error occurred: $_"
    Write-Error $ErrorMessage
} finally {
    if ($presentation) {
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($presentation) | Out-Null
    }
    if ($powerpoint) {
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($powerpoint) | Out-Null
    }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}