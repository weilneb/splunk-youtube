import os
from typing import Dict

import requests

hec_token = os.environ['SPLUNK_HEC_TOKEN']
splunk_hec_base_url = os.getenv('SPLUNK_HEC_BASE_URL', 'http://localhost:8088')
splunk_integration_disabled = 'DISABLE_SPLUNK_HEC' in os.environ


def send_to_splunk_hec(data: Dict, timestamp: float):
    if not splunk_integration_disabled:
        print("Sending data to splunk")
        resp = requests.post(url=f"{splunk_hec_base_url}/services/collector/event",
                             headers={'Authorization': f'Splunk {hec_token}'},
                             json={
                                 "time": timestamp,
                                 "event": data,
                             })
        resp.raise_for_status()
    else:
        print("Not sending - Splunk integration disabled.")
