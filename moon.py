import requests, json, re, asyncio, time
from threading import Thread as thrd
from random import randint
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from stuff import *
from database import redis_connection
from pools.util.timef import timeinletters as timef
from pools.util.cgraph import homans
from pools.mo import mopool
from pools.c3 import c3pool
from pools.nano import nanopool
from pools.spxmr import supportxmrpool
from pools.minexmr import minexmrpool
from pools.p2pool import p2pool

db   = redis_connection()
moon = Client("moon_XD",
      api_id = app_id, api_hash = app_hash,
      bot_token = token)

usrWallets = {}
allWallets = {}
users      = {}
p2pusers   = {}

def bookup(task=""):
    if task == "startup":
       # restore dict from db
       usrwall = db.get('usrwall')
       allwall = db.get('allwall')
       usrs    = db.get('usrs')
       p2pusrs = db.get('p2pusrs')
       global usrWallets; global allWallets; global users; global p2pusers
       usrWallets = json.loads(usrwall, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})
       allWallets = json.loads(allwall, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})
       users      = json.loads(usrs, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})
       p2pusers   = json.loads(p2pusrs, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})
       print("restored backup")
       return
       # #copied from stackoverflow
       # that lambda converts json to py dict,
       # (json have str numbers, dict has int numbers)
       # without that thing output: {"12345678" : "4333aa*"}
       # With this thing output   : { 12345678  : "4333aa*"}

    usrwall = json.dumps(usrWallets)
    allwall = json.dumps(allWallets)
    usrs    = json.dumps(users)
    p2pusrs = json.dumps(p2pusers)
    db.set('usrwall', usrwall)
    db.set('allwall', allwall)
    db.set('usrs', usrs)
    db.set('p2pusrs', p2pusrs)
    print('backup done')

@moon.on_message(filters.command("start"))
async def start(client, message):
    name = getName(client, message)
    await message.reply_text(startMsg%name, reply_markup = keybd)
    await message.reply_sticker(stk5)
    if not message.from_user.id in users:
       users[message.from_user.id] = "[]"
       await logger(client, message, "New user!!!")
       print("user not in db, Added", message.from_user.id)
       bookup()

@moon.on_message(filters.command("help"))
async def help(client, message):
    name = getName(client, message)
    await message.reply_text(helpMsg%name, reply_markup = keybd, disable_web_page_preview=True)
    await message.reply_sticker(stk8)

@moon.on_message(filters.regex("thanks") or filters.regex("Thanks") or filters.regex("thank you") or filters.regex("Thank you"))
async def thank(client, message):
    ran = randint(0, 1)
    if ran == 1:
       await message.reply_text("**You are welcome**", reply_markup = keybd)
    else:
       await message.reply_text("**it's my duty**", reply_markup = keybd)
    await message.reply_sticker(stk7)
    await logger(client, message, logger3)

@moon.on_message(filters.regex("about"))
async def about(client, message):
    name = getName(client, message)
    await message.reply_text(aboutMsg%name, reply_markup = keybd, disable_web_page_preview=True)
    await message.reply_sticker(stk5)
    await logger(client, message, logger4)

@moon.on_message(filters.command("donate"))
async def donate(client, message):
    name = getName(client, message)
    button = InlineKeyboardMarkup([[InlineKeyboardButton("i dOnAtEd 💸 (just klik mE)", callback_data="donationnnnloooolllll")]])
    await message.reply_text(donateMsg%(donwallet, name), reply_markup =button, disable_web_page_preview=True)
    await message.reply_sticker(stk7)
    await logger(client, message, logger2)

@moon.on_message(filters.command("restart"))
async def restart(client, message):
    # use heroku api to restart
    if str(message.chat.id) == "800219239":
       await message.reply_text("**Hold tight restarting.....**")
       restartDyno()
       await message.reply_text("**Restarted?.....**")

