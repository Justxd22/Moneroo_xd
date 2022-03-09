import matplotlib.pyplot as plt
from matplotlib import font_manager
from random import randint
import numpy as np
import mplcyberpunk, time, os
from PIL import Image, ImageFont, ImageDraw, ImageFilter
from stuff import homans

font = "./assets/fonts/"
font = font_manager.findSystemFonts(fontpaths=font)
font = font_manager.fontManager.addfont(font[0])
plt.rcParams['font.family'] = 'Barkentina Test'

def plots(data, hs2, hs, filename):
    nums = []
    nums2 = []

    font = "./fonts/Barkentina.ttf"
#    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
#    font_manager.fontManager.addfont(font_file)

    for i in reversed(range(len(data))):
        if data[i]['hsh2'] == 0:
           print('skip',i)
           continue;
        nums.append(data[i]['hsh2'])
        nums2.append(data[i]['hsh'])

    plt.rcParams['figure.dpi'] = 600
    plt.rcParams['savefig.dpi'] = 600
    plt.style.use("cyberpunk")
    fig = plt.figure()
    ax = plt.gca()


    # calc the avg as the last value
    # for better looking graph end
    # it ends in the middle
    # it doesn't look too high or at ZERO
    avg = sum(nums)/len(nums)
    avg2 = sum(nums2)/len(nums2)

    # only add avg if the last value is very high
    # we don't want to mess with the data
    if avg < nums[-1]:
       nums.append(avg)
       print('applied avg')

    if avg2 < nums2[-1]:
       nums2.append(avg2)
       print('applied avg2')


    line1 = plt.plot(nums)
    plt.grid(False)
    plt.axis('off')

    line2 = plt.plot(nums2)
    plt.grid(False)
    plt.axis('off')

    width, height = fig.canvas.get_width_height()

    x1, y1 = line1[0].get_data()
    x2, y2 = line2[0].get_data()
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

    mid = rann(len(data))
    mid2 = mid+1
    texx2 = (x2[mid] + x2[mid2])/2
    texy2 = (y2[mid] + y2[mid2])/2

    # convert Coordinates to pixels
    boxCords1 = ax.transData.transform((texx1,texy1))
    xpix1, ypix1 = boxCords1
    ypix1 = height - ypix1

    boxCords2 = ax.transData.transform((texx2,texy2))
    xpix2, ypix2 = boxCords2
    ypix2 = height - ypix2
#    print("The pixel coordinates are: ",xpix2, ypix2)


    mplcyberpunk.add_glow_effects()
    plt.savefig(f'./graphs/{filename}PLOT.png', bbox_inches='tight') #, dpi=300)
    plt.close(fig)
#    plt.show()



    img    = Image.open(f"./graphs/{filename}PLOT.png")
    legend = Image.open(clegend(hs2, hs, f"./graphs/{filename}LEG.png")) #Image.open("./assets/legend.png")
    font = "./assets/fonts/Barkentina.ttf"
    font = ImageFont.truetype(font, 40)

#    300dpi
#    xpix1 = round(xpix1)-160
#    xpix2 = round(xpix2)-160
#    ypix1 = round(ypix1)-170
#    ypix2 = round(ypix2)-150

    xpix1 = round(xpix1)-370
    xpix2 = round(xpix2)-370
    ypix1 = round(ypix1)-220
    ypix2 = round(ypix2)-165

    text_size1 = font.getsize('avg - '+homans(avg))
    text_size2 = font.getsize('avg - '+homans(avg2))
    box_size1  = (text_size1[0]+20,text_size1[1]+20)
    box_size2  = (text_size2[0]+20,text_size2[1]+20)

    boxes_mask = Image.new('L', img.size, 0)
    legend_mask= Image.new('L', img.size,0)
    box_img1   = Image.new('RGBA', box_size1, (0,0,0,0))
    box_img2   = Image.new('RGBA', box_size2, (0,0,0,0))

    masks      = ImageDraw.Draw(boxes_mask)
    box_draw1  = ImageDraw.Draw(box_img1)
    box_draw2  = ImageDraw.Draw(box_img2)

    masks.rounded_rectangle((xpix1,ypix1,box_size1[0]+xpix1,box_size1[1]+ypix1), 15, fill=255)
    masks.rounded_rectangle((xpix2,ypix2,box_size2[0]+xpix2,box_size2[1]+ypix2), 15, fill=255)
    legend_mask.paste(legend, (45,45))
    blur = img.filter(ImageFilter.GaussianBlur(10))
    img.paste(blur, mask=boxes_mask)
    img.paste(blur, mask=legend_mask)

    box_draw1.rounded_rectangle(((0, 0), box_size1), 15, outline=(162,162,162,255), width=3)
    box_draw2.rounded_rectangle(((0, 0), box_size2), 15, outline=(162,162,162,255), width=3)

    box_draw1.text((10, 10), 'avg - '+homans(avg), font=font,fill=(240,240,240,255))
    box_draw2.text((10, 10), 'avg - '+homans(avg2) , font=font,fill=(240,240,240,255))
    img.paste(box_img1, (xpix1,ypix1), box_img1)
    img.paste(box_img2, (xpix2,ypix2), box_img2)
    img.paste(legend, (45,45), legend)

    img.save(f"./graphs/{filename}.png", 'PNG')
    try:
       os.remove(f"./graphs/{filename}PLOT.png")
       os.remove(f"./graphs/{filename}LEG.png")
    except: pass

    return f"./graphs/{filename}.png"

