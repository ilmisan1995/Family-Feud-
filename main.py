import pygame
import sys

# --- INISIALISASI ---
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1561, 958
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gemini Family Feud Global - 2026 Edition")

# --- WARNA LED & FONT ---
KUNING_LED = (255, 255, 0)
REDUP_LED = (60, 60, 0)
WHITE, RED, CYAN, PURPLE = (255, 255, 255), (255, 0, 0), (0, 255, 255), (200, 0, 255)

# Font Monospace untuk estetika grid LED
font_led = pygame.font.SysFont("Courier New", 35, bold=True)
font_led_big = pygame.font.SysFont("Courier New", 70, bold=True)
font_ui = pygame.font.SysFont("Arial", 22, bold=True)

# --- KONFIGURASI GLOBAL NEGARA ---
LANG_CONFIG = {
    "INDONESIA":   {"code": "id", "label": "BABAK", "total": "TOTAL"},
    "ENGLISH US":  {"code": "us", "label": "ROUND", "total": "TOTAL"},
    "ENGLISH UK":  {"code": "uk", "label": "ROUND", "total": "TOTAL"},
    "ENGLISH AUS": {"code": "aus", "label": "ROUND", "total": "TOTAL"},
    "GERMANY":     {"code": "de", "label": "RUNDE", "total": "GESAMT"},
    "POLSKA":      {"code": "pl", "label": "RUNDA", "total": "SUMA"},
    "RUSSIAN":     {"code": "ru", "label": "РАУНД", "total": "ИТОГО"}
}
lang_list = list(LANG_CONFIG.keys())

# --- FUNGSI LOAD DATA TXT ---
def load_soal_db(filename):
    db = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            blocks = f.read().split('---')
            for block in blocks:
                lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
                if not lines: continue
                h = lines[0].split('|')
                ans = []
                for l in lines[1:9]:
                    p = l.split(',')
                    ans.append({"txt": p[0].strip(), "pts": int(p[1]), "rev": False})
                db.append({"q1": h[0].strip(), "q2": h[1].strip(), "mult": int(h[2]), "a": ans})
    except:
        db = [{"q1": "FILE SOAL.TXT ERROR", "q2": "ATAU TIDAK DITEMUKAN", "mult": 1, "a": []}]
    return db

# --- STATE GAME ---
db_soal = load_soal_db('soal.txt')
cur_idx = 0
st = {
    "is_fm": False, "is_edit": False, "is_set": False,
    "lang_idx": 0, "vol": 0.5, "wrong": 0,
    "sc_a": 0, "sc_b": 0, "round_sc": 0, "mult": 1,
    "names": ["TIM A", "TIM B"],
    "act_in": None, "buf": ""
}

