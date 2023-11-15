
# [0] assignment, [1] update (PipelineAst), [2] block, [3] cond (PipelineAst)
for ($i = 0; $i -lt 3; $i--) {
  Write-Host $i
}
# [0] assignment, [1] update (PipelineAst), [2] block
for ($i = 0; ; $i++) {
  Write-Host $i
  break
}
# [0] assignment, [1] block, [2] cond (PipelineAst)
for ($i = 0; $i -lt 3;) {
  Write-Host $i++
}
# [0] block
for (; ;) {
  break
}