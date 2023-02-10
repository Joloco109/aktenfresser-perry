from dataclasses import dataclass
import pandas as pd

from termin import Termin
from datenbank import Datenbank

@dataclass
class Scraper:
    daten: Datenbank

    def __init__(self):
        daten = None

#TODO remove this testing code
data = [ Termin(d,'_',a,'_','_','_',False) for d,a in [('2022-1-1','A'),('2022-1-2','B'),('2022-2-1','C')] ]
