import requests, json, re, os
from pools.util.cgraph import apiformating, starttime, homans
from pools.util.cgraph import plots as cgraph
from stuff  import msg0, msg1, msg2, msg3, stk4
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


statsheader = {
       'Connection': 'keep-alive',
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
       'Content-Type': 'application/json',
       'Accept': '*/*',
       'Origin': 'https://moneroocean.stream',
       'Sec-Fetch-Site': 'same-site',
       'Sec-Fetch-Mode': 'cors',
       'Sec-Fetch-Dest': 'empty',
       'Referer': 'https://moneroocean.stream/',
       'Accept-Language': 'en-US,en;q=0.9',
}

async def mopool(client, message, wallet, GRAPH=False):
   try:
       messg = await message.reply_text(msg2)
       stkr = await message.reply_sticker(stk4)
       stats = requests.get(f"https://api.moneroocean.stream/miner/{wallet}/stats", headers=statsheader)
       if stats.status_code != 200:
          await stkr.delete()
          await messg.edit_text(msg1)
          print("http error\n\n", stats.text)
          return

       payout   = requests.get(f"https://api.moneroocean.stream/user/{wallet}", headers=statsheader)
       miners   = requests.get(f"https://api.moneroocean.stream/miner/{wallet}/chart/hashrate/allWorkers", headers=statsheader)
       stats    = json.loads(stats.text)
       payout   = json.loads(payout.text)
       miners   = json.loads(miners.text)
       print(stats)
       if not stats['lastHash']:
          await stkr.delete()
          await messg.edit_text(msg0)
          return

       payout   = payout['payout_threshold']/1000000000000
       if GRAPH:
          data = apiformating(miners['global'], len(miners['global']), starttime())
          if not data:
             #GRAPH = False
             graph="pools/assets/no-data-graph.jpg"
             print('no graph')
          else: graph= cgraph(data,homans(data[0]['hsh2']),homans(data[0]['hsh']),message.from_user.id)
          print('graph done!')

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
       await messg.edit_text(msg3 + " <code>" + str(e) + "</code>")
       await stkr.delete()
      #  await logger(client, message, f"got this error {str(e)}")
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
      await message.reply_photo(graph,caption=msg,reply_markup=button)
      #os.remove(graph)
   else: await messg.edit_text(msg, reply_markup = button)
