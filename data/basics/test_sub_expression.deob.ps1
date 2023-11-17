$a = @(0, 1, 2);
$foo = $(   
   for($i = 0;$i -lt $a.Length;$i++)
   {
      $a[$i] + 1;
   }
   4;
);
Write-Host $foo;
