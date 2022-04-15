import json, requests, time
from pools.util.cgraph import homans
from stuff  import msg0, msg1, msg2, msg3, stk4
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

headers = {
     'authority': 'minexmr.com',
     'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
     'accept': '*/*',
     'sec-fetch-site': 'same-origin',
     'sec-fetch-mode': 'cors',
     'sec-fetch-dest': 'empty',
     'referer': 'https://minexmr.com/dashboard/',
     'accept-language': 'en'
}

async def minexmrpool(c,m,w):
    messg = await m.reply_text(msg2)
    stkr = await m.reply_sticker(stk4)

    try:
        stats1 = requests.get(f"https://minexmr.com/api/main/user/stats?address={w}", headers=headers)
        stats2 = requests.get(f"https://minexmr.com/api/main/user/workers?address={w}", headers=headers)
        if stats1.status_code != 200 or stats2.status_code != 200:
          await stkr.delete()
          await messg.edit_text(msg1 + f" Http code: {stats1.status_code} {stats2.status_code} MINEXMR POOL")
          print("http error\n\n", stats1.text, stats2.text)
          return

        data1 = json.loads(stats1.text)
        data2 = json.loads(stats2.text)
        aliveM   = 0
        deadM    = 0
        hashrate = 0
        workersA  = []
        workersD  = []
        workersn = ""
        lworkers = len(data2)

        for i in range(lworkers):
           if data2[i]['hashrate'] == 0:
              deadM += 1
           else:
              aliveM +=1
              hashrate += data2[i]['hashrate']

        if lworkers==0: workersn = 'No miners Alive'
        else: workersn = "no names -_-"

        hashrate = homans(hashrate)
        xmrmined = format(int(data1['balance'])/1000000000000, '.12f')
        xmrpaid  = "0" if not data1['paid'] else format(int(data1['paid'])/1000000000000, '.12f')
        payout   = data1['thold']/1000000000000
        progress = round(float(xmrmined) * 100 / payout, 2)
        hashes   = int(data2[0]['hashes'])
        invalid  = data2[0]['invalid'] + " " + str(round(int(data2[0]['invalid']) * 100/hashes,4)) + "% of total hashes"
        expired  = data2[0]['expired'] + " " + str(round(int(data2[0]['expired']) * 100/hashes,4)) + "% of total hashes"

    except Exception as e:
        await stkr.delete()
        await messg.edit_text(msg3 + "\n\n<code>" + str(e) + "</code>")
        #await logger(c, m, f"got this error {str(e)}")
        return

    msg = f"""
**Miners**: {aliveM} on {deadM} ded
**Workers**: {workersn}
**hashrate**: {hashrate}
**Total hashes**: {hashes}
**Invalid**: {invalid}
**Expired**: {expired}
**XMR mined**: {xmrmined} XMR {progress}% Done
**XMR payed**: {xmrpaid} XMR
    """
    button = InlineKeyboardMarkup([[InlineKeyboardButton("📬 PING", callback_data="PINGME")]])
    await stkr.delete()
    await messg.edit_text(msg, reply_markup = button, disable_web_page_preview=True)
