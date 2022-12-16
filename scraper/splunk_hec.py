import os
from typing import Dict

import requests

hec_token = os.environ['SPLUNK_HEC_TOKEN']


def send_to_splunk_hec(data: Dict, timestamp: float):
    print("Sending data to splunk")
    resp = requests.post(url="http://localhost:8088/services/collector/event",
                         headers={'Authorization': f'Splunk {hec_token}'},
                         json={
                             "time": timestamp,
                             "event": data,
                         })
    resp.raise_for_status()
