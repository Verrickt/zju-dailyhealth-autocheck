from requests import post
import os
 
"""
TG 消息推送模块
"""



def post_tg(config,message):
    TG_TOKEN = config['bot_token']
    CHAT_ID = config['chat_id']
    PROXY = config['proxy']
    telegram_message = f"{message}"
    params = (
        ('chat_id', CHAT_ID),
        ('text', telegram_message),
        ('parse_mode', "Markdown"), #可选Html或Markdown
        ('disable_web_page_preview', "yes")
    )    
    telegram_url = "https://api.telegram.org/bot" + TG_TOKEN + "/sendMessage"
    proxies = {
        'https':PROXY,
        'http': PROXY
    }
    telegram_req = post(telegram_url, params=params,proxies=proxies)
    telegram_status = telegram_req.status_code
    if telegram_status == 200:
        print(f"INFO: Telegram Message sent")
    else:
        print("Telegram Error")

 
