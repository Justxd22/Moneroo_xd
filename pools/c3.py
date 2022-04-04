import requests, json, re
from pools.cgraph import apiformating, starttime, homans
from pools.cgraph import plots as cgraph
from stuff import msg0, msg1, msg2, msg3,  stk4
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# c3 and moneroocean are the same
# one is a fork of the other
# who cares?// i don't have to read
# more wierd js again :}

statsheader = {
       'Connection': 'keep-alive',
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
       'Content-Type': 'application/json',
       'Accept': '*/*',
       'Origin': 'https://api.c3pool.com',
       'Sec-Fetch-Site': 'same-site',
       'Sec-Fetch-Mode': 'cors',
       'Sec-Fetch-Dest': 'empty',
       'Referer': 'https://api.c3pool.com/',
       'Accept-Language': 'en-US,en;q=0.9',
}

async def c3pool(c,m,w,GRAPH=False):
    try:
       messg = await m.reply_text(msg2)
       stkr = await m.reply_sticker(stk4)
       stats = requests.get(f"https://api.c3pool.com/miner/{w}/stats", headers=statsheader)
       if stats.status_code != 200:
          await stkr.delete()
          await messg.edit_text(msg1)
          print("http error\n\n", stats.text)
          return

       payout = requests.get(f"https://api.c3pool.com/user/{w}", headers=statsheader)
       miners = requests.get(f"https://api.c3pool.com/miner/{w}/chart/hashrate/allWorkers", headers=statsheader)
       stats  = json.loads(stats.text)
       payout = json.loads(payout.text)
       miners = json.loads(miners.text)
       if not stats['lastHash']:
          await stkr.delete()
          await messg.edit_text(msg0)
          return
       payout = payout['payout_threshold']/1000000000000
       if GRAPH:
          data = apiformating(miners['global'], len(miners['global']), starttime())
          if not data:
             #GRAPH = False
             graph="pools/assets/no-data-graph.jpg"
             print('no graph')
          else: graph= cgraph(data,homans(data[0]['hsh2']),homans(data[0]['hsh']),m.from_user.id)

       totalMiners = len(miners)-1 # api always gives a total item contains all miners combined
       paidamt     = 0.0
       xmrmined    = format(stats['amtDue']/1000000000000, '.12f')
       progress    = round(float(xmrmined) * 100 / payout, 2)
       print(payout)
       if stats['amtPaid'] != 0: paidamt = format(stats['amtPaid']/1000000000000, '.12f')
       minersName = []
       for i in range(len(miners)):
           if i==0: continue;
           minersName.append(list(miners.keys())[i])
       if len(minersName) ==0: minersName = 'No miners Alive'
       else: minersName = ", ".join(minersName)

       if GRAPH: button = InlineKeyboardMarkup([[InlineKeyboardButton("📬 PING", callback_data="PINGMEWITHGRAPH")]])
       else: button = InlineKeyboardMarkup([[InlineKeyboardButton("📬 PING", callback_data="PINGME")], [InlineKeyboardButton("📈 GRAPH", callback_data="PINGMEWITHGRAPH")]])

    except Exception as e:
       await stkr.delete()
       await messg.edit_text(msg3, str(e))
      #  await logger(c, m, f"got this error {str(e)}")
       return
    msg = f"""
**Miners:** {totalMiners} workers
**Workers:** {minersName}
**Pay hashrate:** {homans(stats['hash2'])}
**Raw hashrare:** {homans(stats['hash'])}
**Shares:** {stats['validShares']}
**Rejected Shares:** {stats['invalidShares']}
**XMR mined:** {xmrmined} XMR {progress}% done
**Paid XMR:** {paidamt} XMR"""
    await stkr.delete()
    if GRAPH:
       await messg.delete()
       await m.reply_photo(graph,caption=msg,reply_markup=button)
       #os.remove(graph)
    else: await messg.edit_text(msg, reply_markup = button)
