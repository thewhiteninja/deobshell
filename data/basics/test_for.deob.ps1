
for ($i = 0; $i -lt 3; $i--)
{
   Write-Host $i;
}

for ($i = 0; ; $i++)
{
   Write-Host $i;
   break;
}

for ($i = 0; $i -lt 3; )
{
   Write-Host $i++;
}

for (; ; )
{
   break;
}