@moon.on_message(filters.command("users"))
async def get(client, message): # cmd to check users growth
    if str(message.chat.id) == "800219239":
       m = await message.reply_text("Hold on!")
       total_users = len(users)
       print("total users:", total_users)
       await m.edit_text(f"Totalusers: {total_users}")

@moon.on_message(filters.command("getkey"))
async def getkey(client, message): # cmd to check if user used the bot
    if str(message.chat.id) == "800219239":
       m = await message.reply_text("Hold on!")
       key = message.text
       key = key.replace("/getkey ", "")
       if not key in users : await m.edit_text("User in db? use /get"); return
       await m.edit_text(f"User in db {key}")

@moon.on_message(filters.command("ping"))
async def main(client, message, GRAPH=False):
    if not message.from_user.id in usrWallets:
       await message.reply_text("**Sorry i don't have your wallet address** to fetch your mining stats, see /help")
       await message.reply_sticker(stk1)
       return

    try:
       w = usrWallets[message.from_user.id]['address']
       p = usrWallets[message.from_user.id]['pool']
    except Exception as e:
       await message.reply_text(msg0, str(e))
       await logger(client, message, f"got this error {str(e)}")
       return

    # every pool have a separate file
    # use pool var to call the right file
    print(w,p)
    if p == 'MO': await mopool(client,message,w,GRAPH)
    elif p == 'C3': await c3pool(client,message,w,GRAPH)
    elif p == 'NANO': await nanopool(client,message,w)
    elif p == 'SPXMR': await supportxmrpool(client,message,w,GRAPH)
    elif p == 'minexmr': await minexmrpool(client,message,w)
    elif p == 'p2pool': # the following check if user is in the p2p notify list
       if message.from_user.id in p2pusers:
          if p2pusers[message.from_user.id]['w'] == w and p2pusers[message.from_user.id]['p'] == p:
             await p2pool(client,message,w,NOTF='ON')
          else: await p2pool(client,message,w,NOTF='OFF')
       else: await p2pool(client,message,w,NOTF='OFF')
    elif p == 'minip2p':
       if message.from_user.id in p2pusers:
          if p2pusers[message.from_user.id]['w'] == w and p2pusers[message.from_user.id]['p'] == p:
             await p2pool(client,message,w,POOL='mini.',NOTF='ON')
          else: await p2pool(client,message,w,POOL='mini.',NOTF='OFF')
       else: await p2pool(client,message,w,POOL='mini.',NOTF='OFF')
    return
    # p2p list is used to notify users with share updates

