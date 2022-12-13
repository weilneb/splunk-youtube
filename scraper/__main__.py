import argparse
import os
from typing import List

import yaml

from scraper import YTScraper

parser = argparse.ArgumentParser(description='Scrape Youtube API for new videos and send to Splunk HEC')
parser.add_argument("filename", help="YAML file containing youtube channels")


def read_channels_yaml_config(filename: str) -> List[str]:
    print(f"Opening {filename}")
    with open(filename) as f:
        obj = yaml.safe_load(f)
        channels = [x['channel_id'] for x in obj['channels']]
        return channels


if __name__ == '__main__':
    args = parser.parse_args()
    print(args)
    channel_ids = read_channels_yaml_config(args.filename)
    api_key = os.environ['YOUTUBE_API_KEY']
    scraper = YTScraper(api_key)
    scraper.add_channel_ids(channel_ids)
    scraper.scrape_loop()
