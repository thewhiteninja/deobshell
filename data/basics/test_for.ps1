
# [0] assignment, [1] update (PipelineAst), [2] block, [3] cond (PipelineAst)
for ($i = 0; $i -lt 3; $i--) {
  Write-Host $i
}
# [0] assignment, [1] update (PipelineAst), [2] block
for ($i = 0; ; $i++) {
  Write-Host $i
  if ($i -eq 4) {
    break
  }
}
# [0] assignment, [1] block, [2] cond (PipelineAst)
for ($i = 0; $i -lt 3;) {
  Write-Host ($i++)
}
# [0] update, [1] block, [2] cond
for (; $i -lt 4; $i++) {
  Write-Host $i
}
# [0] block
for (; ;) {
  if ($i -eq 3) {
    break
  }
}

# Dead
for ($x = 0; $x -gt 4; $x--) {
  Write-Host $x
}

# Dead, but loop var has usage
for ($y = 4; $y -lt 3; $y--) {
  Write-Host $y+1
}
Write-Host $y

# Lift Write-Host to top
for ($z = Get-Command Get-Process;;) {
  Write-Host $z.CommandType
  break
}
