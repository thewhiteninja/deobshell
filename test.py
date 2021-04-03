import difflib
import os
import shutil
from unittest import TestCase

from main import deob
from modules.logger import set_log_level, LogLevel
from modules.utils import make_directory, delete_directory


def diff_text(a, b):
    with open(a) as fa:
        text1 = fa.readlines()
    with open(b) as fb:
        text2 = fb.readlines()

    return list(difflib.unified_diff(text1, text2))


def test(name):
    tmp_input = os.path.join("tmp", f"{name}.ps1")

    shutil.copy2(os.path.join("data", f"{name}.ps1"), tmp_input)
    deob(tmp_input)

    diff = diff_text(os.path.join("tmp", f"{name}.deob.ps1"), os.path.join("data", f"{name}.deob.ps1"))
    for line in diff:
        print(line)

    return len(diff)


class Test(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        make_directory("tmp")
        set_log_level(LogLevel.NONE)

    @classmethod
    def tearDownClass(cls) -> None:
        delete_directory("tmp")

    def test_emotet1(self):
        self.assertEqual(test("emotet1"), 0)

    def test_malware1(self):
        self.assertEqual(test("malware1"), 0)

    def test_malware2(self):
        self.assertEqual(test("malware2"), 0)
