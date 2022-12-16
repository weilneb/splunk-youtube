import argparse
import os
from typing import List

import yaml
from sqlalchemy.orm import Session

from scraper import YTScraper
from scraper import get_db_engine, init_db_tables

parser = argparse.ArgumentParser(description='Scrape Youtube API for new videos and send to Splunk HEC')
parser.add_argument("filename", help="YAML file containing youtube channels")
parser.add_argument("database", help="Path to sqlite database, which manages pagination state for Youtube API")


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

    db_engine = get_db_engine(path_to_db=args.database)
    init_db_tables(db_engine)

    api_key = os.environ['YOUTUBE_API_KEY']
    with Session(db_engine) as session:
        scraper = YTScraper(api_key, db_session=session, api_page_size=10)
        # scraper = YTScraper(api_key, db_session=session)
        scraper.add_channel_ids(channel_ids)
        scraper.scrape_loop()
