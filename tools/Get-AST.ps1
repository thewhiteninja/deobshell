<#
.SYNOPSIS
    Generate AST of Powershell script to a XML file
.DESCRIPTION
    This script parses a Powershell script using System.Management.Automation.Language.Parser to
    generate the corresponding AST (abstract syntax tree) as a XML file.
.PARAMETER ps1
    The path to the Powershell script.
.PARAMETER ast
    The path to the XML file.
.EXAMPLE
    C:\PS>
    <Description of example>
.NOTES
    Author: @thewhiteninja
    Date:   March 28, 2021
#>


param (
    [ValidateScript({
            if(-Not ($_ | Test-Path -PathType Leaf) ){
                throw "The ps1 argument must be an existing file"
            }
            if($_ -notmatch "(\.ps1)"){
                throw "The file specified in the ps1 argument must have ps1 extension."
            }
            return $true
        })]
    [Parameter(Mandatory=$true)]
    [System.IO.FileInfo] $ps1,
    [string] $ast,
    [switch] $help
)

$global:n_nodes = 0

# This works great when running docker on command line but fails when running from python.
# When run from python, there is an error "the input device is not a TTY" and that itself stops the script.
# $ErrorActionPreference = "Continue"

# filters control characters but allows only properly-formed surrogate sequences
$_invalidXMLChars =
    "(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]|[\uD800-\uDBFF](?![\uDC00-\uDFFF])|[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F\uFEFF\uFFFE\uFFFF]"

# removes any unusual unicode characters that cant be encoded into XML
function SanitizeXMLValues($text)
{
    return $text -replace $_invalidXMLChars, ""
}

function PopulateNode($xmlWriter, $object)
{
    foreach ($child in $object.PSObject.Properties)
    {
        if ($child.Name -eq 'Parent')
        {
            continue
        }

        $childObject = $child.Value

        if ($null -eq $childObject)
        {
            continue
        }

        if ($childObject -is [System.Management.Automation.Language.Ast])
        {
            AddChildNode $xmlWriter $childObject
            continue
        }

        $collection = $childObject -as [System.Management.Automation.Language.Ast[]]
        if ($null -ne $collection)
        {
            $xmlWriter.WriteStartElement($child.Name)


            for ($i = 0; $i -lt $collection.Length; $i++)
            {
                AddChildNode $xmlWriter ($collection[$i])
            }

            $xmlWriter.WriteEndElement()
            continue
        }

        if ($childObject.GetType().FullName -match 'ReadOnlyCollection.*Tuple`2.*Ast.*Ast')
        {
            for ($i = 0; $i -lt $childObject.Count; $i++)
            {
                AddChildNode $xmlWriter ($childObject[$i].Item1)
                AddChildNode $xmlWriter ($childObject[$i].Item2)
            }
            continue
        }
    }
}

function AddChildNode($xmlWriter, $child)
{
    $global:n_nodes += 1

    if ($null -ne $child)
    {
        $xmlWriter.WriteStartElement($child.GetType().Name)

        foreach ($property in $child.PSObject.Properties)
        {
            if ($property.Name -in 'Name', 'ArgumentName', 'ParameterName', 'StaticType', 'StringConstantType', 'TypeName', 'VariablePath', 'Operator', 'Variable', 'Condition', 'Static', 'TokenKind', 'Flags')
            {
                $xmlWriter.WriteAttributeString($property.Name, $property.Value);
            }
        }
        foreach ($property in $child.PSObject.Properties)
        {
            if ($property.Name -in 'Value')
            {
                # We have to check for invalid xml chars before trying to write.
                # Otherwise the writer goes to error state. Not sure how to recover it.
                $sanitized = SanitizeXMLValues($property.Value);
                if ($sanitized.Length -ne $property.Value.Length)
                {
                    Write-Host "Invalid character in node value: $($_)"
                    Write-Host "Node: $($child | Format-List | Out-String)"
                    Write-Host "Using sanitized value: $($sanitized)"
                }
                try {
                    $xmlWriter.WriteString($sanitized);
                }
                catch {
                    Write-Host "Node: $($child | Out-String)"
                    Write-Error "Error writing value: $($_)"
                    throw $_.Exception
                }
            }
        }

        PopulateNode $xmlWriter $child

        $xmlWriter.WriteEndElement()
    }
}

function ConvertToAST($input_filename, $output_filename)
{
    $AST = [System.Management.Automation.Language.Parser]::ParseFile($input_filename, [ref]$null, [ref]$null)

    $xmlsettings = New-Object System.Xml.XmlWriterSettings
    $xmlsettings.Indent = $true
    $xmlsettings.IndentChars = "  "

    $XmlWriter = [System.XML.XmlWriter]::Create($output_filename, $xmlsettings)
    if ($null -ne $XmlWriter)
    {
        $xmlWriter.WriteStartDocument()

        AddChildNode $xmlWriter $AST

        $xmlWriter.WriteEndDocument()
        $xmlWriter.Flush()
        $xmlWriter.Close()
    }

    Write-Host $global:n_nodes nodes parsed
    Write-Host (Get-Item $output_filename).length bytes written
}

if ("" -eq $ast)
{
    $ast = [io.path]::ChangeExtension($ps1, '.xml')
}

ConvertToAST $ps1 $ast




