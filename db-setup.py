from database import redis_connection


uri = input("What's your redis-uri? type in uri:port format (press enter to use localhost) uri: ")
pas = input("What's your redis-pass? (press enter for empty) pass: ")


db = redis_connection(uri,pas)

db.set('usrwall', '{}')
db.set('allwall', '{}')
db.set('usrs', '{}')
db.set('p2pusrs', '{}')


try:
   db.get('usrwall')
   db.get('allwall')
   db.get('usrs')
   db.get('p2pusrs')
except Exception as e:
   print('Error: \n\n', str(e))
   exit()

print('all good you can run the bot now')
