from typing import Union, List
import pandas as pd
from datetime import datetime
import zoneinfo
from dataclasses import dataclass
from termin import Termin, create_termin, COLUMNS, TIMEZONE

DEFAULT_HDF_STORE = "./data/daten.h5"

COLUMNS = { **COLUMNS,
        "erstellt":     [pd.DatetimeTZDtype(tz=TIMEZONE)],
        "veraendert":   [pd.DatetimeTZDtype(tz=TIMEZONE)],
        "geloescht":    [pd.DatetimeTZDtype(tz=TIMEZONE)],
        }

ITEM_SIZES = 128

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

    @property
    def termine(self):
        '''
        Get the termine DataFrame of the Datenbank.
        After modifiying this you should call flush to sync to disc.
        '''
        if self._termine is None:
            raise ValueError('No Termine exist yet')
        return self._termine

    def append(self, data:List[Termin]):
        df = {}
        for c in COLUMNS:
            if c in ('erstellt','veraendert', 'geloescht'):
                continue
            df[c] = [ getattr(d, c) for d in data ]
        df['angekuendigt']= [ int(d.angekuendigt) if not pd.isna(d.angekuendigt) else -1 for d in data]
        now_local = datetime.now(zoneinfo.ZoneInfo(TIMEZONE))
        df['erstellt']    = [now_local for _ in data]
        df['veraendert']  = [now_local for _ in data]
        df['geloescht']   = [pd.NaT    for _ in data]
        self.append_frame(pd.DataFrame(df))

    def append_frame(self, data:pd.DataFrame):
        data['angekuendigt'] = data['angekuendigt'].fillna(-1)
        data = convert(data)
        if self._termine is None:
            self._termine = data
        else:
            #TODO Keep erstellt column, when dropping duplicates
            self._termine = pd.concat((self._termine,data)).drop_duplicates(['aktenzeichen','datum'], keep='last')
        self._store.put("termine", convert_np_types(data), format='t', min_itemsize=ITEM_SIZES, append=True)

    def search(self, value, column='aktenzeichen'):
        # TODO
        if isinstance(column, str):
            column = [column]
        return

    def __getitem__(self, key) -> Union[Termin, List[Termin]]:
        if isinstance(key,  slice):
            termine = []
            for i,t in self._termine.iloc[key].iterrows():
                termin_args = { **(t) }
                termin_args = {key:val for key,val in termin_args.items()
                               if key not in ['erstellt','veraendert','geloescht']}
                termine.append(create_termin(**termin_args))
            return termine
        else:
            termin_args = { **(self._termine.iloc[key]) }
            termin_args = {key:val for key,val in termin_args.items()
                           if key not in ['erstellt','veraendert','geloescht']}
            return create_termin(**termin_args)

    def __iter__(self):
        return iter(self[:]) if self._termine is not None else iter([])

    def flush(self, *args):
        self._store.put("termine", convert_np_types(self._termine),
                        format='t', min_itemsize=ITEM_SIZES, append=False)
        self._store.flush(*args)

    def reload(self, *args):
        self._termine = convert(self._store["termine"])


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
