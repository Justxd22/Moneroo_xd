import matplotlib.pyplot as plt
from matplotlib import font_manager
from random import randint
import numpy as np
import mplcyberpunk, time, os
from PIL import Image, ImageFont, ImageDraw, ImageFilter

font = "pools/assets/fonts/"
font = font_manager.findSystemFonts(fontpaths=font)
font = font_manager.fontManager.addfont(font[0])
plt.rcParams['font.family'] = 'Barkentina Test'

# extracted from moneroocean js
hashUnits = {'TH': 1000000000000, 'GH': 1000000000,
             'MH': 1000000, 'KH': 1000, 'H': 1}

def homans(inte):
    # Extracted/ported from moneroocean js
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

def plots(data, hs, filename):
    nums = []

    font = "pools/assets/fonts/Barkentina.ttf"
#    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
#    font_manager.fontManager.addfont(font_file)

    for i in reversed(range(len(data))):
#        if data[i]['hsh2'] == 0:
#           print('skip',i)
#           continue;
        nums.append(data[i]['hsh'])

    plt.rcParams['figure.dpi'] = 400
    plt.rcParams['savefig.dpi'] = 400
    plt.style.use("cyberpunk")
    fig = plt.figure()
    ax = plt.gca()


    # calc the avg as the last value
    # for better looking graph end
    # it ends in the middle
    # it doesn't look too high or at ZERO
    avg = sum(nums)/len(nums)

    # only add avg if the last value is very high
    # we don't want to mess with the data
    if avg < nums[-1]:
       nums.append(avg)
       print('applied avg')

    line1 = plt.plot(nums)
    plt.grid(False)
    plt.axis('off')

    width, height = fig.canvas.get_width_height()

    x1, y1 = line1[0].get_data()
    # Get the middle of two points
    # Feom my geometry book (old one g9)
    # Finally something useful from all those school year
    def rann(i):
       notallowed = [0,1,2,i-1,i-2,i]
       while 1:
          ii = randint(0, i)
          if ii not in notallowed:
             break

       return ii

    mid = rann(len(data))
    mid2 = mid+1
    texx1 = (x1[mid] + x1[mid2])/2
    texy1 = (y1[mid] + y1[mid2])/2

    # convert Coordinates to pixels
    boxCords1 = ax.transData.transform((texx1,texy1))
    xpix1, ypix1 = boxCords1
    ypix1 = height - ypix1

    mplcyberpunk.add_glow_effects(gradientFill=True)
    plt.savefig(f'pools/graphs/{filename}PLOT.png', bbox_inches='tight') #, dpi=300)
    plt.close(fig)
#    plt.show()



    img    = Image.open(f"pools/graphs/{filename}PLOT.png")
    legend = Image.open(clegend(hs, f"pools/graphs/{filename}LEG.png")) #Image.open("./assets/legend.png")
    font = "pools/assets/fonts/Barkentina.ttf"
    font = ImageFont.truetype(font, 40)

#    300dpi
#    xpix1 = round(xpix1)-160
#    xpix2 = round(xpix2)-160
#    ypix1 = round(ypix1)-170
#    ypix2 = round(ypix2)-150

    # 400dpi
    xpix1 = round(xpix1)-370
    ypix1 = round(ypix1)-220

    text_size1 = font.getsize('avg - '+homans(avg))
    box_size1  = (text_size1[0]+20,text_size1[1]+20)

    boxes_mask = Image.new('L', img.size, 0)
    legend_mask= Image.new('L', img.size,0)
    box_img1   = Image.new('RGBA', box_size1, (0,0,0,0))

    masks      = ImageDraw.Draw(boxes_mask)
    box_draw1  = ImageDraw.Draw(box_img1)

    masks.rounded_rectangle((xpix1,ypix1,box_size1[0]+xpix1,box_size1[1]+ypix1), 15, fill=255)
    legend_mask.paste(legend, (45,45))
    blur = img.filter(ImageFilter.GaussianBlur(10))
    img.paste(blur, mask=boxes_mask)
    img.paste(blur, mask=legend_mask)

    box_draw1.rounded_rectangle(((0, 0), box_size1), 15, outline=(162,162,162,255), width=3)

    box_draw1.text((10, 10), 'avg - '+homans(avg), font=font,fill=(240,240,240,255))
    img.paste(box_img1, (xpix1,ypix1), box_img1)
    img.paste(legend, (45,45), legend)

    img.save(f"pools/graphs/{filename}.png", 'PNG')
    try:
       os.remove(f"pools/graphs/{filename}PLOT.png")
       os.remove(f"pools/graphs/{filename}LEG.png")
    except: pass

    return f"pools/graphs/{filename}.png"

def clegend(hs, filename):
    palette = dict(zip([f'Hashrate - {hs}'], [['#00ff41']))

#    plt.rcParams['text.color'] = '0'
    handles = [plt.Line2D([], [], color=c, label=l) for l, c in palette.items()]
    fig = plt.figure()
    legend = fig.gca().legend(handles=handles, framealpha=1, frameon=True, fancybox=True, edgecolor='white')
    legend.get_frame().set_alpha(None)
    legend.get_frame().set_facecolor((0, 0, 0, 0))

    fig.canvas.draw()
    bbox  = legend.get_window_extent().padded(2).transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(filename, dpi=400, transparent=True, bbox_inches=bbox)
    plt.close(fig)
    return filename

def now(): return round(time.time())
def starttime(): return now() - 14400 # idk
def apiformating(data, lendata, timenow):
    # what you are about to see is magic:
    # no body asks how magic works so....
    # ported from supportxmr js
    interval = 300
    r = {}
    r_key = 0
    r_now = now()
    r_avg = 0
    r_cnt = 0

    for i in range(lendata):
        tme = round(data[i]['ts'] / 1e3)
        hsh = int(data[i]['hs'])

        if tme >= timenow:
           if tme >= r_now - interval:
             r_avg += hsh;
             r_cnt+=1;

           else:
             avg = 0 # r_cnt > 0 && r_avg > 0) ? Rnd((r_avg / r_cnt), 0) : 0;
             if r_cnt > 0 and r_avg > 0: avg = round(r_avg/r_cnt, 0)
             r[r_key] = {'tme': r_now, 'hsh': avg};
             r_avg = hsh;
             r_cnt = 1;
             r_now = r_now - interval;
             r_key+=1;

#   these are useless idkkk
#    d_cnt = len(data)
#    d_sum = 0
#    r_cnt = len(r)
#    r_sum = 0
#
#    for i in range(d_cnt):
#        d_sum += data[i]['hs'];
#    for i in range(r_cnt):
#        r_sum += r[i]['hsh'];

    return r
