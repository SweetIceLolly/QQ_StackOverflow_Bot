# -*- coding:utf-8 -*-

import requests
import json
from cqhttp import CQHttp
import asyncio
import websockets
import uuid
import hashlib
import time
import re
from YoudaoTranslateAPI import translate_chinese


def StackOverflowSearch(question):
    link = 'https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=relevance&q=' + question + '&site=stackoverflow'
    print('Requesting...')
    response = requests.get(link)
    status = response.status_code
    print('Status: ' + str(status))

    url = ''
    if status == 200:
        print('Parsing...')
        url = response.json()['items'][0]['link']
    return url


async def receive_qq_msg():
    global bot

    uri = 'ws://localhost:6700'
    async with websockets.connect(uri) as websocket:
        data = await websocket.recv()
        data = json.loads(data)
        if data['message_type'] == 'group':
            received_msg = data['message']
            if received_msg[0:22] == '[CQ:at,qq=2315335010] ':
                sender_id = data['sender']['user_id']
                from_group_id = data['group_id']
                received_msg = received_msg.replace('[CQ:at,qq=2315335010] ', '').strip()
                
                print(str(from_group_id) + ' - ' + str(sender_id) + ': ' + received_msg)
                if re.search(u'[\u4e00-\u9fff]', received_msg):         # chinese character found, try to translate the message
                    print('Chinese character found')
                    received_msg = translate_chinese(received_msg)
                response_msg = StackOverflowSearch(received_msg)
                if response_msg != '':
                    bot.send_group_msg(group_id=from_group_id,
                                       message = '[CQ:at,qq=' + str(sender_id) + ']' + ' ' + response_msg)
                
                print('Responded!\n')


bot = CQHttp(api_root='http://127.0.0.1:5700')
print('Ready! Waiting for messages...')
while True:
    try:
        asyncio.get_event_loop().run_until_complete(receive_qq_msg())
    except:
        pass
