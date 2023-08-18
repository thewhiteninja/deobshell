$adComputers = Get-ADComputer -Filter * -Properties OperatingSystem;
$operatingSystems = $adComputers.OperatingSystem | Sort-Object -Unique;

foreach($operatingSystem in $operatingSystems)
{
   $computers = ($adComputers | Where-Object    {
      {
         $_.OperatingSystem;
      }
   }
).Name;
   Write-Host ([String]$computers.Count + ' running ' + '.');
}