@moon.on_message(filters.text)
async def wallet(client, message):
    # Bot logic
    # extracted/ported from moneroocean js regex
    Wpattern   = "^[4|8]{1}([A-Za-z0-9]{105}|[A-Za-z0-9]{94})$"
    # i did these, getting better with regex :-D
    SwitchPatt = "^[💰]{1}[4|8]{1}[A-Za-z0-9]{5}[*]{3}[A-Za-z0-9]{6}[\s]{1}[A-Za-z0-9]{,8}$"
    DelPatt    = "^[4|8]{1}[A-Za-z0-9]{5}[*]{3}[A-Za-z0-9]{6}[💰]{1}[\s]{1}[A-Za-z0-9]{,8}$"
    text       = message.text
    if message.reply_to_message:
       if message.reply_to_message.reply_markup:
          if isinstance(message.reply_to_message.reply_markup, ForceReply):
             if message.reply_to_message.reply_markup.placeholder == "Pool name?":
                msg  = "**Alright i forwarded your request** to my dev, he will look into it asap"
                dmsg = f"from: {getName(client,message)}\nid: {message.from_user.id}\n\nRequest: {text}"
                await client.send_message("Pine_Orange",dmsg)
                await message.reply_text(msg, quote=True)
                return

    if re.search(Wpattern, text):
       print("Valid Wallet!")
       try: allWallets[message.from_user.id]
       except KeyError: allWallets[message.from_user.id] = list()

       msg = "**Please select a pool from the supported list below**"
       await message.reply_text(msg, reply_to_message_id=message.message_id, reply_markup=pools)
       return


    if re.search(SwitchPatt, text):
       print("Craffted wallet!")
       tex1, tex2 = text.replace("💰", "").split("***")
       tex2, pool = tex2.split(" ")
       wallid = ''; pool = '';
       for i in allWallets[message.from_user.id]:
           if tex1 in i['address'] and tex2 in i['address'] and pool in i['pool']:
              wallid = i['address']; pool = i['pool']
              usrWallets[message.from_user.id] = {'address':wallid,'pool':pool}
              break
       if wallid == '' and pool == '':  msg = f"**I can't find this wallet address can you add it again?**"
       else: msg = f"**Alright switched your wallet**\n\nUsing Address: <code>{wallid}</code>\nPool: <code>{pool}</code>"
       await message.reply_text(msg, reply_markup = keybd)
       bookup()
       return

    if re.search(DelPatt, text.replace('🗑️', '')):
       print("Delete wallet req!")
       tex1, tex2 = text.replace("💰", "").replace("🗑️", "").split("***")
       tex2, pool = tex2.split(" ")
       for i in allWallets[message.from_user.id]:
           if tex1 in i['address'] and tex2 in i['address'] and pool in i['pool']:
              wallid = i['address']; pool = i['pool']
              allWallets[message.from_user.id].remove(i)
              if usrWallets[message.from_user.id] == i:
                 del usrWallets[message.from_user.id]
                 try: usrWallets[message.from_user.id] = allWallets[message.from_user.id][0]
                 except: pass
              break
       if pool == "p2pool" or pool == "minip2p":
          if message.from_user.id in p2pusers: del p2pusers[message.from_user.id]
       msg = f"**Alright removed your wallet**\nAddress: <code>{wallid}</code>\nPool: <code>{pool}</code>"
       await message.reply_text(msg, reply_markup = keybd)
       bookup()
       return

    if text.lower().replace("💰", "") == "wallet":
       keypad = []
       try:
           addrs = allWallets[message.from_user.id]
       except KeyError:
           await message.reply_text("**Sorry i don't have any of your wallet addresses**, see /help")
           await message.reply_sticker(stk1)
           return

       for i in addrs:
           tex = "💰" + i['address'][:6] + "***" + i['address'][-6:] + " " + i['pool']
           keypad.append([tex])
       keypad.append(["🗑️Delete💰", "<<back>>"])
       await message.reply_text("**Select Wallet to switch to**", reply_markup=ReplyKeyboardMarkup(keypad, resize_keyboard=True))
       return

    if text.lower().replace("📬", "").replace("📜","") == "ping":
       await main(client, message)
       return

    if text.lower().replace("🗑️", "").replace("💰","") == "delete":
       keypad = []
       try: addrs = allWallets[message.from_user.id]
       except KeyError:
           await message.reply_text("**Huh?, there's nothing to delete**", reply_markup = keybd)
           await message.reply_sticker(stk1)
           return

       for i in addrs:
           tex = "🗑️" + i['address'][:6] + "***" + i['address'][-6:] + "💰" + " " + i['pool']
           keypad.append([tex])
       keypad.append(["<<back>>"])
       msg = "**Select a wallet address to delete 🗑️ it**"
       await message.reply_text(msg, reply_markup=ReplyKeyboardMarkup(keypad, resize_keyboard=True))
       bookup()
       return

    if text.lower().replace("<", "").replace(">", "") == "back":
       await message.reply_text("**Hello fellow miner,**\n What do you wanna do?", reply_markup = keybd)
       return
    if text == "⁉️Help":
       await help(client, message)
       return
    if text == "😊Thanks":
       await thank(client, message)
       return
    if text == "👀Who?":
       await about(client, message)
       return
    if text == "💸Donate❤️":
       await donate(client, message)
       return
    if text.lower().replace("/", "") == "sauce":
       await message.reply_text(sauce)
       await message.reply_sticker(stk7)
       return


