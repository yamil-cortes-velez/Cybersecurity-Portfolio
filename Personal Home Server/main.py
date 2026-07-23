import pygame
import sys
import requests

pygame.init()

SCREEN_W, SCREEN_H = 800, 480
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.NOFRAME)
pygame.display.set_caption("Cortes Server")
clock = pygame.time.Clock()

FLASK_URL = "http://localhost:5000"

BG     = (13, 13, 20)
DARK   = (19, 19, 31)
BLUE   = (74, 158, 255)
PURPLE = (168, 85, 247)
YELLOW = (245, 158, 11)
WHITE  = (255, 255, 255)
GREY   = (50, 50, 80)
RED    = (255, 68, 68)
GREEN  = (100, 200, 100)

font_sm = pygame.font.SysFont("monospace", 13)
font_md = pygame.font.SysFont("monospace", 18)
font_lg = pygame.font.SysFont("monospace", 26)

ASSET = r"C:\Users\arcey\Desktop\Animation\ "[:-1]

def load(name, size=None):
    img = pygame.image.load(ASSET + name).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

lock_locked   = load("Lock_Locked.png",   (44, 44))
lock_unlocked = load("Lock_Unlocked.png", (44, 44))
camera_img    = load("Camera.png",        (72, 72))
files_img     = load("Files_Image.png",   (72, 72))
house_img     = load("House.png",         (128, 128))
server_y      = load("Server.png",        (128, 128))
server_g      = load("Server_Green.png",  (128, 128))
walk_frames   = [load(f"walk_{i}.png",    (96, 96)) for i in range(1, 5)]

STATE_HOME     = "home"
STATE_PIN      = "pin"
STATE_FILES    = "files"
STATE_PHOTOS   = "photos"
STATE_SEND     = "send"
STATE_TRANSFER = "transfer"

state         = STATE_HOME
unlocked      = False
pin_input     = ""
correct_pin   = "1234"
pin_error     = False

transfer_mode     = "upload"
transfer_progress = 0.0
repair_man_x      = 100
repair_man_y      = 190
frame_index       = 0
frame_timer       = 0
flicker_timer     = 0
use_green         = False

file_list    = []
photo_list   = []
device_list  = []
scroll_offset = 0

storage_total   = 1
storage_used    = 0
storage_percent = 0.0
local_ip        = "unavailable"

r_files   = pygame.Rect(0,0,0,0)
r_photos  = pygame.Rect(0,0,0,0)
r_send    = pygame.Rect(0,0,0,0)
r_lock    = pygame.Rect(0,0,0,0)
exit_rect = pygame.Rect(0,0,0,0)
file_rects  = []
photo_rects = []
dev_rects   = []
back_rect   = pygame.Rect(0,0,0,0)
pin_rects   = {}

def get_local_ip():
    global local_ip
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "unavailable"

def fetch_storage():
    global storage_total, storage_used, storage_percent
    try:
        r = requests.get(f"{FLASK_URL}/storage", timeout=2)
        d = r.json()
        storage_total   = d["total"]
        storage_used    = d["used"]
        storage_percent = d["percent"] / 100
    except:
        pass

def fetch_files():
    global file_list
    try:
        r = requests.get(f"{FLASK_URL}/api/files", timeout=2)
        file_list = r.json().get("files", [])
    except:
        file_list = []

def fetch_photos():
    global photo_list
    try:
        r = requests.get(f"{FLASK_URL}/api/photos", timeout=2)
        photo_list = r.json().get("photos", [])
    except:
        photo_list = []

def fetch_devices():
    global device_list
    try:
        r = requests.get(f"{FLASK_URL}/api/devices", timeout=2)
        device_list = r.json().get("devices", [])
    except:
        device_list = []

def delete_file(filename):
    try:
        requests.get(f"{FLASK_URL}/delete/{filename}", timeout=2)
    except:
        pass

def gb(b):
    return f"{b / 1e9:.1f} GB"

def draw_text(text, font, color, x, y, center=False):
    surf = font.render(str(text), True, color)
    if center:
        x -= surf.get_width() // 2
    screen.blit(surf, (x, y))

