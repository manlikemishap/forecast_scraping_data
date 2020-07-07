import csv
import datetime
import dateparser
import pytz
from operator import itemgetter

POLL_FIELDS = [
    "start_date",
    "end_date",
    "release_date",
    "pollster",
    "office",
    "state",
    "district",
    "sample",
    "moe",
    "dem_pct",
    "rep_pct",
    "ind_pct"
]

EASTERN = pytz.timezone('US/Eastern')
DATE_FMT = "%Y-%m-%d"

def today_eastern():
    dt = datetime.datetime.now(tz=pytz.utc).astimezone(EASTERN)
    return dt.strftime(DATE_FMT)

def ts_to_date(ts):
    if isinstance(ts, (int, float)):
        d = datetime.datetime.fromtimestamp(ts, tz=pytz.utc).astimezone(EASTERN)
    else:
        d = dateparser.parse(ts).astimezone(EASTERN)
    return d.strftime(DATE_FMT)

class Predictions(object):
    def __init__(self, prediction_list):
        self.prediction_list = prediction_list

    def to_csv(self, dest):
        writer = csv.DictWriter(dest, fieldnames=POLL_FIELDS)
        writer.writeheader()
        for p in sorted(self.prediction_list, key=itemgetter(*POLL_FIELDS)):
            row = dict(p)
            writer.writerow(row)

class Poll(object):
    def get_latest_polls(self):
        return False

    def get_historical_polls(self):
        return False

    def prune_polls(self):
        return False
