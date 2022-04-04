import os, datetime, sys
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup,InlineKeyboardButton

token = os.getenv("token", "")
app_id = os.getenv("app_id", "")
app_hash = os.getenv("app_hash", "")
logGroup = os.getenv("logGroup", "")
redisURI = os.getenv("redisURI", "")
redisPASS = os.getenv("redisPASS", "")

x = datetime.datetime.utcnow()
i = x + datetime.timedelta(hours=3)
y = i.strftime("%Y-%m-%d_%I:%M%P")
d = i.strftime("%Y-%m-%d")
na = d + ".txt"
print(na)
print("My PID is:", os.getpid())

if len(str(token)) < 5: print("please put your token in env"); sys.exit(1)
if logGroup: logGroup = int(logGroup);

keybd = ReplyKeyboardMarkup([
     ['📬Ping📜', '⁉️Help', '💰Wallet'],
     ['💸Donate❤️', '😊Thanks', '👀Who?']], resize_keyboard=True)

pools = InlineKeyboardMarkup([
        [InlineKeyboardButton("Moneroocean", callback_data="pool|MO"),
         InlineKeyboardButton("C3pool", callback_data="pool|C3")],
        [InlineKeyboardButton("Nanopool", callback_data="pool|NANO"),
         InlineKeyboardButton("SupportXMR", callback_data="pool|SPXMR")],
        [InlineKeyboardButton("MineXMR☹️", callback_data="pool|minexmr"),
         InlineKeyboardButton("👀Not listed?", callback_data="pool|report")]])

stk0 = "CAADBAADrgcAAnILQFPgjUtxHDj-oQI"
stk1 = "CAADBAADlQoAAo8RQFOWkvFydBKJlwI"
stk2 = "CAADBAADSAsAAn_eOFPurvLfXO2hzAI"
stk3 = "CAADBAAD0QoAAkKSOFND8vqd0dBlhQI"
stk4 = "CAADAQADGwADabn4TK5rm6F3R6RvAg"
stk5 = "CAADBAADHwoAAgTjOFPwcaIN8VE3uQI"
stk6 = "CAADBAAD2AgAAv1sOFOBvhMuUqdpVgI"
stk7 = "CAADBAAD_AkAAzI4U1zm0zS8ZmfzAg"
stk8 = "CAADBAADZQoAAvmvQFN_0Kq6nbL7IAI"
stk9 = "CAADBAADKgwAAkYwAVNi12G8g59PaAI"
stk10 ="CAADBAADEw4AAg-KCFNpq_7F9U8esAI"
stk11 ="CAADBAADAQoAAiWVAAFTxQWRFrkAARXjAg"
stk12 ="CAADBAAD7woAAhuzCVMcN1Wsyt074gI"

startMsg = """
Hello **%s fellow miner**,
I can help making mining easier
Setup your miner and come here check your stats

**Send your Wallet** address to start
Or checkout /help"""

helpMsg = """
Hello **%s fellow miner**,

I'm very easy to use

**Steps**
1.Copy your public Wallet address
  from Moneroocean.com
2.Paste me your wallet address
3.Enjoy

Note:Your public wallet address
      is safe to share as no one can
      control your wallet except
      with a private key,
      So don't you worry.

**Commands**
 •/start - sTaRtMe
 •/help - show this menu
 •/ping - Ping Moneroocean and return Stuff
 •/donate - ❤️ Reward My dev
 •/about - About the dev
 •/sauce - See How i work (git repo)

**Buttons**
 •Ping - Ping Moneroocean and return Stuff
 •Help - Show help
 •Wallet - Select/add/delete Wallet Addresses
 •Thanks - Say thanks to me
 •Donate - ❤️ Reward My dev
 •Who? - About the dev
"""
aboutMsg = """
Hello **%s fello miner**,

I'm **@Moneroo_xd_bot** 👋
**Project** By **@Pine_Orange** also know as **@xd2222**

**Info:**

•**Programming Language**: **Python** 3.9
•**Hosting**: **railway.app** and Sometimes **Heroku**
•**Source Code**: hosted on <a href="">**github.com**</a> use /sauce

**Libares used:**

•**pyrogram** - the middle guy Contacts telegram bot API

**About Me:**

known as **.XD22**

i'm a **dev** (kind of) and a **student** (kind of too)

My other Bots:

•**@Catty_Xd_bot** - Cat fantasy
•**@rdt_XD_bot** - The Reddit Universe
•**@Memes_XD_bot** - Bored?
•**@Spotify_XD_bot** - Love music? Enjoy it offline for free
•**@Tube_XD_bot** - Fastest youtube downloader out in the wild

**Links:**

•**Website**: **justxd22.github.io**
•**Github**: **github.com/justxd22**

**Donate: use /donate**"""

donateMsg = """
**Donations** will be used in:
 •Keeping Hosting server up
 •Help with my study
 •Maybe Updating My rig?

**Donating Address**
** •XMR:<code>%s</code>**

  total Donations Received: 0.0 XMR
  (click button bellow if you donated)

Thanks Kind Miner %s
"""

sauce = """
**Are you a dev?

sauce code  : github.com/justxd22/Moneroocean_xd
Hop on my github: github.com/justxd22
(✨ support me by staring 🌟)**"""

msg0 = "**OoPs, pLz send Vaild wallet address** address not found"
msg1 = "**4o4 not found** looks like the website is down??"
msg2 = "**Hold tight!**"
msg3 = "**OoPs, s0mETHing wENT wRONg**"

logger1 = "**New user!!**"
logger2 = "**User May have donated**"
logger3 = "**User is Happy** says thanks "
logger4 = "**User is curious**"

donwallet = "433CbZXrdTBQzESkZReqQp1TKmj7MfUBXbc8FkG1jpVTBFxY9MCk1RXPWSG6CnCbqW7eiMTEGFgbHXj3rx3PxZadPgFD3DX"
