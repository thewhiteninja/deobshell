$i = 4
$i += 2
$j = 5
$j *= 2
$k = 6
$k -= 2
$m = (16 / 2) % 9
$m %= 7
$s = (1 -shl 8) -bor 1
Write-Host $i $j $k $m $s

if ($i -lt 4) {
    $z = 1
} elseif ($j -lt 5) {
    $z = 2
} else {
    $z = 3
}
Write-Host $z

$foo = $notthere - 5
Write-Host $foo