# --- ASSETS ---
logos = {}
sfx = {"benar": {}, "salah": {}}
for l in lang_list:
    c = LANG_CONFIG[l]["code"]
    try:
        raw = pygame.image.load(f"logos/logo_{c}.png").convert_alpha()
        ls = pygame.Surface(raw.get_size(), pygame.SRCALPHA)
        ls.fill(KUNING_LED); ls.blit(raw, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
        logos[c] = pygame.transform.scale(ls, (180, 100))
        sfx["benar"][c] = pygame.mixer.Sound(f"sfx/{c}_benar.wav")
        sfx["salah"][c] = pygame.mixer.Sound(f"sfx/{c}_salah.wav")
    except: pass

fm_data = {"p1": [{"txt": "", "pts": 0, "sh_t": False, "sh_p": False} for _ in range(5)],
           "p2": [{"txt": "", "pts": 0, "sh_t": False, "sh_p": False} for _ in range(5)], "total": 0}

# --- RENDERER ---
def draw_led(text, pos, font=font_led, color=KUNING_LED, center=False):
    surf = font.render(str(text).upper(), True, color)
    rect = surf.get_rect(center=pos) if center else surf.get_rect(topleft=pos)
    screen.blit(surf, rect)

def play_sfx(k):
    c = LANG_CONFIG[lang_list[st["lang_idx"]]]["code"]
    if c in sfx[k] and sfx[k][c]:
        sfx[k][c].set_volume(st["vol"]); sfx[k][c].play()

# --- MAIN LOOP ---
def main():
    global cur_idx, fm_data
    clock = pygame.time.Clock()
    bg = pygame.image.load('board.png')
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

    while True:
        screen.blit(bg, (0, 0))
        cur_l = LANG_CONFIG[lang_list[st["lang_idx"]]]
        soal = db_soal[cur_idx]
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                # Menu Controls
                if e.key == pygame.K_b: st["is_set"] = not st["is_set"]; st["is_edit"] = False
                if e.key == pygame.K_e: st["is_edit"] = not st["is_edit"]; st["is_set"] = False
                
                if st["is_edit"] or st["is_set"]:
                    if e.key == pygame.K_RETURN and st["act_in"]:
                        c, i, f = st["act_in"]; v = st["buf"]
                        if c == "name": st["names"][i] = v
                        elif c == "vol": st["vol"] = max(0, min(1, int(v)/100))
                        elif c == "fm":
                            if f == "t": fm_data[i][c]["txt"] = v[:12]; st["act_in"] = ("fm", i, "p"); st["buf"] = ""; continue
                            else: fm_data[i][c]["pts"] = int(v) if v.isdigit() else 0
                        st["act_in"] = None; st["buf"] = ""
                    elif e.key == pygame.K_BACKSPACE: st["buf"] = st["buf"][:-1]
                    else:
                        if st["is_set"]:
                            if e.key == pygame.K_a: st["act_in"] = ("name", 0, ""); st["buf"] = ""
                            if e.key == pygame.K_l: st["act_in"] = ("name", 1, ""); st["buf"] = ""
                            if e.key == pygame.K_v: st["act_in"] = ("vol", 0, ""); st["buf"] = ""
                            if e.key == pygame.K_g: st["lang_idx"] = (st["lang_idx"]+1)%len(lang_list); play_sfx("benar")
                        elif st["is_edit"] and st["is_fm"]:
                            if pygame.K_1 <= e.key <= pygame.K_5: st["act_in"] = ("fm", e.key-pygame.K_1, "p1"); st["buf"] = ""
                            if pygame.K_6 <= e.key <= pygame.K_0: st["act_in"] = ("fm", (4 if e.key==pygame.K_0 else e.key-pygame.K_6), "p2"); st["buf"] = ""
                        st["buf"] += e.unicode if e.key not in [pygame.K_RETURN, pygame.K_BACKSPACE, pygame.K_e, pygame.K_b] else ""
                else:
                    # Gameplay
                    if e.key == pygame.K_f: st["is_fm"] = True
                    if e.key == pygame.K_m: st["is_fm"] = False
                    if e.key == pygame.K_SPACE: st["wrong"] = 45; play_sfx("salah")
                    if e.key == pygame.K_n: cur_idx = (cur_idx+1)%len(db_soal); st["round_sc"] = 0; st["mult"] = db_soal[cur_idx]["mult"]
                    
                    if not st["is_fm"]:
                        if pygame.K_1 <= e.key <= pygame.K_8:
                            i = e.key-pygame.K_1
                            if i < len(soal["a"]) and not soal["a"][i]["rev"]:
                                soal["a"][i]["rev"] = True; st["round_sc"] += soal["a"][i]["pts"]*st["mult"]; play_sfx("benar")
                        if e.key == pygame.K_LEFT: st["sc_a"] += st["round_sc"]; st["round_sc"] = 0
                        if e.key == pygame.K_RIGHT: st["sc_b"] += st["round_sc"]; st["round_sc"] = 0
                    else:
                        p1_pts = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t]
                        if e.key in p1_pts:
                            i = p1_pts.index(e.key)
                            if not fm_data["p1"][i]["sh_p"]: fm_data["p1"][i]["sh_p"] = True; fm_data["total"] += fm_data["p1"][i]["pts"]; play_sfx("benar")

        # --- DRAW ---
        c_code = cur_l["code"]
        if c_code in logos: screen.blit(logos[c_code], (WIDTH//2 - 90, 140))

        draw_led(st["names"][0], (150, 40), font_ui, center=True)
        draw_led(st["sc_a"], (150, 100), font_led_big, center=True)
        draw_led(cur_l["label"], (780, 40), font_ui, center=True)
        draw_led(st["round_sc"], (780, 100), font_led_big, center=True)
        draw_led(st["names"][1], (1410, 40), font_ui, center=True)
        draw_led(st["score_b"] if "score_b" in st else st["sc_b"], (1410, 100), font_led_big, center=True)

        if not st["is_fm"]:
            draw_led(soal["q1"], (110, 185), font_ui)
            draw_led(soal["q2"], (110, 235), font_ui)
            for i in range(8):
                y = 338 + (i * 64)
                if i < len(soal["a"]) and (soal["a"][i]["rev"] or st["is_edit"]):
                    draw_led(soal["a"][i]["txt"], (125, y))
                    draw_led(soal["a"][i]["pts"], (1385, y))
                else: draw_led("."*30, (125, y), color=REDUP_LED)
        else:
            for i in range(5):
                y = 402 + (i * 64)
                if fm_data["p1"][i]["sh_t"] or st["is_edit"]: draw_led(fm_data["p1"][i]["txt"], (125, y))
                if fm_data["p1"][i][ "sh_p"] or st["is_edit"]: draw_led(fm_data["p1"][i]["pts"], (650, y))
                if fm_data["p2"][i]["sh_t"] or st["is_edit"]: draw_led(fm_data["p2"][i]["txt"], (850, y))
                if fm_data["p2"][i]["sh_p"] or st["is_edit"]: draw_led(fm_data["p2"][i]["pts"], (1385, y))
            draw_led(f"{cur_l['total']}: {fm_data['total']}", (810, 880), font_led_big, center=True)

        if st["is_set"]: draw_led(f"SET: (G) LANG: {lang_list[st['lang_idx']]} | (V) VOL: {int(st['vol']*100)}%", (WIDTH//2, 250), font_ui, color=PURPLE, center=True)
        if st["act_in"]: draw_led(f"TYPE: {st['buf']}_", (WIDTH//2, 300), font_led, color=CYAN, center=True)
        if st["wrong"] > 0:
            draw_led("X", (WIDTH//2, HEIGHT//2), pygame.font.SysFont("Arial", 500), color=RED, center=True)
            st["wrong"] -= 1

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__": main()
