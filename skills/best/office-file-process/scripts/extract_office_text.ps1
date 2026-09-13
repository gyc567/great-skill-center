# extract_office_text.ps1
# Extract text from Word/Excel/PowerPoint files via Office COM object model.
# Designed for PowerShell 5.1 on Windows. Script is pure ASCII on purpose:
# PS 5.1 reads BOM-less .ps1 as ANSI/GBK, so any non-ASCII char in the script
# body would corrupt paths and string literals.
#
# Usage (NO other flags needed):
#   powershell -NoProfile -ExecutionPolicy Bypass -File extract_office_text.ps1 -PathPattern "D:\some\dir\*.doc"
#
# Behavior (all defaults, nothing to remember):
#   - Output ALWAYS goes NEXT TO THE SOURCE FILE as office_extract_<n>.txt
#     (ASCII file name so Read/Grep can open it, even though the parent dir may
#     be CJK; the original document stays where it is, the extract sits beside it)
#   - Stale office_extract_*.txt from previous runs in that directory are
#     removed first, so the directory only holds the current run's results.
#   - A manifest at the end maps each source file to its output file.
#   - Word table cells are converted to tab-separated text (readable tables).
#   - Headless Office processes left behind by failed runs are killed at exit.
#
# Optional:
#   -OutDir <path>   write all outputs to a different directory instead
#
# Notes:
# - Files are opened READ-ONLY; nothing is modified.
# - Output is UTF-8 with BOM.
# - Requires Office installed (Word/Excel/PowerPoint COM automation).
#   For .docx/.xlsx/.pptx on machines WITHOUT Office, unzip the file and parse
#   the XML directly instead (see SKILL.md).

