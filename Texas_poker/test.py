import time

import requests

dic = {}
for i in range(4):
    res = requests.get('http://127.0.0.1:5000/join_game').json()
    dic[i] = res['ID']
    print(res['content'])
while True:
    time.sleep(1)
    for i in dic:
        requests.get(f'http://127.0.0.1:5000/ingame/{dic[i]}/2')
        c = requests.get(f'http://127.0.0.1:5000/ingame/{dic[i]}')
        print(c.text)

