import time
# the max limit a unit can take before it became unreadable
# for example seconds max at 59
# ok     40 sec ago - 59 sec ago
# not ok 64 sec ago - 74 sec ago
# same for m and h days doesn't have a max
d = "infint" #lol
h = 86400
m = 3540
s = 59
def timeinletters(unixt):
    t    = int(time.time())
    diff = t - unixt
    days=hours=mins=secs=None
    if   diff < s:  return str(diff) + "s ago"
    elif diff < m:  return str(round(diff/60)) + "m ago"
    elif diff < h:  return str(int(diff/3600)) + "h ago"
    else:           return str(int(diff/86400)) + "days ago"
