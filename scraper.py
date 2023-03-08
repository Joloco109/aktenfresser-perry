import typing
from dataclasses import dataclass
import pandas as pd

from termin import Termin
from datenbank import Datenbank, COLUMNS

class Scraper:
    _daten: Datenbank
    _watchlist: Datenbank

    def __init__(self, datenbank=None, watchlist=None):
        self._daten = Datenbank("./data/daten.h5") if datenbank is None else datenbank
        self._watchlist = Datenbank("./data/watch.h5") if watchlist is None else watchlist

    def watch(self, entry:dict) -> None:
        '''
        Adds entry to watchlist
        entry should be a dict with keys from COLUMNS (not specified keys will be ignored in comparisons)
        '''
        entry = { c: [(entry[c] if c in entry.keys() else pd.NA)] for c in COLUMNS.keys() }
        self._watchlist.append_frame(pd.DataFrame(entry))

    def unwatch(self, entry:dict) -> None:
        '''
        Removes the matching entry from watchlist
        TODO
        '''
        pass

    def pull(self, source='TODO') -> typing.List[Termin]:
        #TODO
        return []

    def update(self) -> typing.List[Termin]:
        '''
        Pull the most recent table, append it to daten and return list of Termin objects matching watchlist
        '''
        self._daten.append(self.pull())
        #TODO
        return []

#TODO remove this testing code
data = [ Termin(d,'_',a,'_','_','_',False) for d,a in [('2022-1-1','A'),('2022-1-2','B'),('2022-2-1','C')] ]
