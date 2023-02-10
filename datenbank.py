import pandas as pd
from datetime import datetime
import zoneinfo
from dataclasses import dataclass
from termin import Termin

DEFAULT_HDF_STORE = "./daten.h5"
TIMEZONE = 'Europe/Berlin'

COLUMNS = {
        "datum":        [pd.DatetimeTZDtype(tz=TIMEZONE)],
        "beschreibung": [pd.StringDtype(), object],
        "aktenzeichen": [pd.StringDtype(), object],
        "verfahren":    [pd.StringDtype(), object],
        "saal":         [pd.StringDtype(), object],
        "hinweis":      [pd.StringDtype(), object],
        "angekuendigt": [pd.BooleanDtype(),int],
        "erstellt":     [pd.DatetimeTZDtype(tz=TIMEZONE)]
        }

class Datenbank:
    _store : pd.HDFStore
    _termine: pd.DataFrame

    def __init__(self, file=None):
        if file is None:
            file = DEFAULT_HDF_STORE
        self._store = pd.HDFStore(file)
        try:
            self._termine = convert(self._store["termine"])
        except KeyError:
            self._termine = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._store.put("termine", convert_np_types(self._termine), format='t', append=False)

    @property
    def termine(self):
        '''
        Get the termine DataFrame of the Datenbank.
        After modifiying this you should call flush to sync to disc.
        '''
        if self._termine is None:
            raise ValueError('No Termine exist yet')
        return self._termine

    def append(self, data:[Termin]):
        df = {}
        for c in COLUMNS:
            if c == 'erstellt':
                continue
            df[c] = [ getattr(d, c) for d in data ]
        now_local = datetime.now(zoneinfo.ZoneInfo(TIMEZONE))
        df['erstellt'] = [now_local for _ in data]
        self.append_frame(pd.DataFrame(df))

    def append_frame(self, data:pd.DataFrame):
        data = convert(data)
        if self._termine is None:
            self._termine = data
        else:
            self._termine = pd.concat((self._termine,data))
        self._store.put("termine", convert_np_types(data), format='t', append=True)

    def __getitem__(self, key) -> Termin:
        return Termin(**(self._termine[key]))

    def flush(self, *args):
        self._store.put("termine", convert_np_types(self._termine), format='t', append=False)
        self._store.flush(*args)


def convert(data:pd.DataFrame) -> pd.DataFrame:
    '''
    Creates a DataFrame copy of data with the standard column types
    '''
    return pd.DataFrame({ c: data[c].astype(t[0]) for c,t in COLUMNS.items() })

def convert_np_types(data:pd.DataFrame) -> pd.DataFrame:
    '''
    Creates a DataFrame copy of data with the alternate numpy column types compatible with storing 
    '''
    return pd.DataFrame({ c: data[c].astype(t[-1]) for c,t in COLUMNS.items() })
