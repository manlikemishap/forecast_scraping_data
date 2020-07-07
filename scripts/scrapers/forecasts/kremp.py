import requests
from . import forecast
import json
import re
import sys
import us

URL = "https://raw.githubusercontent.com/pkremp/polls/8954a09ca462e04183b407e7f550a5067d1cce3f/report.html"

class Kremp(forecast.Forecast):
    def get_latest_predictions(self):
        html = requests.get(URL).content.decode("utf-8")
        data = json.loads(re.search(r'(\[\["\*National.*?\]\])', html).group(1))
        biden_probs = list(zip(data[0], data[-1], data[-2]))[1:]
        biden_probs.append(("DC", 1, None))
        arr = []
        for state, biden_prob, biden_share in biden_probs:
            for party in [ "D", "R" ]:
                if biden_share == None:
                    est_share = None
                elif party == "D":
                    est_share = biden_share
                else:
                    est_share = 1 - biden_share
                arr.append({
                    "date": "2016-11-07",
                    "model": "kremp",
                    "office": "P",
                    "state": us.states.lookup(state).abbr,
                    "party": party,
                    "candidate": "CLINTON" if party == "D" else "TRUMP",
                    "win_prob": biden_prob if party == "D" else 1 - biden_prob,
                    "est_diff": None,
                    "est_share": None,
                    "est_share_2p": est_share,
                })
        return forecast.Predictions(arr)
