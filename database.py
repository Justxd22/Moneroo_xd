import os, time, redis
from stuff import redisURI, redisPASS

class Redis:
    def __init__(self):
        self.db_uri = redisURI
        self.db_pass = redisPASS
        if self.db_uri == "" or self.db_pass == "":
            print("Please set REDIS_URI and REDIS_PASSORD")
            exit()

    def getConnection(self):
        print("Getting Connection With Redis Database")
        err = ""
        if ":" not in self.db_uri:
            err += "\nWrong REDIS_URI. Quitting...\n"
        if "/" in self.db_uri:
            err += "Your REDIS_URI should start with redis.xyz. Quitting...\n"

        self.db_uri = self.db_uri.replace("\n", "").replace(" ", "")
        self.db_pass = self.db_pass.replace("\n", "").replace(" ", "")
        self.db_uri = self.db_uri.split(":")
        if err:
            print(err)
            exit(1)

        time.sleep(1.5)
        return redis.Redis(
            host=self.db_uri[0],
            port=self.db_uri[1],
            password=self.db_pass,
            decode_responses=True)




def redis_connection():
    init_db = Redis()
    our_db = init_db.getConnection()
    time.sleep(5)
    try:
        our_db.ping()
    except BaseException:
        connected = []
        print("Can't connect to Redis Database.... Restarting....")
        for x in range(1, 6):
            try:
                our_db = Redis()
                time.sleep(3)
                if our_db.ping():
                    connected.append(1)
                    break
            except BaseException as conn:
                print(
                    f"{(conn)}\nConnection Failed ...  Trying To Reconnect {x}/5 .."
                )
        if not connected:
            print("Redis Connection Failed.....")
            exit(1)
        else:
            print("Reconnected To Redis Server Succesfully")
    print("Succesfully Established Connection With Redis DataBase.")
    return our_db
