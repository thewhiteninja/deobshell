import difflib
import os
import shutil
from unittest import TestCase

from main import deob, OPTIONS
from modules.logger import set_log_level, LogLevel
from modules.utils import make_directory, delete_directory


def diff_text(a, b):
    with open(a) as fa:
        text1 = fa.readlines()
    with open(b) as fb:
        text2 = fb.readlines()

    return list(difflib.unified_diff(text1, text2))


def test(folder, name):
    src = os.path.join("data", folder, f"{name}.ps1.donotrun")
    expected = os.path.join("data", folder, f"{name}.deob.ps1.donotrun")
    tmp_input = os.path.join("tmp", f"{name}.ps1")
    tmp_output = os.path.join("tmp", f"{name}.deob.ps1")

    shutil.copy2(src, tmp_input)
    if not deob(tmp_input):
        return -1

    diff = diff_text(expected, tmp_output)
    for line in diff:
        print(line)

    return len(diff)


class Test(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        make_directory("tmp")
        # set_log_level(LogLevel.DEBUG, 500)
        set_log_level(LogLevel.NONE)
        OPTIONS["docker"] = True

    @classmethod
    def tearDownClass(cls) -> None:
        # delete_directory("tmp")
        pass

    def test_emotet1(self):
        self.assertEqual(0, test("malwares", "emotet1"))

    def test_malware1(self):
        self.assertEqual(0, test("malwares", "malware1"))

    def test_malware2(self):
        self.assertEqual(0, test("malwares", "malware2"))

    def test_malware3(self):
        self.assertEqual(0, test("malwares", "malware3"))

    def test_malware5(self):
        self.assertEqual(0, test("malwares", "malware5"))
