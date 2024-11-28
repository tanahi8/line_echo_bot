import os
import sys

from flask import Flask, request, abort

from linebot.v3 import WebhookHandler

from linebot.v3.webhooks import MessageEvent, TextMessageContent, UserSource
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, TextMessage, ReplyMessageRequest
from linebot.v3.exceptions import InvalidSignatureError

channel_access_token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
channel_secret = os.environ["LINE_CHANNEL_SECRET"]

if channel_access_token is None or channel_secret is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)

handler = WebhookHandler(channel_secret)
configuration = Configuration(access_token=channel_access_token)

app = Flask(__name__)


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        abort(400, e)

    return "OK"

import random
import datetime

def generate_response(from_user, text):
    res = []
    res.append(TextMessage(text=f"あー{from_user}さん。。。"))
    if "こん" in text:
        res.append(TextMessage(text="こんちゃー"))
    elif "おは" in text:
        res.append(TextMessage(text="おはこんばんわ"))
    elif "何時" in text or "なんじ" in text:
        now = datetime.datetime.now()
        res.append(TextMessage(text=f"今は{now.hour}時{now.minute}分ですよ"))
    else:
        msg_templates = ["ホゲホゲ", "そうねぇ", f"「{text}」って言ったね？"]
        msg_num = len(msg_templates) # メッセージの数
        idx = random.randrange(msg_num) # 0からmsg_num-1までの乱数を生成
        res.append(TextMessage(text=msg_templates[idx]))
    return res


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if isinstance(event.source, UserSource):
            profile = line_bot_api.get_profile(event.source.user_id)
            res = generate_response(profile.display_name, text)
            line_bot_api.reply_message_with_http_info(ReplyMessageRequest(reply_token=event.reply_token, messages=res))
        else:
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token, messages=[TextMessage(text="Received message: " + text)]
                )
            )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
