from typing import Union, List
from dataclasses import dataclass
import datetime

import pandas as pd

TIMEZONE = 'Europe/Berlin'
COLUMNS = {
        "datum":        [pd.DatetimeTZDtype(tz=TIMEZONE)],
        "beschreibung": [pd.StringDtype(), object],
        "aktenzeichen": [pd.StringDtype(), object],
        "verfahren":    [pd.StringDtype(), object],
        "saal":         [pd.StringDtype(), object],
        "hinweis":      [pd.StringDtype(), object],
        # angekuendigt has to managed inside an integer, since pandas stores do not really support bools with NA
        "angekuendigt": [pd.Int8Dtype(),int],
        }

@dataclass
class Termin:
    datum: datetime.datetime
    beschreibung: str
    aktenzeichen: str
    verfahren: str
    saal: str
    hinweis: str

    angekuendigt: bool

    def ankuendigen(self) -> str:

        return_str = f"{self.verfahren} mit Aktenzeichen {self.aktenzeichen} wird am {self.datum} in Saal {self.saal} verhandelt."
        self.angekuendigt = True

        return return_str

    def __eq__(self, other):
        if self.__class__ == Termin and other.__class__ == Termin:

            if self.aktenzeichen == other.aktenzeichen and self.datum.date() == other.datum.date():
                return True

        return False

    def __str__(self):
        return f"{self.verfahren} mit Aktenzeichen {self.aktenzeichen} am {self.datum} in Saal {self.saal}"

def create_termin(**termin_args):
    a = termin_args['angekuendigt']
    termin_args['angekuendigt'] = bool(a) if a > 0 else pd.NA
    return Termin(**termin_args)

class TerminList:
    _termine : pd.DataFrame

    def __init__(self, termine: Union[pd.DataFrame, Termin, List[Termin]]):
        if isinstance(termine, pd.DataFrame):
            self._termine = termine[COLUMNS.keys()]
        else:
            if isinstance(termine, Termin):
                termine = [termine]
            df = {}
            for c in COLUMNS.keys():
                if c == 'angekuendigt':
                    continue
                df[c] = [ getattr(t, c) for t in termine ]
            df['angekuendigt']= [ int(t.angekuendigt) if not pd.isna(t.angekuendigt) else -1 for t in termine]
            self._termine = pd.DataFrame(df)

    def copy(self, *args, **kwargs) -> 'TerminList':
        return TerminList(self._termine.copy(*args, **kwargs))

    def concat(self, termine: Union[pd.DataFrame, Termin, List[Termin], 'TerminList']) -> 'TerminList':
        if not isinstance(termine, TerminList):
            termine = TerminList(termine)
        return TerminList(pd.concat((self._termine, termine._termine)))

    def __setitem__(self, key, value: Union[pd.DataFrame, Termin, List[Termin], 'TerminList']):
        if not isinstance(value, TerminList):
            value = TerminList(value)
        self._termine.iloc[key] = value._termine

    def __getitem__(self, key) -> Union[Termin, List[Termin]]:
        if isinstance(key,  slice):
            termine = []
            for i,t in self._termine.iloc[key].iterrows():
                termin_args = { **(t) }
                termine.append(create_termin(**termin_args))
            return termine
        else:
            termin_args = { **(self._termine.iloc[key]) }
            return create_termin(**termin_args)

    def __iter__(self):
        return iter(self[:])
