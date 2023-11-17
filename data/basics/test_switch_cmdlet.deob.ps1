$variable = "Option2";
switch -Wildcard ($variable) {
   "Option1" {
      Write-Output "Selected Option 1";
   }
   "Option*" {
      Write-Output "Selected Option with wildcard match";
   }
   "AnotherOption" {
      Write-Output "Selected AnotherOption";
   }
   default {
      Write-Output "Default Option";
   }
}