param(
    [Parameter(Mandatory = $true)][string]$PathPattern,
    [string]$OutDir = ''
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$utf8bom = New-Object System.Text.UTF8Encoding($true)

function Resolve-TargetDir {
    # Accept a concrete directory, a single file, or a wildcard path. Return the
    # fully resolved directory plus a file filter. NOTE: Get-ChildItem silently
    # returns nothing when a PARENT component of -Path contains a wildcard and
    # -Filter is used together, so wildcard parents must be resolved via
    # Get-Item first.
    if (Test-Path $PathPattern -PathType Container) {
        return @{ Dir = (Resolve-Path $PathPattern).Path; Filter = '*' }
    }
    $dirPart = Split-Path -Parent $PathPattern
    if ([string]::IsNullOrEmpty($dirPart)) { $dirPart = '.' }
    $leaf = Split-Path -Leaf $PathPattern
    # resolve wildcard characters in parent components (e.g. CJK directory
    # names the caller cannot type, replaced with '*')
    if ($dirPart -match '[*?]') {
        $resolved = @(Get-Item -Path $dirPart -ErrorAction SilentlyContinue)
        if ($resolved.Count -ge 1) { $dirPart = $resolved[0].FullName }
    }
    return @{ Dir = $dirPart; Filter = $leaf }
}

function Save-Text {
    param([string]$OutPath, [string]$Text)
    [System.IO.File]::WriteAllText($OutPath, $Text, $utf8bom)
}

function Normalize-WordText {
    # Word's Content.Text marks end-of-table-cell as "`r`a" (CR + BEL) and
    # end-of-row as "`r`a`r`a". Convert to tab-separated rows so protocol
    # tables (cmd/param definitions) stay readable as plain text.
    param([string]$Text)
    $t = $Text -replace "`r`a`r`a", "`n"
    $t = $t -replace "`r`a", "`t"
    $t = $t -replace "[`a`v]", "`n"
    $t = $t -replace "`r", "`n"
    return $t
}

function Extract-Word {
    param($Word, [string]$FilePath, [string]$OutPath)
    $doc = $Word.Documents.Open($FilePath, $false, $true)   # ConfirmConversions, ReadOnly
    try {
        $text = Normalize-WordText -Text $doc.Content.Text
        Save-Text -OutPath $OutPath -Text $text
        return $text.Length
    } finally {
        $doc.Close(0)   # wdDoNotSaveChanges
    }
}

function Format-Cell {
    param($Cell)
    if ($null -eq $Cell) { return '' }
    if ($Cell -is [datetime]) { return $Cell.ToString('yyyy-MM-dd HH:mm:ss') }
    return "$Cell"
}

function Extract-Excel {
    param($Excel, [string]$FilePath, [string]$OutPath)
    $wb = $Excel.Workbooks.Open($FilePath, 0, $true)   # UpdateLinks=0, ReadOnly
    try {
        $sb = New-Object System.Text.StringBuilder
        foreach ($ws in $wb.Worksheets) {
            [void]$sb.AppendLine('===== SHEET: ' + $ws.Name + ' =====')
            $used = $ws.UsedRange
            $arr = $used.Value2
            if ($null -eq $arr) {
                # empty sheet
            } elseif ($arr -is [object[,]]) {
                $rows = $arr.GetLength(0); $cols = $arr.GetLength(1)
                for ($r = 0; $r -lt $rows; $r++) {
                    $line = New-Object System.Collections.Generic.List[string]
                    for ($c = 0; $c -lt $cols; $c++) { $line.Add((Format-Cell $arr[$r, $c])) }
                    [void]$sb.AppendLine(($line -join "`t"))
                }
            } else {
                [void]$sb.AppendLine((Format-Cell $arr))
            }
            [void]$sb.AppendLine()
        }
        $text = $sb.ToString()
        Save-Text -OutPath $OutPath -Text $text
        return $text.Length
    } finally {
        $wb.Close($false)
    }
}

function Get-ShapeText {
    param($Shape, [System.Text.StringBuilder]$Sb, [string]$Prefix)
    if ($Shape.HasTextFrame -eq -1 -and $Shape.TextFrame2.HasText -eq -1) {
        $t = $Shape.TextFrame2.TextRange.Text
        if ($t -and $t.Trim().Length -gt 0) {
            [void]$Sb.AppendLine($Prefix + $t)
        }
    }
}

function Extract-PowerPoint {
    param($PptApp, [string]$FilePath, [string]$OutPath)
    # Open(FileName, ReadOnly, Untitled, WithWindow)
    $pres = $PptApp.Presentations.Open($FilePath, $true, $false, $false)
    try {
        $sb = New-Object System.Text.StringBuilder
        $i = 0
        foreach ($slide in $pres.Slides) {
            $i++
            [void]$sb.AppendLine('===== SLIDE ' + $i + ' =====')
            foreach ($shape in $slide.Shapes) {
                Get-ShapeText -Shape $shape -Sb $sb -Prefix ''
            }
            if ($slide.HasNotesPage -eq -1) {
                $notes = New-Object System.Text.StringBuilder
                foreach ($shape in $slide.NotesPage.Shapes) {
                    Get-ShapeText -Shape $shape -Sb $notes -Prefix ''
                }
                $nt = $notes.ToString().Trim()
                if ($nt.Length -gt 0) { [void]$sb.AppendLine('[NOTES] ' + $nt) }
            }
            [void]$sb.AppendLine()
        }
        $text = $sb.ToString()
        Save-Text -OutPath $OutPath -Text $text
        return $text.Length
    } finally {
        $pres.Close()
    }
}

function Quit-App {
    param($App)
    if ($null -ne $App) {
        try { $App.Quit() } catch { }
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($App)
    }
}

function Remove-HeadlessOffice {
    # Kill only Office processes WITHOUT a main window (i.e. invisible
    # automation instances orphaned by crashed runs). The user's own visible
    # Word/Excel windows have a non-zero MainWindowHandle and are never touched.
    Get-Process -Name WINWORD, EXCEL, POWERPNT -ErrorAction SilentlyContinue |
        Where-Object { $_.MainWindowHandle -eq 0 } |
        Stop-Process -Force -ErrorAction SilentlyContinue
}

# ---- main ----
$t = Resolve-TargetDir
$files = @(Get-ChildItem -Path $t.Dir -Filter $t.Filter -File | Where-Object {
    $_.Extension -match '^\.(docx?|xlsx?|pptx?|rtf)$'
})
if ($files.Count -eq 0) {
    Write-Output ('NO FILES matched: ' + $PathPattern)
    exit 1
}
Write-Output ('matched ' + $files.Count + ' file(s)')

# resolve output mode: default is next to each source file, named
# office_extract_<n>.txt (ASCII name so Read/Grep always work even under a CJK
# parent directory). Stale outputs from previous runs in that directory are
# cleared first. -OutDir redirects everything to one directory instead.
$useOutDir = (-not [string]::IsNullOrEmpty($OutDir))
if ($useOutDir) {
    if (-not (Test-Path -PathType Container $OutDir)) {
        New-Item -ItemType Directory -Path $OutDir | Out-Null
    }
    Get-ChildItem -Path $OutDir -Filter 'office_extract_*.txt' -File -ErrorAction SilentlyContinue |
        Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Output ('output dir: ' + $OutDir)
} else {
    Get-ChildItem -Path $t.Dir -Filter 'office_extract_*.txt' -File -ErrorAction SilentlyContinue |
        Remove-Item -Force -ErrorAction SilentlyContinue
}

$word = $null; $excel = $null; $ppt = $null
$n = 0
$manifest = New-Object System.Text.StringBuilder
try {
    foreach ($f in $files) {
        $n++
        $ext = $f.Extension.ToLower()
        if ($useOutDir) {
            $outPath = Join-Path $OutDir ('office_extract_' + $n + '.txt')
        } else {
            $outPath = Join-Path $f.DirectoryName ('office_extract_' + $n + '.txt')
        }
        try {
            if ($ext -match '^\.(doc|docx|rtf)$') {
                if ($null -eq $word) { $word = New-Object -ComObject Word.Application; $word.Visible = $false; $word.DisplayAlerts = 0 }
                $len = Extract-Word -Word $word -FilePath $f.FullName -OutPath $outPath
            } elseif ($ext -match '^\.(xls|xlsx)$') {
                if ($null -eq $excel) { $excel = New-Object -ComObject Excel.Application; $excel.Visible = $false; $excel.DisplayAlerts = $false }
                $len = Extract-Excel -Excel $excel -FilePath $f.FullName -OutPath $outPath
            } else {
                if ($null -eq $ppt) { $ppt = New-Object -ComObject PowerPoint.Application }
                $len = Extract-PowerPoint -PptApp $ppt -FilePath $f.FullName -OutPath $outPath
            }
            Write-Output ('  OK  ' + $f.Name + ' -> ' + $outPath + ' (' + $len + ' chars)')
            [void]$manifest.AppendLine('  ' + $n.ToString() + '. ' + $f.Name + '  ->  ' + $outPath)
        } catch {
            Write-Output ('  FAIL ' + $f.Name + ' :: ' + $_.Exception.Message)
            [void]$manifest.AppendLine('  ' + $n.ToString() + '. ' + $f.Name + '  ->  FAILED: ' + $_.Exception.Message)
        }
    }
} finally {
    Quit-App $word; Quit-App $excel; Quit-App $ppt
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
    Remove-HeadlessOffice
}
Write-Output 'DONE. manifest:'
Write-Output $manifest.ToString()
