import requests, json, re
from pools.cgraphSPXMR import apiformating, starttime, homans
from pools.cgraphSPXMR import plots as cgraph
from stuff import msg0, msg1, msg2, msg3, stk4
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

## Edit they all are based on nodejs-pool project
# SupportXmr c3 and moneroocean are the same
# one is a fork of the other
# who cares?// i don't have to read
# more wierd js again! :}

statsheader = {
       'Connection': 'keep-alive',
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
       'Content-Type': 'application/json',
       'Accept': '*/*',
       'Origin': 'https://supportxmr.com',
       'Sec-Fetch-Site': 'same-site',
       'Sec-Fetch-Mode': 'cors',
       'Sec-Fetch-Dest': 'empty',
       'Referer': 'https://supportxmr.com/',
       'Accept-Language': 'en-US,en;q=0.9',
}

async def supportxmrpool(c,m,w,GRAPH=False):
    try:
       messg = await m.reply_text(msg2)
       stkr = await m.reply_sticker(stk4)
       stats = requests.get(f"https://supportxmr.com/api/miner/{w}/stats", headers=statsheader)
       if stats.status_code != 200:
          await stkr.delete()
          await messg.edit_text(msg1)
          print("http error\n\n", stats.text)
          return

       miners = requests.get(f"https://supportxmr.com/api/miner/{w}/chart/hashrate/allWorkers", headers=statsheader)
       payout = requests.get(f"https://supportxmr.com/api/user/{w}", headers=statsheader)
       stats  = json.loads(stats.text)
       payout = json.loads(payout.text)
       miners = json.loads(miners.text)
       if stats['totalHashes'] == 0:
          await stkr.delete()
          await messg.edit_text(msg0)
          return

       payout   = payout['msg']['payout_threshold']/1000000000000
       if GRAPH:
          data = apiformating(miners['global'], len(miners['global']), starttime())
          print(data)
          if not data:
             #GRAPH = False
             graph="pools/assets/no-data-graph.jpg"
             print('no graph')
          else: graph= cgraph(data,homans(data[0]['hsh']),m.from_user.id)

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
**Hashrare:** {homans(stats['hash'])}
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
