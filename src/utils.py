from __future__ import annotations

import re
import unittest

az_regex = r'(([A-Z])\w*\s\d+[/]\d{2})'


def clean_akteneichen(aktenzeichen: str) -> None | str:
    """
    Input sanitization für durch den User eingegebene Aktenzeichen. Versucht auf den gegbenen
    String ein Regex zu matchen und gibt den matchenden String zurück

    Parameters
    ----------

    aktenzeichen: str

    Returns
    -------

    Gematchten String
    """
    cleaned = re.search(az_regex, aktenzeichen).group(0)

    if cleaned == "":
        return None
    else:
        return cleaned


class TestUtils(unittest.TestCase):
    def test_cleaned_aktenzeichen(self):
        teststring = "11:30 Uhr 	Hauptverhandlungstermin 	Bußgeldverfahren 	A 2.003 	OWi 9/23 (Amtsgericht)"

        cleaned = clean_akteneichen(teststring)
        print(cleaned)

        self.assertEqual("OWi 9/23", cleaned)
