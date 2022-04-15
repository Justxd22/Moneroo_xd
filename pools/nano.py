import json, requests, time
from pools.util.cgraph import homans
from stuff  import msg0, msg1, msg2, stk4
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


headers = {
     'authority': 'xmr.nanopool.org',
     'accept': 'application/json, text/javascript, */*; q=0.01',
     'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
     'x-requested-with': 'XMLHttpRequest',
     'sec-fetch-site': 'same-origin',
     'sec-fetch-mode': 'cors',
     'sec-fetch-dest': 'empty',
     'referer': 'https://xmr.nanopool.org/',
     'accept-language': 'en'
}


async def nanopool(c,m,w):
    messg = await m.reply_text(msg2)
    stkr = await m.reply_sticker(stk4)

    try:
       # fetch json
       # For some reason they have two outputs form thier api user/load_account
       # some data is more accurate in load_account like the balance so i will use both
       stats1 = requests.get(f"https://xmr.nanopool.org/api/v1/user/{w}", headers=headers)
       stats2 = requests.get(f"https://xmr.nanopool.org/api/v1/load_account/{w}", headers=headers)
       if stats1.status_code != 200 or stats2.status_code != 200:
          await stkr.delete()
          await messg.edit_text(msg1 + f" Http code: {stats1.status_code} {stats2.status_code} NANO POOL")
          print("http error\n\n", stats1.text, stats2.text)
          return

#       print(stats.text)
       data1    = json.loads(stats1.text)['data']
       data2    = json.loads(stats2.text)['data']['userParams']
       data3    = json.loads(stats2.text)['data']
       lworkers = len(data1['workers'])
       aliveM   = 0
       deadM    = 0
       workersA  = []
       workersD  = []
       workersn = ""

       for i in range(lworkers):
#           workers.append(data['workers'][i]['id'])
           if data1['workers'][i]['hashrate'] == '0.0':
              deadM += 1; workersD.append(data1['workers'][i]['id'])
           else: aliveM +=1 ; workersA.append(data1['workers'][i]['id'])

       if lworkers==0: workersn = 'No miners Alive'
       else:
           if len(workersD) != 0:
              workersn = ", ".join(workersA) + " **" + ", ".join(workersD) + " IS DED**"
           else: workersn = ", ".join(workersA)

       minersText = f"{lworkers} workers"
       if deadM != 0: minersText += f" {aliveM} on, {deadM} ded"
       curhashr = homans(float(data2['hashrate']))
       h1 = homans(float(data1['avgHashrate']['h1'])) # avg hs in 1 hour
       h3 = homans(float(data1['avgHashrate']['h3'])) # avg hs in 3 hour
       h6 = homans(float(data1['avgHashrate']['h6'])) # avg hs in 6 hour
       h12 = homans(float(data1['avgHashrate']['h12'])) # avg hs in 12 hour
       h24 = homans(float(data1['avgHashrate']['h24'])) # avg hs in 24 hour


       xmrmined = str(data2['balance'])[:12]
       xmrUnCon = str(data2['balance_unconfirmed'])[:12]
       totalxmr = data2['e_sum']
       payments = data2['e_count']
       minPay   = data2['min_payout']
       progress = round(float(xmrmined) * 100 / minPay, 2)
       # get shares in last hour by searching for the closest value to last hour if we did calculte the time right
       lastHour = round(time.time() - 7200) * 1000 /3600000 # don't ask me they use wierd time formating-_-
       print(lastHour)
       Shistory = data3['shareRateHistory']
       index    = min(range(len(Shistory)), key=lambda i: abs(Shistory[i]['hour']-lastHour))
       shares   = Shistory[index]['sum']

    except Exception as e:
       await stkr.delete()
       await messg.edit_text(msg3 + " <code>" + str(e) + "</code>")
      #  await logger(c, m, f"got this error {str(e)}")
       return

    msg = f"""
**Miners**: {minersText}
**Workers**: {workersn}
**hashrate**: {curhashr}
**avg hashrare last hour**: {h1}
**avg hashrare last 12h**: {h12}
**Shares last hour**: {shares}
**XMR mined**: {xmrmined} XMR {progress}% Done
**UNConfirmed XMR**: {xmrUnCon} XMR
**XMR**: {totalxmr} XMR
**Payments made**: {payments}
    """
    button = InlineKeyboardMarkup([[InlineKeyboardButton("📬 PING", callback_data="PINGME")]])
    await stkr.delete()
    await messg.edit_text(msg, reply_markup = button, disable_web_page_preview=True)

