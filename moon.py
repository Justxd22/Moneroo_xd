import requests, json, re
from random import randint
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from stuff import *
from database import redis_connection
from pools.mo import mopool
from pools.c3 import c3pool
from pools.nano import nanopool
from pools.spxmr import supportxmrpool
from pools.minexmr import minexmrpool

db = redis_connection()

moon = Client("moon_XD",
      api_id = app_id, api_hash = app_hash,
      bot_token = token)

usrWallets = {}
allWallets = {}
users = {}

def bookup(task=""):
    if task == "startup":
       #restore dict from db
       usrwall = db.get('usrwall')
       allwall = db.get('allwall')
       usrs = db.get('usrs')
       global usrWallets; global allWallets; global users;
       usrWallets = json.loads(usrwall, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})
       allWallets = json.loads(allwall, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})
       users      = json.loads(usrs, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})
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
    db.set('usrwall', usrwall)
    db.set('allwall', allwall)
    db.set('usrs', usrs)
    print('backup done')

@moon.on_message(filters.command("start"))
async def start(client, message):
    name = getName(client, message)
    await message.reply_text(startMsg%name, reply_markup = keybd)
    await message.reply_sticker(stk5)

    if not message.from_user.id in users:
        users[message.from_user.id] = "[]"
        print("user not in db, Added", message.from_user.id);
        await logger(client, message, "New user!!!")
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
    return



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
                print(message)
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
       for i in allWallets[message.from_user.id]:
           if tex1 in i['address'] and tex2 in i['address'] and pool in i['pool']:
              wallid = i['address']; pool = i['pool']
              usrWallets[message.from_user.id] = {'address':wallid,'pool':pool}
              break
       msg = f"**Alright switched your wallet**\n\nUsing Address: <code>{wallid}</code>\nPool: <code>{pool}</code>"
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
#       print(wallid, allWallets)
      #  allWallets[message.from_user.id].remove(wallid)
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
       if data == "PINGMEWITHGRAPH": await main(client, message.message, True) #graph = true
       else: await main(client, message.message, False) #fetch new data
       return

    if "pool" in data:
       _,pool = data.split("|")
       if pool == "report":
          msg = "**Alright you can suggest a pool, my dev will try adding it**\n\n**Notes:** The pool should have a public api\nReply the pool name and domain name, also provide any additional details, Or you can ignore this message and directly pm my dev @_xd2222 or @Pine_Orange"
          await message.message.delete()
          msgg = await message.message.reply_text(msg, reply_to_message_id=message.message.reply_to_message_id,reply_markup=ForceReply(True, "Pool name?"))
#          print(msgg)
          return

       msgid = message.message.reply_to_message.message_id
       walletADR = (await client.get_messages(message.message.chat.id, msgid)).text
       message.message.from_user.id =  message.message.chat.id
       print(msgid, walletADR, "id: ", message.message.from_user.id)
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

       await message.answer()
       usrWallets[message.message.from_user.id] = {'address':walletADR,'pool':pool}
       allWallets[message.message.from_user.id].append({'address':walletADR,'pool':pool})
       msg = f"**I saved your wallet** you can start using me now 👍 try the buttons\n\nYour Address: <code>{walletADR}</code>\nPool: <code>{pool}</code>"
       await message.message.edit_text(msg, reply_markup = keybd)
       bookup()
       return


       print('new w add from cb:', pool, walletADR)



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

bookup("startup")
moon.run()