def draw_topbar(title):
    pygame.draw.rect(screen, DARK, (0, 0, 800, 48))
    pygame.draw.line(screen, GREY, (0, 48), (800, 48), 1)
    draw_text("CORTES SERVER", font_sm, (80,80,120), 12, 6)
    draw_text(f"IP: {local_ip}:5000", font_sm, (80,80,120), 12, 24)
    draw_text(title, font_md, WHITE, SCREEN_W//2, 14, center=True)
    # exit button — top right, spaced from lock
    global exit_rect
    exit_rect = pygame.Rect(SCREEN_W-120, 8, 52, 30)
    pygame.draw.rect(screen, RED, exit_rect, border_radius=6)
    draw_text("EXIT", font_sm, WHITE, SCREEN_W-94, 14, center=True)
    # lock icon — top right corner
    icon = lock_unlocked if unlocked else lock_locked
    screen.blit(icon, (SCREEN_W-58, 2))
    bar_x, bar_y, bar_w, bar_h = 480, 8, 160, 8
    pygame.draw.rect(screen, GREY, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    pygame.draw.rect(screen, BLUE, (bar_x, bar_y, int(bar_w * storage_percent), bar_h), border_radius=4)
    draw_text(f"{gb(storage_used)}/{gb(storage_total)}", font_sm, BLUE, bar_x, bar_y+12)

def draw_bottombar(text):
    pygame.draw.rect(screen, DARK, (0, 448, 800, 32))
    pygame.draw.line(screen, GREY, (0, 448), (800, 448), 1)
    draw_text(text, font_sm, (60,60,90), SCREEN_W//2, 458, center=True)

def draw_back():
    b = pygame.Rect(12, 415, 90, 28)
    pygame.draw.rect(screen, GREY, b, border_radius=6)
    draw_text("← BACK", font_sm, WHITE, 57, 421, center=True)
    return b

def draw_card(rect, label, color, icon=None, locked=False):
    x, y, w, h = rect
    pygame.draw.rect(screen, (15,15,25) if locked else DARK, rect, border_radius=12)
    pygame.draw.rect(screen, (40,40,50) if locked else color, rect, 2, border_radius=12)
    pygame.draw.rect(screen, (60,60,60) if locked else color, (x,y,w,4), border_radius=6)
    if icon:
        ix = x + 16
        iy = y + h//2 - icon.get_height()//2
        if locked:
            dark = icon.copy()
            mask = pygame.Surface(icon.get_size(), pygame.SRCALPHA)
            mask.fill((30,30,30,180))
            dark.blit(mask, (0,0))
            screen.blit(dark, (ix, iy))
        else:
            screen.blit(icon, (ix, iy))
    tc = (50,50,50) if locked else WHITE
    draw_text(label, font_md, tc, x+(110 if icon else w//2), y+h//2-9, center=(icon is None))
    if locked:
        screen.blit(lock_locked, (x+w-36, y+8))
    return pygame.Rect(rect)

def draw_home():
    global r_files, r_photos, r_send, r_lock
    screen.fill(BG)
    for x in range(0,800,40):
        pygame.draw.line(screen,(20,20,30),(x,0),(x,480))
    for y in range(0,480,40):
        pygame.draw.line(screen,(20,20,30),(0,y),(800,y))
    draw_topbar("HOME")
    pad = 12
    bw = (800 - pad*3) // 2
    bh = (480 - 48 - 32 - pad*3) // 2
    r_files  = draw_card((pad,      48+pad,      bw, bh), "FILES",  BLUE,   files_img,  not unlocked)
    r_photos = draw_card((pad*2+bw, 48+pad,      bw, bh), "PHOTOS", PURPLE, camera_img, not unlocked)
    r_send   = draw_card((pad,      48+pad*2+bh, bw, bh), "SEND",   YELLOW, None,       not unlocked)
    r_lock   = draw_card((pad*2+bw, 48+pad*2+bh, bw, bh), "LOCK" if unlocked else "UNLOCK", BLUE, None, False)
    draw_bottombar(f"CONNECT AT {local_ip}:5000  ·  WIREGUARD ACTIVE")

def draw_pin():
    global pin_rects
    overlay = pygame.Surface((800,480), pygame.SRCALPHA)
    overlay.fill((0,0,0,200))
    screen.blit(overlay,(0,0))
    pw, ph = 320, 400
    px = SCREEN_W//2 - pw//2
    py = SCREEN_H//2 - ph//2
    pygame.draw.rect(screen, DARK, (px,py,pw,ph), border_radius=16)
    pygame.draw.rect(screen, BLUE, (px,py,pw,ph), 2, border_radius=16)
    draw_text("ENTER PIN", font_md, (150,150,200), SCREEN_W//2, py+16, center=True)
    dot_y = py+56
    for i in range(4):
        cx = px+52+i*58
        filled = i < len(pin_input)
        color = RED if pin_error else (BLUE if filled else GREY)
        pygame.draw.circle(screen, color, (cx,dot_y), 13 if filled else 9, 0 if filled else 2)
    nums = [['1','2','3'],['4','5','6'],['7','8','9'],['X','0','OK']]
    bw2,bh2,bp = 76,50,8
    gx = px+(pw-(bw2*3+bp*2))//2
    gy = dot_y+36
    pin_rects = {}
    for ri,row in enumerate(nums):
        for ci,key in enumerate(row):
            bx = gx+ci*(bw2+bp)
            by = gy+ri*(bh2+bp)
            c = RED if key=='X' else (GREEN if key=='OK' else GREY)
            pygame.draw.rect(screen,(25,25,40),(bx,by,bw2,bh2),border_radius=8)
            pygame.draw.rect(screen,c,(bx,by,bw2,bh2),2,border_radius=8)
            draw_text(key,font_lg,WHITE,bx+bw2//2,by+bh2//2-13,center=True)
            pin_rects[key] = pygame.Rect(bx,by,bw2,bh2)

def draw_files():
    global file_rects, back_rect
    screen.fill(BG)
    draw_topbar("FILES")
    file_rects = []
    y_start = 58
    for i,f in enumerate(file_list):
        fy = y_start+i*52-scroll_offset
        if 48 < fy < 410:
            pygame.draw.rect(screen,DARK,(12,fy,776,44),border_radius=8)
            pygame.draw.rect(screen,GREY,(12,fy,776,44),1,border_radius=8)
            draw_text(f[:50],font_sm,WHITE,20,fy+15)
            dl = pygame.Rect(618,fy+8,68,28)
            de = pygame.Rect(694,fy+8,68,28)
            pygame.draw.rect(screen,BLUE,dl,border_radius=6)
            pygame.draw.rect(screen,RED, de,border_radius=6)
            draw_text("GET",font_sm,WHITE,652,fy+14,center=True)
            draw_text("DEL",font_sm,WHITE,728,fy+14,center=True)
            file_rects.append((f,dl,de))
    back_rect = draw_back()
    draw_bottombar("SCROLL TO BROWSE · DEL TO DELETE · GET TO DOWNLOAD")

def draw_photos():
    global photo_rects, back_rect
    screen.fill(BG)
    draw_topbar("PHOTOS")
    cols,size,pad2 = 4,152,8
    photo_rects = []
    for i,p in enumerate(photo_list):
        col = i%cols
        row = i//cols
        px2 = pad2+col*(size+pad2)
        py2 = 58+row*(size+pad2)-scroll_offset
        if 48 < py2 < 410:
            pygame.draw.rect(screen,DARK,  (px2,py2,size,size),border_radius=8)
            pygame.draw.rect(screen,PURPLE,(px2,py2,size,size),2,border_radius=8)
            draw_text(p[:18],font_sm,(150,150,200),px2+4,py2+size-18)
            photo_rects.append((p,pygame.Rect(px2,py2,size,size)))
    back_rect = draw_back()
    draw_bottombar("TAP PHOTO TO DOWNLOAD")

def draw_send():
    global dev_rects, back_rect
    screen.fill(BG)
    draw_topbar("SEND")
    dev_rects = []
    for i,d in enumerate(device_list):
        dy = 60+i*64
        pygame.draw.rect(screen,DARK,  (12,dy,776,54),border_radius=8)
        pygame.draw.rect(screen,YELLOW,(12,dy,776,54),1,border_radius=8)
        draw_text(d.get("name","Unknown"),font_md,WHITE,20,dy+8)
        draw_text(d.get("wireguard_ip",""),font_sm,(120,120,80),20,dy+32)
        sr = pygame.Rect(682,dy+12,90,30)
        pygame.draw.rect(screen,YELLOW,sr,border_radius=6)
        draw_text("SEND",font_sm,(0,0,0),727,dy+18,center=True)
        dev_rects.append((d,sr))
    back_rect = draw_back()
    draw_bottombar("SELECT DEVICE TO SEND FILES")

def draw_transfer():
    global frame_index,frame_timer,flicker_timer,use_green,repair_man_x
    screen.fill((28,28,46))
    for x in range(0,800,40):
        pygame.draw.line(screen,(38,38,56),(x,0),(x,480))
    for y in range(0,480,40):
        pygame.draw.line(screen,(38,38,56),(0,y),(800,y))
    screen.blit(house_img,(40,210))
    screen.blit(server_g if use_green else server_y,(620,210))
    frame_timer+=1
    if frame_timer>=8:
        frame_timer=0
        frame_index=(frame_index+1)%4
    flicker_timer+=1
    if flicker_timer>=15:
        flicker_timer=0
        use_green=not use_green
    if transfer_mode=="upload":
        repair_man_x=min(repair_man_x+2,570)
        screen.blit(walk_frames[frame_index],(repair_man_x,repair_man_y))
    else:
        repair_man_x=max(repair_man_x-2,120)
        flipped=pygame.transform.flip(walk_frames[frame_index],True,False)
        screen.blit(flipped,(repair_man_x,repair_man_y))
    pygame.draw.rect(screen,GREY,(50,430,700,24),border_radius=8)
    pygame.draw.rect(screen,BLUE,(50,430,int(700*transfer_progress),24),border_radius=8)
    label="Uploading..." if transfer_mode=="upload" else "Downloading..."
    draw_text(f"{label}  {int(transfer_progress*100)}%",font_md,WHITE,50,403)

get_local_ip()
fetch_storage()
last_storage_tick = 0

while True:
    clock.tick(30)

    if state == STATE_HOME:
        draw_home()
    elif state == STATE_PIN:
        draw_home()
        draw_pin()
    elif state == STATE_FILES:
        draw_files()
    elif state == STATE_PHOTOS:
        draw_photos()
    elif state == STATE_SEND:
        draw_send()
    elif state == STATE_TRANSFER:
        draw_transfer()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if state == STATE_HOME:
                if exit_rect.collidepoint(mx,my):
                    pygame.quit()
                    sys.exit()
                elif r_lock.collidepoint(mx,my):
                    if unlocked:
                        unlocked = False
                    else:
                        state = STATE_PIN
                        pin_input = ""
                        pin_error = False
                elif unlocked:
                    if r_files.collidepoint(mx,my):
                        fetch_files(); scroll_offset=0; state=STATE_FILES
                    elif r_photos.collidepoint(mx,my):
                        fetch_photos(); scroll_offset=0; state=STATE_PHOTOS
                    elif r_send.collidepoint(mx,my):
                        fetch_devices(); state=STATE_SEND

            elif state == STATE_PIN:
                for key,rect in pin_rects.items():
                    if rect.collidepoint(mx,my):
                        if key=='X':
                            pin_input=pin_input[:-1]
                            pin_error=False
                        elif key=='OK':
                            if pin_input==correct_pin:
                                unlocked=True; state=STATE_HOME
                            else:
                                pin_error=True; pin_input=""
                        else:
                            if len(pin_input)<4:
                                pin_input+=key
                                if len(pin_input)==4:
                                    if pin_input==correct_pin:
                                        unlocked=True; state=STATE_HOME
                                    else:
                                        pin_error=True; pin_input=""

            elif state == STATE_FILES:
                if back_rect.collidepoint(mx,my):
                    state=STATE_HOME
                for fname,dl,de in file_rects:
                    if de.collidepoint(mx,my):
                        delete_file(fname)
                        fetch_files()

            elif state == STATE_PHOTOS:
                if back_rect.collidepoint(mx,my):
                    state=STATE_HOME

            elif state == STATE_SEND:
                if back_rect.collidepoint(mx,my):
                    state=STATE_HOME

        if event.type == pygame.MOUSEWHEEL:
            scroll_offset = max(0, scroll_offset - event.y*20)

    now = pygame.time.get_ticks()
    if now - last_storage_tick > 5000:
        fetch_storage()
        last_storage_tick = now

    pygame.display.flip()