def clegend(hs2, hs, filename):
    palette = dict(zip([f'Pay hashrate - {hs2}', f'Raw  hashrate - {hs}'], ['#c803ff', '#00ff41']))

#    plt.rcParams['text.color'] = '0'
    handles = [plt.Line2D([], [], color=c, label=l) for l, c in palette.items()]
    fig = plt.figure()
    legend = fig.gca().legend(handles=handles, framealpha=1, frameon=True, fancybox=True, edgecolor='white')
    legend.get_frame().set_alpha(None)
    legend.get_frame().set_facecolor((0, 0, 0, 0))

    fig.canvas.draw()
    bbox  = legend.get_window_extent().padded(2).transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(filename, dpi=600, transparent=True, bbox_inches=bbox)
    plt.close(fig)
    return filename

def now(): return round(time.time())
def starttime(): return now() - 129600 # ask devs at moneroocean wtf is this
def apiformating(data, lendata, timenow):
    # what you are about to see is magic:
    # no body asks how magic works so....
    # ported from moneroocean js
    interval = 15 * 60
    r = {}
    r_key = 0
    r_now = now()
    r_avg = 0
    r_avg2 = 0
    r_cnt = 0
    prev_tme = now()
    # sort elements from large time to low time
    def tmeDesnd(element): return element['ts']
    data.sort(reverse=True, key=tmeDesnd)
    for i in range(lendata):
        tme = round(data[i]['ts'] / 1e3)
        if tme < timenow:
           print('very old data') # incase data is too old
           break;                 # it's not inculded in the graph
        hsh = int(data[i]['hs'])
        hsh2 = int(data[i]['hs2'])
        if prev_tme - tme < interval:
           r_avg += hsh;
           r_avg2 += hsh2;
           r_cnt+=1;
        else:
           if r_cnt == 0: result = hsh; # rcnt ? ravg / rcnt : hsh
           else: result = r_avg / r_cnt;
           if r_cnt == 0: result2 = hsh2; # rcnt ? ravg2 / rcnt : hsh2
           else: result2 = r_avg2 / r_cnt;
           try:
              if r[0]['tme']: r_key+=1
           except KeyError: pass;
           r[r_key] = {'tme': prev_tme, 'hsh': result, 'hsh2': result2};
           if i < 200 and prev_tme - tme > 2 * interval:
              r_key+=1
              r[r_key] = {'tme': prev_tme - 1, 'hsh': 0, 'hsh2': 0 };

              r_key+=1
              r[r_key] = {'tme': tme + 1, 'hsh': 0, 'hsh2': 0}

           r_avg = 0; r_avg2 = 0; r_cnt = 0; prev_tme = tme;
    r_key+=1 # idk man it just works like this
    for i in range(r_key):
         if r == {}: return None
         if r[i]['hsh'] == 0:  continue;
         r_avg = 0; r_avg2 = 0; r_cnt = 0; jj = -10;
         while jj != 11:
            if i + jj < 0 or i + jj >= r_key:
               jj +=1
               continue;
            r_avg += r[i + jj]['hsh'];
            r_avg2 += r[i + jj]['hsh2'];
            r_cnt+=1
            jj +=1

         r[i]['hsh'] = r_avg / r_cnt
         r[i]['hsh2'] = r_avg2 / r_cnt

    return r