@moon.on_callback_query()
async def calls(client, message):
    data = message.data
    if "donationnnnloooolllll" in data:
       await message.answer("❤️❤️Thank you kind Miner")
       await message.message.reply_sticker(stk9)
       await message.message.reply_sticker(stk10)
       await message.message.reply_sticker(stk11)
       await message.message.reply_sticker(stk12)
       return

    if "PINGME" in data:
       # dirty way faking the messeage id
       # technically the bot is the sender
       # we patch the sender id with the user'sID
       # i'm too lazy to use effective.from_user
       # this works fine.
       await message.answer()
       message.message.from_user.id =  message.message.chat.id
       await message.message.delete() #delete old data
       if data == "PINGMEWITHGRAPH": await main(client, message.message, True)
       else: await main(client, message.message, False) #fetch new data
       return

    if "NOTIFYME" in data:
       message.message.from_user.id =  message.message.chat.id
       try:
          w = usrWallets[message.message.from_user.id]['address']
          p = usrWallets[message.message.from_user.id]['pool']
       except Exception as e:
          await message.message.reply_text(msg0 + " <code>" + str(e) + "</code>")
          await logger(client, message.message, f"got this error {str(e)}")
          return

       print(p,w)
       if p != "p2pool" and p != "minip2p":
          msg = "**This feature is for P2pool and Minip2pool only send me your wallet address if you're using p2pool**"
          await message.message.reply_text(msg)
          await message.answer()
          return

       if "OFF" in data and message.message.from_user.id in p2pusers:
          del p2pusers[message.message.from_user.id]
          button = InlineKeyboardMarkup([[InlineKeyboardButton("📬 PING", callback_data="PINGME")], [InlineKeyboardButton(f"📳 Notify me OFF", callback_data="NOTIFYME")]])
          msg = f"**Alright Notifications Disabled\n\nPlease note this is still under beta,**\nplease report any bugs/feedback you have\n\nWallet: <code>{w}</code>\nPool: <code>{p}</code>"
          await message.message.edit_reply_markup(button)
          await message.message.reply_text(msg)
          await message.answer('Notifications Disabled!')
          bookup()
          return

       p2pusers[message.message.from_user.id] = {'p': p, 'w': w}
       button = InlineKeyboardMarkup([[InlineKeyboardButton("📬 PING", callback_data="PINGME")], [InlineKeyboardButton(f"📳 Notify me ON", callback_data="NOTIFYME")]])
       msg = f"**Alright, you will be notified once you make a share\n\nPlease note this is still under beta,**\nFor now you can get notifications for one address only, i may add support for multi addresses\nplease report any bugs/feedback you have\n\nWallet: `{w}`\nPool: `{p}`"
       await message.message.edit_reply_markup(button)
       await message.message.reply_text(msg)
       await message.answer('Notifications Enabled!')
       bookup()
       return

    if "pool" in data:
       _,pool = data.split("|")
       if pool == "report":
          msg = "**Alright you can suggest a pool, my dev will try adding it**\n\n**Notes:** The pool should have a public api\nReply the pool name and domain name, also provide any additional details, Or you can ignore this message and directly pm my dev @_xd2222 or @Pine_Orange"
          await message.message.delete()
          msgg = await message.message.reply_text(msg, reply_to_message_id=message.message.reply_to_message_id,reply_markup=ForceReply(True, "Pool name?"))
          return

       msgid = message.message.reply_to_message.message_id
       walletADR = (await client.get_messages(message.message.chat.id, msgid)).text
       message.message.from_user.id =  message.message.chat.id
       print(msgid, walletADR, pool, "id: ", message.message.from_user.id)
       if not re.search("^[4|8]{1}([A-Za-z0-9]{105}|[A-Za-z0-9]{94})$", walletADR):
          await message.answer("Your wallet address is wrong")
          await message.message.delete()
          return

       for i in allWallets[message.message.from_user.id]:
           if walletADR  in i['address'] and pool in i['pool']:
              msg = "**I already saved this address with same pool** you can switch to it, use 💰Wallet button"
              await message.message.edit_text(msg, reply_markup = keybd)
              await message.message.reply_sticker(stk2)
              return

       await message.answer('wallet saved!')
       usrWallets[message.message.from_user.id] = {'address':walletADR,'pool':pool}
       allWallets[message.message.from_user.id].append({'address':walletADR,'pool':pool})
       msg = ''
       if pool == 'minexmr':
          msg += """
**🔴🔴🔴⚠️ATTENTION⚠️🔴🔴🔴
MINEXMR users you need to switch to another pool ASAP,
As minexmr hashrate is very high nearly [50% of the network,](https://miningpoolstats.stream/monero)
If it reaches 51% xmr might be at risk [full details here,](https://www.investopedia.com/terms/1/51-attack.asp)
High hashrate doesn't mean more profits, you may lose all your xmr!!!!
🔴🔴🔴⚠️ATTENTION⚠️🔴🔴🔴
**\n\n\n\n"""
       msg += f"**I saved your wallet** you can start using me now 👍 try the buttons\n\nYour Address: <code>{walletADR}</code>\nPool: <code>{pool}</code>"
       await message.message.edit_text(msg, reply_markup = keybd)
       bookup()
       return


