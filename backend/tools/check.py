import requests as req
import json
from application.app import logger


def get_res(content: str) -> int:
    access_token = '' # your own token of baidu API
    host = 'https://aip.baidubce.com/rest/2.0/antispam/v2/spam?access_token=%s'
    url = host % access_token
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        resp = req.post(url, headers=headers, data={'content': content})
        res = json.loads(resp.text)
        # print(res)
    except Exception as e:
        logger.error(str(e))
        return 1
    if 'result' in res:
        return 0 if res['result']['spam'] != 1 else -1
    else:
        return 1

