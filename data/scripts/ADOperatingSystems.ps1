# List operating systems in AD and how many machines are running each one.
#

# Get all AD computers and include the OperatingSystem property
$adComputers = Get-ADComputer -Filter * -Properties OperatingSystem

# Gather up all unique OperatingSystems from the AD computers into one list
$operatingSystems = $adComputers.OperatingSystem | Sort-Object -Unique

# Output to screen each operating system and how many AD computers are running it
foreach ($operatingSystem in $operatingSystems) {
    $computers = ($adComputers | Where-Object {$_.OperatingSystem -eq $operatingSystem}).Name
    Write-Host ([string]$computers.Count + ' running ' + $operatingSystem + '.')
}
