from pprint import pprint

import pync
from quart import Quart, request

app = Quart(__name__)


@app.route("/test", methods=['POST'])
async def test_notify():
    pync.notify('Hello World', open='http://github.com/')
    return 'OK'


# See https://docs.splunk.com/Documentation/Splunk/latest/Alert/Webhooks

@app.route("/alert", methods=['POST'])
async def alert():
    await request.get_data()
    print("Alert from splunk")
    j = await request.get_json()
    # pprint(j)
    first_result = j["result"]
    video_title = first_result["title"]
    channel = first_result["channelTitle"]
    vid_id = first_result["resourceId.videoId"]
    video_url = f"https://www.youtube.com/watch?v={vid_id}"
    pync.notify(f'{video_title}',
                title=f"Youtube - New {channel} Video",
                open=video_url)
    return "Notification sent"


if __name__ == '__main__':
    app.run()
