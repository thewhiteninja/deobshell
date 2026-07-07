# coding=utf-8
OPS = {
    "Minus": " - ",
    "Plus": " + ",
    "Multiply": " * ",
    "Divide": " / ",
    "Rem": " % ",
    "Format": " -f ",
    "Equals": " = ",
    "PlusEquals": " += ",
    "MinusEquals": " -= ",
    "MultiplyEquals": " *= ",
    "DivideEquals": " /= ",
    "RemEquals": " %= ",
    "PostfixPlusPlus": "++",
    "PostfixMinusMinus": "--",
    "Is": " -is ",
    "As": " -as ",
    "Ieq": " -eq ",
    "Ige": " -ge ",
    "Igt": " -gt ",
    "Ile": " -le ",
    "Ilt": " -lt ",
    "Ine": " -ne ",
    "Band": " -band ",
    "Bor": " -bor ",
    "Bxor": " -bxor ",
    "Bnot": " -bnot ",
    "Shl": " -shl ",
    "Shr": " -shr ",
    "BandEquals": " -band= ",
    "BorEquals": " -bor= ",
    "BxorEquals": " -bxor= ",
    "ShlEquals": " -shl= ",
    "ShrEquals": " -shr= ",
    "Ireplace": " -replace ",
    "Join": " -join ",
    "Imatch": " -match ",
    "Inotmatch": " -notmatch ",
    "Isplit": " -split ",
    "And": " -and ",
    "Or": " -or ",
    "DotDot": "..",
}


def do_const_comparison(a, b, operator):
    if operator == "Ieq":
        return a == b
    elif operator == "Ine":
        return a != b
    elif operator == "Ige":
        return a >= b
    elif operator == "Igt":
        return a > b
    elif operator == "Ile":
        return a <= b
    elif operator == "Ilt":
        return a < b

    return None
