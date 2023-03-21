from dataclasses import dataclass
import datetime as dt
import zoneinfo
import pandas as pd
import urllib.request
import functools

from termin import Termin, TerminList
from datenbank import Datenbank, COLUMNS, TIMEZONE

DEFAULT_SOURCE='https://www.lg-aachen.nrw.de/behoerde/sitzungstermine/index.php?&termsPerPage=0#sitzungsTermineDates'

DATED_SOURCE='https://www.lg-aachen.nrw.de/behoerde/sitzungstermine/index.php?startDate={timestamp}&orderBy=datum&sort=asc&termsPerPage=0#stForm'

tz = zoneinfo.ZoneInfo(TIMEZONE)

def pull(source=DEFAULT_SOURCE, date=dt.date.today()) -> TerminList:
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
    return TerminList(termine)

def pull_date(date=dt.date.today()) -> TerminList:
    datetime = dt.datetime.combine(date, dt.time(), tzinfo=tz)
    source = DATED_SOURCE.format(timestamp=int(datetime.timestamp()))
    return pull(source, date)

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
        # TODO
        raise NotImplemented('Removing entries from the watchlist is not yet implemented!')

    def match_watchlist(self, termine: TerminList) -> TerminList:
        # TODO improve this, performance is gonna be terrible
        # It should probably be moved partially into TerminList
        matches = []
        for w in self._watchlist:
            matching = termine[:]
            for col in COLUMNS:
                if col in ('erstellt','veraendert', 'geloescht', 'angekuendigt'):
                    continue
                target = getattr(w, col)
                if not pd.isna(target):
                    matching = [m for m in matching if getattr(m, col) == target]
            matches.extend(matching)
        return TerminList(matches)


    def update(self) -> TerminList:
        '''
        Pull the most recent table, append it to daten, mark deleted entries as deleted and
        return list of Termin objects matching watchlist
        '''
        today = dt.date.today()
        scraped_daten = []
        for i in range(7):
            delta = dt.timedelta(days=i)
            scrape = pull_date(today+delta)
            scraped_daten.append(scrape)
            # TODO: mark entries not found in scrape as deleted
            # TODO: mark existing and changed entries as not angekuendigt
        scraped_daten = functools.reduce(TerminList.concat, scraped_daten)

        self._daten.append(scraped_daten)
        watched = self.match_watchlist(scraped_daten)
        watched = TerminList([w for w in watched if not w.angekuendigt])
        return watched

#TODO remove this testing code
data = [ Termin(d,'_',a,'_','_','_',False) for d,a in [('2022-1-1','A'),('2022-1-2','B'),('2022-2-1','C')] ]

scraper = Scraper()
