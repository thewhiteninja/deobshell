$i = 2;
while ($i -gt 0) {
  # Must not remove usage of $unassgn
  $unassgn = $unassn + 4;
  $i--;
}
Write-Host $unassgn

$j = 2;
$yessub = 5;
while ($j -gt 0)
{
  # Must not substitute $j+1 with 3
  Write-Host ($j+1);
  Write-Host ($yessub+0);
  $j--;
}

# Must replace $nothere with 0 instead of stripping the operation
$foo = $nothere - 5
Write-Host $foo

# Completely gone
if (5 -gt 6) {
    Write-Host
}

if (5 -gt 6) {
    Write-Host
} elseif (6 -gt 7) {
    Write-Host
} else {
    # This clause is lifted
    Write-Host "hi"
}
