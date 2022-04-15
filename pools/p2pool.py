import requests, json, re
from pools.util.timef import timeinletters as timef
from pools.util.cgraph import homans
from stuff import msg0, msg1, msg2, msg3,  stk4
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Thanks to github.com/WeebDataHoarder api
# adding p2pool/minip2pool is posible (with php pain)

# im using headers cuz im afraid i might get rate-limiting
# these are copied from chrome im not sure if cors are required whatever
headers = {
       'Connection': 'keep-alive',
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
       'authority': 'p2pool.observer',
       'cache-control': 'max-age=0',
       'Content-Type': 'application/json',
       'Accept': '*/*',
       'Origin': 'https://p2pool.observer',
       'Sec-Fetch-Site': 'same-site',
       'Sec-Fetch-Mode': 'cors',
       'Sec-Fetch-Dest': 'empty',
       'Accept-Language': 'en-US,en;q=0.9'}

# the following is the result of pain in ass php porting
# idk anything about php i managed this port aftr hundreds of
# searches and stackoverflows and r/php, r/learnpython
# idk why people still use php, AND WHY THE WIERD HEX FORMATS??
# enjoy!
# this works for both mini/normal p2p pool
async def p2pool(c,m,w,POOL='',NOTF="OFF"):
    try:
       messg = await m.reply_text(msg2)
       stkr = await m.reply_sticker(stk4)
       poolstats = requests.get(f"https://{POOL}p2pool.observer/api/pool_info", headers=headers)
       minerstats= requests.get(f"https://{POOL}p2pool.observer/api/miner_info/{w}", headers=headers)
       payout    = requests.get(f"https://{POOL}p2pool.observer/api/payouts/{w}", headers=headers)

       if poolstats.status_code != 200:
          await stkr.delete()
          await messg.edit_text(msg1)
          print("http error\n\n", stats.text)
          return

       poolstats  = json.loads(poolstats.text)
       minerstats = json.loads(minerstats.text)
       payout     = json.loads(payout.text)
       windowsize = 2160 * 4 # constant copied from php code
       sheight    = poolstats['sidechain']['height'] # this request is made after getting the current height
       windowsh   = requests.get(f"https://{POOL}p2pool.observer/api/shares_in_window/{w}?from={sheight}&window={windowsize}", headers=headers)
       windowsh   = json.loads(windowsh.text)
       sharesInwind = 0
       unclesInwind = 0
       window_diff  = 0
       tip          = sheight
       wend         = tip - 2160
       # get only shares made in current window
       for i in range(len(windowsh)):
          if 'parent' in windowsh[i]:
             if windowsh[i]['height'] > wend:
                unclesInwind +=1
                window_diff   = window_diff + windowsh[i]['weight']
          else:
             if windowsh[i]['height'] > wend:
                sharesInwind +=1
                window_diff   = window_diff + windowsh[i]['weight']
       # these come in hex format i spent hours trying to figure this
       pdiff   = int(poolstats['sidechain']['difficulty'],16)
       pweight = int(poolstats['sidechain']['window']['weight'],16)
       btime   = poolstats['sidechain']['block_time']
       hashes  = homans(window_diff / pweight * (pdiff/btime))
       pshares = round((window_diff / pweight * 100),3)
       pminers = str(poolstats['sidechain']['miners']) + " miners online"
       beffort = str(poolstats['sidechain']['effort']['current']) + "% **avg** " + str(poolstats['sidechain']['effort']['average']) + "%"
       shares  = str(minerstats['shares']['blocks']) + " **uncles:** " + str(minerstats['shares']['uncles'])
       wshares = str(sharesInwind) + " **uncles:** " + str(unclesInwind)
       lshare  = timef(minerstats['last_share_timestamp']) #custom made time formating
       lpay    = timef(payout[0]['timestamp'])
       lxmr    = payout[0]['coinbase']['reward']/1000000000000 #standard xmr length
       poolname= 'P2pool' if not POOL else "Minip2pool"

    except Exception as e:
       await stkr.delete()         # wrapped in <code> for easy copying
       await messg.edit_text(msg3 + " <code>" + str(e) + "</code>")
       #await logger(c, m, f"got this error {str(e)}")
       return
    msg = f"""
**{poolname} Miners:** {pminers}
**Block effort :** {beffort}
**Hashrate:** {hashes}
**Shares:** {shares}
**Shares in PPLNS:** {wshares}
**Pool share:** {pshares}%
**Last Share:** {lshare}
**Last Payout:** {lpay}
**Last XMR:** {lxmr} XMR"""
    await stkr.delete()
    button = InlineKeyboardMarkup([[InlineKeyboardButton("📬 PING", callback_data="PINGME")], [InlineKeyboardButton(f"📳 Notify me {NOTF}", callback_data=f"{'NOTIFYME' if NOTF == 'OFF' else 'NOTIFYME | OFF'}")]])
    await messg.edit_text(msg, reply_markup = button)
