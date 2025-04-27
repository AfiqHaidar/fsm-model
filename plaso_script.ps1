# Plaso Analysis Script

# Usage:

# Generate plaso file in directory "plaso_analysis_1"
# .\plaso_script.ps1 -plaso -n 1
# & "C:\Users\afiqh\OneDrive\Documents\TA\ta-code\plaso_script.ps1" -plaso -n 1

# Generate full timeline CSV in directory "plaso_analysis_1"
# .\plaso_script.ps1 -csv -n 1 -a
# & "C:\Users\afiqh\OneDrive\Documents\TA\ta-code\plaso_script.ps1" -csv -n 1 -a

# Generate filtered timeline in directory "plaso_analysis_1"
# .\plaso_script.ps1 -csv -n 1 -t -ts "2023-01-01 00:00:00" -te "2024-12-31 23:59:59"  
#& "C:\Users\afiqh\OneDrive\Documents\TA\ta-code\plaso_script.ps1" -csv -n 1 -t -ts "2023-01-01 00:00:00" -te "2024-12-31 23:59:59"

param(
    [Parameter(Mandatory=$false)]
    [switch]$plaso,
    
    [Parameter(Mandatory=$false)]
    [switch]$csv,
    
    [Parameter(Mandatory=$false)]
    [int]$n = 1,
    
    [Parameter(Mandatory=$false)]
    [switch]$a,
    
    [Parameter(Mandatory=$false)]
    [switch]$t,
    
    [Parameter(Mandatory=$false)]
    [string]$ts = "2023-01-01 00:00:00",
    
    [Parameter(Mandatory=$false)]
    [string]$te = "2026-12-31 23:59:59",
    
    [Parameter(Mandatory=$false)]
    [string]$VmDiskPath = "C:\Users\afiqh\VirtualBox VMs\Ubuntu\Ubuntu.vdi",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputBaseDir = "C:\Users\afiqh\OneDrive\Documents\TA\ta-data"
)

# Validate parameters
if (-not ($plaso -or $csv)) {
    Write-Host "Error: You must specify either -plaso or -csv" -ForegroundColor Red
    exit 1
}

if ($csv -and -not ($a -or $t)) {
    Write-Host "Error: When using -csv, you must specify either -a (all time) or -t (time filter)" -ForegroundColor Red
    exit 1
}

# Create the directory path
$outputDir = Join-Path $OutputBaseDir "plaso_analysis_$n"

# Create directory if it doesn't exist 
if (-not (Test-Path $outputDir)) {
    Write-Host "Creating output directory: $outputDir"
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# Get VM disk filename
$vmDiskName = Split-Path $VmDiskPath -Leaf
$vmDiskDir = Split-Path $VmDiskPath -Parent

# Process based on command
if ($plaso) {
    # Step 1: Generate timeline.plaso file
    Write-Host "Generating timeline.plaso from $vmDiskName in directory $outputDir..." -ForegroundColor Green
    
    # Fixed command using proper escaping for PowerShell
    $dockerCmd = "docker run -v `"${vmDiskDir}:/input`" -v `"${outputDir}:/output`" --rm log2timeline/plaso log2timeline --partitions all --storage-file /output/timeline.plaso /input/$vmDiskName"
    
    Write-Host "Running: $dockerCmd" -ForegroundColor Cyan
    Invoke-Expression $dockerCmd
    
    Write-Host "Plaso file generation complete! Results saved to: $outputDir\timeline.plaso" -ForegroundColor Green
}

if ($csv) {
    # Check if timeline.plaso exists in the directory
    $plasoFile = Join-Path $outputDir "timeline.plaso"
    if (-not (Test-Path $plasoFile)) {
        Write-Host "Error: timeline.plaso not found in $outputDir" -ForegroundColor Red
        Write-Host "Please run with -plaso flag first to generate the plaso file" -ForegroundColor Yellow
        exit 1
    }
    
    # Format current timestamp for filenames
    $currentTimestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    
    if ($a) {
        # Generate full timeline CSV with timestamp
        $csvFilename = "timeline_all_${currentTimestamp}.csv"
        Write-Host "Generating full timeline CSV in directory $outputDir..." -ForegroundColor Green
        
        # Fixed command using proper escaping for PowerShell
        $dockerCmd = "docker run -v `"${outputDir}:/data`" --rm log2timeline/plaso psort -w /data/$csvFilename /data/timeline.plaso"
        
        Write-Host "Running: $dockerCmd" -ForegroundColor Cyan
        Invoke-Expression $dockerCmd
        
        Write-Host "Full timeline CSV generation complete! Results saved to: $outputDir\$csvFilename" -ForegroundColor Green
    }
    
    if ($t) {
        # Validate and format date inputs
        try {
            # Attempt to parse the start time
            $startDateTime = [datetime]::ParseExact($ts, "yyyy-MM-dd HH:mm:ss", [System.Globalization.CultureInfo]::InvariantCulture)
            $formattedStartTime = $startDateTime.ToString("yyyy-MM-dd HH:mm:ss")
            
            # Attempt to parse the end time
            $endDateTime = [datetime]::ParseExact($te, "yyyy-MM-dd HH:mm:ss", [System.Globalization.CultureInfo]::InvariantCulture)
            $formattedEndTime = $endDateTime.ToString("yyyy-MM-dd HH:mm:ss")
        }
        catch {
            Write-Host "Error: Invalid date format. Please use the format 'yyyy-MM-dd HH:mm:ss'" -ForegroundColor Red
            Write-Host "Example: 2025-01-01 00:00:00" -ForegroundColor Yellow
            exit 1
        }
        
        # Format date range for filename - replace colons and spaces with underscores
        $startTimeFormatted = $formattedStartTime.Replace(":", "-").Replace(" ", "_")
        $endTimeFormatted = $formattedEndTime.Replace(":", "-").Replace(" ", "_")
        
        # Generate filtered timeline CSV with descriptive filename
        $csvFilename = "timeline_filtered_${currentTimestamp}_from_${startTimeFormatted}_to_${endTimeFormatted}.csv"
        
        Write-Host "Generating filtered timeline CSV from $formattedStartTime to $formattedEndTime in directory $outputDir..." -ForegroundColor Green
        
        # Fixed command using proper escaping for PowerShell
        $dockerCmd = "docker run -v `"${outputDir}:/data`" --rm log2timeline/plaso psort -q /data/timeline.plaso `"date < '$formattedEndTime' and date > '$formattedStartTime'`" -w /data/$csvFilename"
        
        Write-Host "Running: $dockerCmd" -ForegroundColor Cyan
        Invoke-Expression $dockerCmd
        
        Write-Host "Filtered timeline CSV generation complete! Results saved to: $outputDir\$csvFilename" -ForegroundColor Green
    }
}