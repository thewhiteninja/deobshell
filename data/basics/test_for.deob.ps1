
for ($i = 0; $i -lt 3; $i--)
{
   Write-Host $i;
}

for ($i = 0; ; $i++)
{
   Write-Host $i;
   if ($i -eq 4)
   {
      break;
   }
}

for ($i = 0; $i -lt 3; )
{
   Write-Host ($i++);
}

for (; $i -lt 4; $i++)
{
   Write-Host $i;
}

for (; ; )
{
   if ($i -eq 3)
   {
      break;
   }
}
$y = 4;
Write-Host $y;
$z = Get-Command Get-Process;
Write-Host $z.CommandType;
