import requests, json, re
from random import randint
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from stuff import *
from database import redis_connection

db = redis_connection()

moon = Client("moon_XD",
      api_id = app_id, api_hash = app_hash,
      bot_token = token)

usrWallets = {}
allWallets = {}
users = {}

def bookup(task=""):
    if task == "startup":
       usrwall = db.get('usrwall')
       allwall = db.get('allwall')
       usrs = db.get('usrs')
       global usrWallets; global allWallets; global users;
       usrWallets = json.loads(usrwall, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})
       allWallets = json.loads(allwall, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})
       users      = json.loads(usrs, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})
       print("restored backup")
       return

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

    if message.from_user.id in users: print("user in db");
    else:
        users[message.from_user.id] = "[]"
        print("user not in db, Added", users);
        await logger(client, message, "New user!")
        bookup()

def homans(inte):
    # Extracted from moneroocean js
    # idk how tf it works but it does
    # removed wierd checks like ===
    # i mean why would you check the type??
    if inte < 0: inte = 0
    u = "/s"
    for un in hashUnits:
        if inte >= hashUnits[un]:
           inte = inte/hashUnits[un]
           u = f"{un}{u}"
           break
    if inte == 0: u = "H/s"
    inte = round(inte, 2)
    print(inte, u)
    return(f"{inte} {u}")

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
    if str(message.chat.id) == "800219239":
       await message.reply_text("**Hold tight restarting.....**")
       restartDyno()
       await message.reply_text("**Restarted?.....**")

@moon.on_message(filters.command("getusr"))
async def get(client, message):
    if str(message.chat.id) == "800219239":
       m = await message.reply_text("Hold on!")
       total_users = len(users)
       print("total users:", total_users)
       await m.edit_text(f"Totalusers: {total_users}")

@moon.on_message(filters.command("getkey"))
async def getkey(client, message):
    if str(message.chat.id) == "800219239":
       m = await message.reply_text("Hold on!")
       key = message.text
       key = key.replace("/getkey ", "")
       if not key in users : await m.edit_text("User in db? use /get"); return
       await m.edit_text(f"User in db {key}")

@moon.on_message(filters.command("ping"))
async def main(client, message):
    if not message.from_user.id in usrWallets:
       await message.reply_text("**Sorry i don't have your wallet address** to fetch your mining stats, see /help")
       return

    messg = await message.reply_text(msg2)
    stkr = await message.reply_sticker(stk4)

    try:
       wallet = usrWallets[message.from_user.id]
       stats = requests.get(f"https://api.moneroocean.stream/miner/{wallet}/stats", headers=statsheader)
       if stats.status_code != 200:
          await stkr.delete()
          await messg.edit_text(msg1)
          print("http error\n\n", stats.text)
          return

       stats = json.loads(stats.text)
       miners= requests.get(f"https://api.moneroocean.stream/miner/{wallet}/chart/hashrate/allWorkers", headers=statsheader)
       miners= json.loads(miners.text)
       totalMiners = len(miners)-1
       minersName = []
       for i in range(len(miners)):
           if i==0: continue;
           minersName.append(list(miners.keys())[i])
       if len(minersName) ==0: minersName = 'No miners Alive'
       else: minersName = ", ".join(minersName)

    except Exception as e:
       await stkr.delete()
       await messg.edit_text(msg0, str(e))
       await logger(client, message, "got this error")
       return

    msg = f"""
**Miners:** {totalMiners} workers
**Workers:** {minersName}
**Pay hashrate:** {homans(stats['hash2'])}
**Raw hashrare:** {homans(stats['hash'])}
**Shares:** {stats['validShares']}
**Rejected Shares:** {stats['invalidShares']}
**XMR mined:** {stats['amtDue']/1000000000000} XMR
**Paid XMR:** {stats['amtPaid']/1000000000000} XMR"""
    await stkr.delete()
    await messg.edit_text(msg)

@moon.on_message(filters.text)
async def wallet(client, message):
    # extracted from moneroocean js regex
    Wpattern = "^[4|8]{1}([A-Za-z0-9]{105}|[A-Za-z0-9]{94})$"
    SwitchPatt = "^[💰]{1}[4|8]{1}[A-Za-z0-9]{7}[*]{4}[A-Za-z0-9]{8}$"
    DelPatt =    "^[4|8]{1}[A-Za-z0-9]{7}[*]{4}[A-Za-z0-9]{8}[💰]{1}$"
    text = message.text
    if re.search(Wpattern, text):
       print("Valid Wallet!")
       try: allWallets[message.from_user.id]
       except KeyError: allWallets[message.from_user.id] = list()

       if text in allWallets[message.from_user.id]:
          msg = "**I already saved this address** you can switch to it use 💰Wallet button"
          await message.reply_text(msg)
          return

       usrWallets[message.from_user.id] = text
       allWallets[message.from_user.id].extend([text])
       msg = f"**I saved your wallet** you can start using me now 👍 try the buttons\n\nYour Address: <code>{text}</code>"
       await message.reply_text(msg)
       bookup()
       return

    if re.search(SwitchPatt, text):
       print("Craffted wallet!")
       tex1, tex2 = text.replace("💰", "").split("****")
       for i in allWallets[message.from_user.id]:
           if tex1 in i and tex2 in i:
              usrWallets[message.from_user.id] = i
              wallid = i
              break
       msg = f"**Alright switched your wallet**\n\nUsing Address: <code>{wallid}</code>"
       await message.reply_text(msg, reply_markup = keybd)
       bookup()
       return

    if re.search(DelPatt, text.replace('🗑️', '')):
       print("Delete wallet req!")
       tex1, tex2 = text.replace("💰", "").replace("🗑️", "").split("****")
       for i in allWallets[message.from_user.id]:
           if tex1 in i and tex2 in i:
              wallid = i
              break
       print(wallid, allWallets)
       allWallets[message.from_user.id].remove(wallid)
       if usrWallets[message.from_user.id] == wallid:
          usrWallets.pop(message.from_user.id)
       msg = f"**Alright removed your wallet** Address: <code>{wallid}</code>"
       await message.reply_text(msg, reply_markup = keybd)
       bookup()
       return

    if text.lower().replace("💰", "") == "wallet":
       keypad = []
       try:
           addrs = allWallets[message.from_user.id]
           CurAddrs = usrWallets[message.from_user.id]
       except KeyError:
           await message.reply_text("**Sorry i don't have your wallet address** to fetch your mining stats, see /help")
           return

       for i in addrs:
           tex = "💰" + i[:8] + "****" + i[87:]
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
           await message.reply_text("**Huh?, there's nothing to delete**")
           return

       for i in addrs:
           tex = "🗑️" + i[:8] + "****" + i[87:] + "💰"
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

@moon.on_callback_query()
async def calls(client, message):
    data = message.data
    if "donationnnnloooolllll" in data:
       await message.answer("❤️❤️Thank you kind Miner")
       await message.message.reply_sticker(stk9)
       await message.message.reply_sticker(stk10)
       await message.message.reply_sticker(stk11)
       await message.message.reply_sticker(stk12)

def getName(client, message):
    user_id = message.from_user.id
    username = "@" + message.from_user.username
    frname = message.from_user.first_name
    lasname = message.from_user.last_name
    name = ""

    if username != "None":
       name = username
    elif frname != "None":
       name = frname
    elif username == "None" and frname == "None":
       name = str(user_id)
    return name

async def logger(client, message, msg, text=""):
    ms = msg + text + f"\n\n{message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username} {message.from_user.id}"
    await client.send_message(logGroup, ms, disable_web_page_preview=True)

bookup("startup")
moon.run()
