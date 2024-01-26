from dataclasses import dataclass
import datetime


@dataclass
class Termin:
    datum: datetime.datetime
    beschreibung: str
    aktenzeichen: str
    verfahren: str
    saal: str
    hinweis: str

    def __eq__(self, other):
        if self.__class__ == Termin and other.__class__ == Termin:

            if self.aktenzeichen == other.aktenzeichen and self.datum.date() == other.datum.date():
                return True

        return False

    def __str__(self):
        return (f"{self.verfahren} mit Aktenzeichen {self.aktenzeichen} am {self.datum} in Saal {self.saal} \n"
                f"HINWEIS: {self.hinweis}")


