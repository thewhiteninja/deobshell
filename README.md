# DeobShell

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.MIT)
[![Language: Python](https://img.shields.io/badge/Language-Python-brightgreen.svg?tyle=flat-square)](#)
[![Cross-platform](https://img.shields.io/badge/Platform-All-0078d7.svg)](#)
[![v1.0](https://img.shields.io/badge/Version-1.0-ff5733.svg)](#)

<br />

DeobShell is PoC to deobfuscate Powershell using Abstract Syntax Tree (AST) manipulation in Python.
The AST is extracted using a Powershell script by calling `System.Management.Automation.Language.Parser` and
writing relevant nodes to an XML file.

AST manipulation and optimization is based on a set of rules (ex: concat constant string, apply format operator ...).

From the deobfuscated AST, a ps1 script is rebuilt using Python.
See the diagram below.

*It's a PoC ... only a subset of Powershell is supported*

## How

<p align="center">
  <img alt="diagram" src="assets/diagram.png" width="600">
</p>

### Example of rules

- Format

#### In
```xml
<BinaryExpressionAst Operator="Format" StaticType="System.Object">
    <StringConstantExpressionAst StringConstantType="DoubleQuoted" StaticType="string">{0}{1}</StringConstantExpressionAst>
        <ArrayLiteralAst StaticType="System.Object[]">
          <Elements>
            <StringConstantExpressionAst StringConstantType="SingleQuoted" StaticType="string">c</StringConstantExpressionAst>
            <StringConstantExpressionAst StringConstantType="SingleQuoted" StaticType="string">AcA</StringConstantExpressionAst>
          </Elements>
  </ArrayLiteralAst>
</BinaryExpressionAst>
```
#### Out
```xml
<StringConstantExpressionAst StringConstantType="SingleQuoted" StaticType="string">cAcA</StringConstantExpressionAst>
```

### Examples of script

- a CTF chall

#### In

```powershell
$mRSp73  =  [ChaR[] ]" ))43]raHc[]gNIRtS[,)38]raHc[+98]raHc[+611]raHc[((eCAlper.)421]raHc[]gNIRtS[,'5IP'(eCAlper.)'$',)09]raHc[+99]raHc[+701]raHc[((eCAlper.)93]raHc[]gNIRtS[,'vzW'(eCAlper.)'


2halB.tcejboZck tuptuO-etirW

7halB.tcejboZck +'+' 6halB.tcejboZck + halB.tc'+'ejboZck '+'= 2galFFT'+'C:'+'vneZck

SYt!eciNSYt = 1galFFTC:vneZck

SYt...aedi dab yre'+'v'+' ,yre'+'v a yllacipyt svzWtaht ,ton fI .ti gninnur erofeb siht detacsufbo-ed uoy epoh ISYt eulaV- 2halB emaN- '+'ytreporPetoN epy'+'TrebmeM- rebmeM-ddA 5IP tcejboZck

SYt'+'.uoy tresed dna dnuora nur annog reveNSYt eulaV- 9hal'+'B emaN- ytreporPetoN epyTrebmeM- rebmeM-ddA 5'+'IP tcejboZck

SYt.nwod uo'+'y tel annog '+'re'+'veN .'+'pu uoy evig annog reveNSYt eulaV- 8halB emaN- ytreporPetoN epyTrebm'+'eM- rebmeM-d'+'dA 5IP tcejboZck

SYt}f1j9kdSYt eulaV- 7halB emaN- y'+'treporPetoN ep'+'yTrebmeM- rebmeM-ddA 5IP tcejboZck

SYtg4lf_3ht_t0nSYt eulaV- 4halB emaN- yt'+'reporPetoN epyTrebmeM- rebmeM-ddA 5IP tcejboZck

SYt1#f!J{SYt eulaV- 6halB emaN- ytreporPetoN epyTrebmeM- rebmeM-'+'ddA 5IP tcejboZck

SYtgalF,ehT,toN,oslASYt eulaV- 5halB emaN- ytreporPetoN epyTrebmeM- rebmeM-ddA 5IP tcejboZck

SY'+'t}fdjfkslfdSYt eulaV- 3halB emaN- ytrepor'+'PetoN e'+'pyTrebmeM- rebmeM-ddA 5IP tcejboZ'+'ck

SYtgalfSYt eulaV- halB em'+'aN- ytreporPetoN e'+'pyTrebmeM- rebmeM-ddA 5IP tcej'+'boZck

tc'+'ejbO'+'SP tcejbO-weN = tc'+'ejboZck'( ()''nioJ-'x'+]3,1[)eCNERefErpESoBreV$]GniRTS[( (. " ;[aRRAy]::REVerse($MrSp73);. ( 'IeX') ( -JoiN$MrSp73)
```

#### Out

```powershell
$object = New-Object PSObject;
$object | Add-Member  NoteProperty  Blah  "flag";
$object | Add-Member  NoteProperty  Blah3  "dflskfjdf}";
$object | Add-Member  NoteProperty  Blah5  "Also,Not,The,Flag";
$object | Add-Member  NoteProperty  Blah6  "{J!f`#1";
$object | Add-Member  NoteProperty  Blah4  "n0t_th3_fl4g";
$object | Add-Member  NoteProperty  Blah7  "dk9j1f}";
$object | Add-Member  NoteProperty  Blah8  "Never gonna give you up. Never gonna let you down.";
$object | Add-Member  NoteProperty  Blah9  "Never gonna run around and desert you.";
$object | Add-Member  NoteProperty  Blah2  "I hope you de-obfuscated this before running it. If not, that''s typically a very, very bad idea...";
$env:CTFFlag1 = "Nice!";
$env:CTFFlag2 = $object.Blah + $object.Blah6 + $object.Blah7;
Write-Output $object.Blah2;
```

### References 

- https://github.com/R3MRUM/PSDecode
- https://robwillis.info/2020/08/invoke-decoder-a-powershell-script-to-decode-deobfuscate-malware-samples/
- https://www.varonis.com/blog/adventures-malware-free-hacking-part-ii/
- https://gist.github.com/notdodo/3d5ac56cd837c3f79d2c687f3e75cac1
