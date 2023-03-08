import typing
from dataclasses import dataclass
import datetime as dt
import zoneinfo
import pandas as pd
import urllib.request

from termin import Termin
from datenbank import Datenbank, COLUMNS, TIMEZONE

DEFAULT_SOURCE='https://www.lg-aachen.nrw.de/behoerde/sitzungstermine/index.php?&termsPerPage=0#sitzungsTermineDates'

tz = zoneinfo.ZoneInfo(TIMEZONE)

def pull(source=DEFAULT_SOURCE, date=dt.date.today()) -> typing.List[Termin]:
    with urllib.request.urlopen(source) as fp:
        content = fp.read().decode('utf-8')
    tables = pd.read_html(content)
    assert len(tables) == 1
    frame = tables[0]
    termine = []
    for _, t in frame.iterrows():
        try:
            time = dt.datetime.strptime(t['Uhrzeit'], '%H:%M Uhr').time()
            datetime = dt.datetime.combine(date, time, tzinfo=tz)
        except ValueError:
            continue
        beschreibung = t['Termin']
        aktenzeichen = t['Aktenzeichen']
        verfahren    = t['Verfahren']
        saal         = t['Saal']
        hinweis      = t['Hinweis'] if not pd.isna(t['Hinweis']) else pd.NA
        termine.append( Termin(datetime, beschreibung, aktenzeichen, verfahren, saal, hinweis, False) )
    return termine

def pull_date(date=dt.date.today()) -> typing.List[Termin]:
    return

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

    def update(self) -> typing.List[Termin]:
        '''
        Pull the most recent table, append it to daten, mark deleted entries as deleted and
        return list of Termin objects matching watchlist
        '''
        self._daten.append(pull_date())
        #TODO
        return []

#TODO remove this testing code
data = [ Termin(d,'_',a,'_','_','_',False) for d,a in [('2022-1-1','A'),('2022-1-2','B'),('2022-2-1','C')] ]

scraper = Scraper()