def getName(client, message):
    user_id  = message.from_user.id
    username = "@" + message.from_user.username
    frname   = message.from_user.first_name
    lasname  = message.from_user.last_name
    name     = ""

    if username != "None":
       name = username
    elif frname != "None":
       name = frname
    elif username == "None" and frname == "None":
       name = str(user_id)
    return name

async def logger(client, message, msg, text=""):
    # keep track of bot errors/growth
    if not logGroup: return
    ms = msg + text + f"\n\n{message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username} {message.from_user.id}"
    await client.send_message(logGroup, ms, disable_web_page_preview=True)

async def pushNOTFI():
    if not pushNOTIFICATIONS: return
    if not logGroup: return
    print('starting push notifications service')
    await asyncio.sleep(5) # wait for client to start
    await moon.send_message(logGroup,"**Started push Notifications service**")
    p2ptime  = time.time()
    minitime = time.time() + 90
    xmrbeast = time.time() + 120
    lwon  = ''      # last winner
    xsent = 0       # how much we alerted the winner
    lasth = 0       # last height is the last share from the previous request
    nshare = 20     # number of shares to fetch, 20 on first run
    mlasth = 0; mnshare = 20; # for minip2p
    while 1: # the most accurate timer ever no sleep no async.sleep no shit
       try:
        if int(time.time()) - int(p2ptime) >= 80: # use unix time to check how much time passed
           if len(p2pusers) == 0: continue
           print('new req with', nshare, lasth)
           shares  = requests.get(f'https://p2pool.observer/api/shares?limit={nshare}', headers=p2pheaders)
           shares  = json.loads(shares.text)
           nshares = []; index = None
           if lasth == 0:                                # if this is first run
              print('first run')
              lasth=shares[0]['height']; nshares=shares; # treat all shares as new
           else:
              for i in shares:               # search for last height
                  if i['height'] == lasth:   # get index
                     index = shares.index(i) # use index to get only new shares
                     break                   # BREAK FOR NOT WHILE
           if not index and nshares == []:
              print('not found', lasth)
              if nshare >= 650:
                 print('giving up', lasth)
                 ttt = json.dumps(shares)
                 test = 'is lasth there? : ' + str(str(lasth) in ttt)
                 print(test)
                 debug = open('debug.txt', 'w')
                 debug.write(ttt)
                 debug.close()
                 await moon.send_message(logGroup, f"**Attention!**\nLASTH NOT FOUND {lasth}\nTest: {test}")
                 await moon.send_document(logGroup, 'debug.txt')
                 nshares = shares
              else:
                 nshare += 150            # if we didn't find last height that means
                 print('trying again.. ', nshare)
                 await asyncio.sleep(1)
                 continue                 # we missed a lot of shared get last 100+ shares
           elif index == 0: continue      # last height is still the last height continue
           else: nshares = shares[:index] # new shares after last height we checked
           nshares.sort(reverse=False, key=lambda d:d['height']) # sort height from old to new
           print('new shares:', len(nshares), 'index: ', index)
           userids = list(p2pusers.keys())
           for i in nshares:
             for ii in userids:
               if i['miner'] == p2pusers[ii]['w'] and p2pusers[ii]['p'] == 'p2pool':
                  u = ii
                  a = "💰" + i['miner'][:6] + "&ast;&ast;&ast;" + i['miner'][-6:] + " p2pool"
                  h = i['height']
                  r = i['coinbase']['reward']/1000000000000
                  c = i['coinbase']['id']+"/"+i['miner']+"/"+i['coinbase']['private_key']
                  d = int(i['difficulty'], 16)
                  t = timef(i['timestamp'])
                  id= i['id']
                  msg = f"""
**YOU Just found a SHARE!!**\n
**Time:** {t}
**Height:** <a href="https://p2pool.observer/share/{id}">{h}</a>
**Difficulty:** {d}
**Reward:** <a href="https://www.exploremonero.com/receipt/{c}">{r}</a> XMR
"""
                  if i['main']['found']: msg += f"**Shared in Mainchain!**\n**Block:**{i['main']['height']}"
                  msg += f"**Address:** <code>{a}</code>"
                  msg += "\n\nYou can stop this alerts by switching to the address above and turnoff NotifyMe"
                  msg += "\nThis feature is under beta if you think there was a mistake please report see /help"
                  await moon.send_message(u, msg, disable_web_page_preview=True)
           lasth = nshares[-1]['height']; nshare = 50; # last item is the newest height
           p2ptime = time.time()
           continue
        elif int(time.time()) - int(minitime) >= 80: # minip2p
           if len(p2pusers) == 0: continue
           print('new mini req with', mnshare, mlasth)
           shares  = requests.get(f'https://mini.p2pool.observer/api/shares?limit={mnshare}', headers=p2pheaders)
           shares  = json.loads(shares.text)
           mnshares  = []; index   = None
           if mlasth == 0:                                 # if this is first run
              print('first run')
              mlasth=shares[0]['height']; mnshares=shares; # treat all shares as new
           else:
              for i in shares:               # search for last height
                  if i['height'] == mlasth:  # get index
                     index = shares.index(i) # use index to get only new shares
                     break                   # BREAK FOR NOT WHILE
           if not index and mnshares == []:
              print('not found', mlasth)
              if mnshare >= 650:
                 print('giving up', mlasth)
                 ttt = json.dumps(shares)
                 test = 'is mlasth there? : ' + str(str(mlasth) in ttt)
                 print(test)
                 debug = open('debugMINI.txt', 'w')
                 debug.write(ttt)
                 debug.close()
                 await moon.send_message(logGroup, f"**Attention!**\nmLASTH NOT FOUND {mlasth}\nTest: {test}")
                 await moon.send_document(logGroup, 'debugMINI.txt')
                 mnshares = shares
              else:
                 mnshare += 150      # if we didn't find last height that means
                 print('trying again.. ', mnshare)
                 await asyncio.sleep(1)
                 continue            # we missed a lot of shared get last 100+ shares
           elif index == 0: continue # last height is still the last height continue
           else: mnshares = shares[:index] # new shares after last height we checked
           mnshares.sort(reverse=False, key=lambda d:d['height']) # sort height from old to new
           print('new mini shares:', len(mnshares), 'index: ', index)
           userids = list(p2pusers.keys())
           for i in mnshares:
             for ii in userids:
               if i['miner'] == p2pusers[ii]['w'] and p2pusers[ii]['p'] == 'minip2p':
                  u = ii
                  a = "💰" + i['miner'][:6] + "&ast;&ast;&ast;" + i['miner'][-6:] + " minip2p"
                  h = i['height']
                  r = i['coinbase']['reward']/1000000000000
                  c = i['coinbase']['id']+"/"+i['miner']+"/"+i['coinbase']['private_key']
                  d = int(i['difficulty'], 16)
                  t = timef(i['timestamp'])
                  id= i['id']
                  msg = f"""
**YOU Just found a SHARE!!**\n
**Time:** {t}
**Height:** <a href="https://mini.p2pool.observer/share/{id}">{h}</a>
**Difficulty:** {d}
**Reward:** <a href="https://www.exploremonero.com/receipt/{c}">{r}</a> XMR
"""
                  if i['main']['found']: msg += f"**Shared in Mainchain!**\n**Block:**{i['main']['height']}"
                  msg += f"**Address:** <code>{a}</code>"
                  msg += "\n\nYou can stop this alerts by switching to the address above and turnoff NotifyMe"
                  msg += "\nThis feature is under beta if you think there was a mistake please report see /help"
                  await moon.send_message(u, msg, disable_web_page_preview=True)
           mlasth = mnshares[-1]['height']; mnshare = 50; # last item is the newest height
           minitime = time.time()
           continue
        elif int(time.time()) - int(xmrbeast) >= 150:
           print('new xmrvsbeast req')
           raffel  = requests.get(f'https://xmrvsbeast.com/p2pool/stats')
           raffel  = json.loads(raffel.text.replace("`",'')) # someting is wrong with xmrvsbeast json it has a '`'
           winer   = raffel['winner']
           if winer in lwon:
              if int(lwon.split("|")[1]) >= 2:
                 print("xmrvsbeast sent twice moving on")
                 xmrbeast = time.time()
                 continue
           else: xsent = 0
           w1, w2  = winer.split('...')
           for i in allWallets:
               for ii in allWallets[i]:
                   if w1 in ii['address'] and w2 in ii['address']:
                      wallet  = ii['address']
                      user    = i
                      rtime    = raffel['time_remain']
                      hashes  = homans(raffel['bonus_hr'] + raffel['donate_hr'])
                      miners  = raffel['players']
                      msg     = f"""
**YOU WON XMRVSBEAST BONUS HR RAFFLE!**

**Time Remaining:** {rtime} min
**Bonus Hashrate:** {hashes}
**Mining Players:** {miners}
[<b>xmrvsbeast.com/p2pool/</b>](https://xmrvsbeast.com/p2pool/)

**Winer Address:** {winer}
**Your Address:** {wallet}
**Pool:** {ii['pool']}

**This Feature is under beta,**
Please report if you think there was a mistake!
See /help
"""
                      await moon.send_message(user, msg, disable_web_page_preview=True)
                      xsent += 1
           timetowait = raffel['time_remain']*60 # wait for the remaining time
           if timetowait >= 2400: timetowait = 0 # instead of spamming the api
           print('next xmrvsbeast req in:', timetowait)
           xmrbeast = time.time() + timetowait   # don't wait if <40min tho
           lwon     = f"{winer} |{xsent}"  # don't notfiy people twice!
           continue
        else:
           await asyncio.sleep(1) # sleep to slow down if checks every cpu cycle
           continue
       except requests.exceptions.ConnectionError:
          await asyncio.sleep(2) # for any http errors ignore them
          continue
       except Exception as eeeror:
          print("[ERROR]\n\n", eeeror)
          if logGroup: await moon.send_message(logGroup, f"**  ERROR  **\n\n<code>{eeeror}</code>")
          continue

def runasync(): # run thread in asyncio loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(pushNOTFI())

bookup("startup")
tsk = thrd(target=runasync)
tsk.daemon=True
tsk.start()
moon.run()
