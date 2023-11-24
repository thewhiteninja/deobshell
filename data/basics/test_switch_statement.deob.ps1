$variable = "Option2";
switch ($variable) {
   "Option1" {
      Write-Output "Selected Option 1";
   }
   "Option2" {
      Write-Output "Selected Option 2";
   }
   "Option3" {
      Write-Output "Selected Option 3";
   }
   default {
      Write-Output "Default Option";
   }
}
Write-Output "Default Option";
