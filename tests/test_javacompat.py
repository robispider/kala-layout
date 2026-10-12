import unittest

from bangla_dh.colemak.javacompat import (
    f32, java_format_fixed, java_is_alphabetic, java_split, java_upper_char, shortest_f32_repr,
)


class Float32Tests(unittest.TestCase):
    def test_rounds_to_binary32(self):
        self.assertEqual(f32(0.1), 0.10000000149011612)
        self.assertEqual(f32(1.0), 1.0)

    def test_float_division_matches_binary32(self):
        # 1189270 / 11366958 computed in binary32 differs from binary64.
        value = f32(f32(1189270) / f32(11366958))
        self.assertEqual(value, f32(value))
        self.assertNotEqual(value, 1189270 / 11366958)

    def test_shortest_repr(self):
        self.assertEqual(shortest_f32_repr(f32(0.1)), "0.1")
        self.assertEqual(shortest_f32_repr(f32(1 / 3)), "0.33333334")


class JavaFormatTests(unittest.TestCase):
    def test_half_up_on_exact_ties(self):
        self.assertEqual(java_format_fixed(0.0625, 3), "0.063")
        self.assertEqual(f"{0.0625:.3f}", "0.062")  # Python differs

    def test_half_up_on_shortest_digits(self):
        # 1.0005 is stored slightly below 1.0005; Java rounds its shortest digits.
        self.assertEqual(java_format_fixed(1.0005, 3), "1.001")

    def test_space_flag(self):
        self.assertEqual(java_format_fixed(1.5, 3, space_flag=True), " 1.500")
        self.assertEqual(java_format_fixed(-0.25, 3, space_flag=True), "-0.250")


class TextTests(unittest.TestCase):
    def test_split_drops_empty_tokens(self):
        self.assertEqual(java_split("q  w   e", " "), ["q", "w", "e"])

    def test_upper_char_never_expands(self):
        self.assertEqual(java_upper_char("ß"), "ß")
        self.assertEqual(java_upper_char("a"), "A")

    def test_bengali_alphabetic(self):
        self.assertTrue(java_is_alphabetic("ক"))
        self.assertTrue(java_is_alphabetic("া"))  # Other_Alphabetic vowel sign
        self.assertFalse(java_is_alphabetic("্"))  # hasant
        self.assertFalse(java_is_alphabetic(";"))


if __name__ == "__main__":
    unittest.main()
