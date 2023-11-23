function Invoke-WinEnum{
   [CmdletBinding]
   param
   (
      [Parameter](Mandatory=$False, Position=0)
      $UserName, 
      [Parameter](Mandatory=$False, Position=1)
      $keywords
   )
   function Get-UserInfo   {
      if ($UserName)
      {
         "UserName: $UserName`n";
         $DomainUser = $UserName;
      }
      else
      {
         $DomainUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name;
         $UserName = $DomainUser.Split('\')[-1];
         "UserName: $UserName`n";
      }

      "`n-------------------------------------`n";
      "AD Group Memberships";
      "`n-------------------------------------`n";
      Add-Type -AssemblyName System.DirectoryServices.AccountManagement;
      $dsclass = "System.DirectoryServices.AccountManagement";
      $dsclassUP = "$dsclass.userprincipal" -as [Type];
      $Domain = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain();
      $contextTypeDomain = New-Object System.DirectoryServices.AccountManagement.PrincipalContext @([System.DirectoryServices.AccountManagement.ContextType]::Domain, $Domain.Name);
      $usr = $dsclassUP::FindByIdentity($contextTypeDomain, "SamAccountName", $DomainUser);
      $usr.GetGroups() | ForEach-Object       {
         {
            $_.Name;
         }
      }
      "`n-------------------------------------`n";
      "Password Last changed";
      "`n-------------------------------------`n";
      $(         $usr.LastPasswordSet;
      ) + "`n";
      "`n-------------------------------------`n";
      "Last 5 files opened";
      "`n-------------------------------------`n";
      $AllOpenedFiles = Get-ChildItem -Path "C:\" -Recurse -Include @("*.txt", "*.pdf", "*.docx", "*.doc", "*.xls", "*.ppt") -ea SilentlyContinue | Sort-Object       {
         {
            $_.LastAccessTime;
         }
      }
;
      $LastOpenedFiles = @();
      $AllOpenedFiles | ForEach-Object       {
         {
            $owner = $(               $_.GetAccessControl();
            ).Owner;
            $owner = $owner.Split('\')[-1];
            if ($owner -eq $UserName)
            {
               $LastOpenedFiles += $_;
            }
         }
      }
      if ($LastOpenedFiles)
      {
         $LastOpenedFiles | Sort-Object LastAccessTime -Descending | Select-Object @(FullName, LastAccessTime) -First 5 | Format-List | Out-String;
      }
      "`n-------------------------------------`n";
      "Interesting Files";
      "`n-------------------------------------`n";
      $NewestInterestingFiles = @();
      if ($keywords)
      {
         $AllInterestingFiles = Get-ChildItem -Path "C:\" -Recurse -Include $keywords -ea SilentlyContinue | Where-Object          {
            {
               $_.Mode.StartsWith('d') -eq $False;
            }
         }
 | Sort-Object          {
            {
               $_.LastAccessTime;
            }
         }
;
         $AllInterestingFiles | ForEach-Object          {
            {
               $owner = $_.GetAccessControl().Owner;
               $owner = $owner.Split('\')[-1];
               if ($owner -eq $UserName)
               {
                  $NewestInterestingFiles += $_;
               }
            }
         }
         if ($NewestInterestingFiles)
         {
            $NewestInterestingFiles | Sort-Object LastAccessTime -Descending | Select-Object @(FullName, LastAccessTime) | Format-List | Out-String;
         }
      }
      else
      {
         $AllInterestingFiles = Get-ChildItem -Path "C:\" -Recurse -Include @("*.txt", "*.pdf", "*.docx", "*.doc", "*.xls", "*.ppt", "*pass*", "*cred*") -ErrorAction SilentlyContinue | Where-Object          {
            {
               $_.Mode.StartsWith('d') -eq $False;
            }
         }
 | Sort-Object          {
            {
               $_.LastAccessTime;
            }
         }
;
         $AllInterestingFiles | ForEach-Object          {
            {
               $owner = $_.GetAccessControl().Owner;
               $owner = $owner.Split('\')[-1];
               if ($owner -eq $UserName)
               {
                  $NewestInterestingFiles += $_;
               }
            }
         }
         if ($NewestInterestingFiles)
         {
            $NewestInterestingFiles | Sort-Object LastAccessTime -Descending | Select-Object @(FullName, LastAccessTime) | Format-List | Out-String;
         }
      }

      "`n-------------------------------------`n";
      "Clipboard Contents";
      "`n-------------------------------------`n";
      $cmd =       {
         {
            Add-Type -Assembly PresentationCore;
            [Windows.Clipboard]::GetText() -replace @("`n", '') -split "`n";
         }
      }
;
      if ([threading.thread]::CurrentThread.GetApartmentState() -eq 'MTA')
      {
         Powershell -Sta -Command $cmd;
      }
      else
      {
         $cmd;
      }

      "`n";
   }
;
   function Get-SysInfo   {
      "`n-------------------------------------`n";
      "System Information";
      "`n-------------------------------------`n";
      $OSVersion = (Get-WmiObject -class Win32_OperatingSystem).Caption;
      $OSArch = (Get-WmiObject -class win32_operatingsystem).OSArchitecture;
      "OS: $OSVersion $OSArch`n";
      if ($OSArch -eq '64-bit')
      {
         $registeredAppsx64 = Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName | Sort-Object DisplayName;
         $registeredAppsx86 = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName | Sort-Object DisplayName;
         $registeredAppsx64 | Where-Object          {
            {
               $_.DisplayName -ne ' ';
            }
         }
 | Select-Object DisplayName | Format-Table -AutoSize | Out-String;
         $registeredAppsx86 | Where-Object          {
            {
               $_.DisplayName -ne ' ';
            }
         }
 | Select-Object DisplayName | Format-Table -AutoSize | Out-String;
      }
      else
      {
         $registeredAppsx86 = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName | Sort-Object DisplayName;
         $registeredAppsx86 | Where-Object          {
            {
               $_.DisplayName -ne ' ';
            }
         }
 | Select-Object DisplayName | Format-Table -AutoSize | Out-String;
      }

      "`n-------------------------------------`n";
      "Services";
      "`n-------------------------------------`n";
      $AllServices = @();
      Get-WmiObject -class win32_service | ForEach-Object       {
         {
            $service = New-Object PSObject -Property @{ ServiceName = $_.DisplayName = ServiceStatus = (Get-service | where-Object             {
               {
                  $_.DisplayName -eq $ServiceName;
               }
            }
).status = ServicePathtoExe = $_.PathName = StartupType = $_.StartMode };
            $AllServices += $service;
         }
      }
      $AllServices | Select-Object @(ServicePathtoExe, ServiceName) | Format-Table -AutoSize | Out-String;
      "`n-------------------------------------`n";
      "Available Shares";
      "`n-------------------------------------`n";
      Get-WmiObject -class win32_share | Format-Table -AutoSize @(Name, Path, Description, Status) | Out-String;
      "`n-------------------------------------`n";
      "AV Solution";
      "`n-------------------------------------`n";
      $AV = Get-WmiObject -namespace root\SecurityCenter2 -class Antivirusproduct;
      if ($AV)
      {
         $AV.DisplayName + "`n";
         $AVstate = $AV.productState;
         $statuscode = "{0:x6}" -f $AVstate;
         $wscscanner = $statuscode[@(2, 3)];
         $wscuptodate = $statuscode[@(4, 5)];
         $statuscode = $statuscode -join '';
         "AV Product State: " + $AV.productState + "`n";
         if ($wscscanner -ge '10')
         {
            "Enabled: Yes`n";
         }
         elseif ($wscscanner -eq '00' -or $wscscanner -eq '01')
         {
            "Enabled: No`n";
         }
         else
         {
            "Enabled: Unknown`n";
         }

         if ($wscuptodate -eq '00')
         {
            "Updated: Yes`n";
         }
         elseif ($wscuptodate -eq '10')
         {
            "Updated: No`n";
         }
         else
         {
            "Updated: Unknown`n";
         }

      }
      "`n-------------------------------------`n";
      "Windows Last Updated";
      "`n-------------------------------------`n";
      $Lastupdate = Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object InstalledOn -First 1;
      if ($Lastupdate)
      {
         $Lastupdate.InstalledOn | Out-String;
         "`n";
      }
      else
      {
         "Unknown`n";
      }

   }
;
   function Get-NetInfo   {
      "`n-------------------------------------`n";
      "Network Adapters";
      "`n-------------------------------------`n";
      
      foreach($Adapter in (Get-WmiObject -class win32_networkadapter -Filter "NetConnectionStatus=''2''"))
      {
         $config = Get-WmiObject -class win32_networkadapterconfiguration -Filter "Index = ''$($Adapter.Index)''";
         "`n";
         "Adapter: " + $Adapter.Name + "`n";
         "`n";
         "IP Address: ";
         if ($config.IPAddress -is [System.array])
         {
            $config.IPAddress[0] + "`n";
         }
         else
         {
            $config.IPAddress + "`n";
         }

         "`n";
         "Mac Address: " + $Config.MacAddress;
         "`n";
      }
      "`n-------------------------------------`n";
      "Netstat Established connections and processes";
      "`n-------------------------------------`n";
      $properties = @('Protocol', 'LocalAddress', 'LocalPort');
      $properties += @('RemoteAddress', 'RemotePort', 'State', 'ProcessName', 'PID');
      netstat -ano | Select-String -Pattern '\s+(TCP|UDP)' | ForEach-Object       {
         {
            $item = $_.line.Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries);
            if ($item[1] -notmatch '^\[::')
            {
               if ($la = $item[1] -as [ipaddress].AddressFamily -eq 'InterNetworkV6')
               {
                  $localAddress = $la.IPAddressToString;
                  $localPort = $item[1].Split('\]:')[-1];
               }
               else
               {
                  $localAddress = $item[1].Split(':')[0];
                  $localPort = $item[1].Split(':')[-1];
               }

               if ($ra = $item[2] -as [ipaddress].AddressFamily -eq 'InterNetworkV6')
               {
                  $remoteAddress = $ra.IPAddressToString;
                  $remotePort = $item[2].Split('\]:')[-1];
               }
               else
               {
                  $remoteAddress = $item[2].Split(':')[0];
                  $remotePort = $item[2].Split(':')[-1];
               }

               $netstat = New-Object PSObject -Property @{ PID = $item[-1] = ProcessName = (Get-Process -Id $item[-1] -ErrorAction SilentlyContinue).Name = Protocol = $item[0] = LocalAddress = $localAddress = LocalPort = $localPort = RemoteAddress = $remoteAddress = RemotePort = $remotePort = State = if ($item[0] -eq 'tcp')
               {
                  $item[3];
               }
               else
               {
                  $null;
               }

 };
               if ($netstat.State -eq 'ESTABLISHED')
               {
                  $netstat | Format-List @(ProcessName, LocalAddress, LocalPort, RemoteAddress, RemotePort, State) | Out-String | %                   {
                     {
                        $_.Trim();
                     }
                  }
                  "`n`n";
               }
            }
         }
      }
      "`n-------------------------------------`n";
      "Mapped Network Drives";
      "`n-------------------------------------`n";
      Get-WmiObject -class win32_logicaldisk | where-Object       {
         {
            $_.DeviceType -eq 4;
         }
      }
 | ForEach-Object       {
         {
            $NetPath = $_.ProviderName;
            $DriveLetter = $_.DeviceID;
            $DriveName = $_.VolumeName;
            $NetworkDrive = New-Object PSObject -Property @{ Path = $NetPath = Drive = $DriveLetter = Name = $DriveName };
            $NetworkDrive;
         }
      }
      "`n-------------------------------------`n";
      "Firewall Rules";
      "`n-------------------------------------`n";
      $fw = New-Object -ComObject HNetCfg.FwPolicy2;
      $fwprofiletypes = @{ 1073741824 = "All" = 1 = "Domain" = 2 = "Private" = 4 = "Public" };
      $fwaction = @{ 1 = "Allow" = 0 = "Block" };
      $FwProtocols = @{ 1 = "ICMPv4" = 2 = "IGMP" = 6 = "TCP" = 17 = "UDP" = 41 = "IPV6" = 43 = "IPv6Route" = 44 = "IPv6Frag" = 47 = "GRE" = 58 = "ICMPv6" = 59 = "IPv6NoNxt" = 60 = "IPv60pts" = 112 = "VRRP" = 113 = "PGM" = 115 = "L2TP" };
      $fwdirection = @{ 1 = "Inbound" = 2 = "Outbound" };
      $fwprofiletype = $fwprofiletypes.Get_Item($fw.CurrentProfileTypes);
      $fwrules = $fw.rules;
      "Current Firewall Profile Type in use: $fwprofiletype";
      $AllFWRules = @();
      $fwrules | ForEach-Object       {
         {
            $FirewallRule = New-Object PSObject -Property @{ ApplicationName = $_.Name = Protocol = $fwProtocols.Get_Item($_.Protocol) = Direction = $fwdirection.Get_Item($_.Direction) = Action = $fwaction.Get_Item($_.Action) = LocalIP = $_.LocalAddresses = LocalPort = $_.LocalPorts = RemoteIP = $_.RemoteAddresses = RemotePort = $_.RemotePorts };
            $AllFWRules += $FirewallRule;
         }
      }
      $AllFWRules | Select-Object @(Action, Direction, RemoteIP, RemotePort, LocalPort, ApplicationName) | Format-List | Out-String;
   }
;
   Get-UserInfo;
   Get-SysInfo;
   Get-NetInfo;
}
;
