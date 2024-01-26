import datetime
import io
import typing
import datetime as dt
from dataclasses import dataclass

import pandas as pd
import urllib.request

from termin import Termin

DEFAULT_SOURCE = 'https://www.lg-aachen.nrw.de/behoerde/sitzungstermine/index.php?&termsPerPage=0#sitzungsTermineDates'

DATED_SOURCE = 'https://www.lg-aachen.nrw.de/behoerde/sitzungstermine/index.php?startDate={timestamp}&orderBy=datum&sort=asc&termsPerPage=0#stForm'


def pull(source=DEFAULT_SOURCE, date=dt.date.today()) -> typing.List[Termin]:
    with urllib.request.urlopen(source) as fp:
        content = fp.read().decode('utf-8')
    tables = pd.read_html(io.StringIO(content))
    assert len(tables) == 1
    frame = tables[0]
    termine = []
    for _, t in frame.iterrows():
        try:
            time = dt.datetime.strptime(t['Uhrzeit'], '%H:%M Uhr').time()
            datetime = dt.datetime.combine(date, time)
        except ValueError:
            continue
        beschreibung = t['Termin']
        aktenzeichen = t['Aktenzeichen']
        verfahren = t['Verfahren']
        saal = t['Saal']
        hinweis = t['Hinweis'] if not pd.isna(t['Hinweis']) else ""
        termine.append(Termin(datetime, beschreibung, aktenzeichen, verfahren, saal, hinweis))
    return termine


def pull_date(date=dt.date.today()) -> typing.List[Termin]:
    datetime = dt.datetime.combine(date, dt.time())
    source = DATED_SOURCE.format(timestamp=int(datetime.timestamp()))
    return pull(source, date)


@dataclass
class Scrape:
    date: dt.date
    termine: list[Termin]


class Scraper:

    def __init__(self, datenbank=None, watchlist=None):
        pass

    def update(self) -> Scrape:
        '''
        Pull the most recent table, append it to daten, mark deleted entries as deleted and
        return list of Termin objects matching watchlist
        '''
        today = dt.date.today()
        scraped_daten = []
        for i in range(7):
            delta = dt.timedelta(days=i)
            scrape = pull_date(today + delta)
            scraped_daten.extend(scrape)
            # TODO: mark entries not found in scrape as deleted
            # TODO: mark existing and changed entries as not angekuendigt

        return Scrape(date=datetime.datetime.now(), termine=scraped_daten)


# TODO remove this testing code
data = [Termin(d, '_', a, '_', '_', '_') for d, a in [('2022-1-1', 'A'), ('2022-1-2', 'B'), ('2022-2-1', 'C')]]

scraper = Scraper()
