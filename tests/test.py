import unittest
from parameterized import parameterized

from scripts.common_utils import calculate_similarity, convert_ocr_string

class TestCommonUtils(unittest.TestCase):

    @parameterized.expand([
        ("たっぷりかけちゃいますね♡", "たつふりかけちやいますね", 100),
        ("そこ、動くなっ！", "そこ 動くなつ", 100),
        ("つめた～いココナッツジュース！", "つめたいココナツツツユース", 100),
        ("旋律の一音目", "旋律のー音目", 100),
        ("心理掌握", "心理", 50),
    ])
    def test_calculate_similarity(self, s1, s2, result):
        s1 = convert_ocr_string(s1)
        s2 = convert_ocr_string(s2)
        self.assertEqual(calculate_similarity(s1, s2), result)
