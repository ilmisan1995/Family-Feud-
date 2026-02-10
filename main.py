import pygame
import sys

# --- INISIALISASI ---
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1561, 958
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Family Feud Global Pro - LED Edition")

# --- KONFIGURASI VISUAL ---
LED_YELLOW = (255, 255, 0)
DARK_YELLOW = (60, 60, 0)
WHITE, RED, CYAN, PURPLE = (255, 255, 255), (255, 0, 0), (0, 255, 255), (200, 0, 255)

# Font Monospace untuk kesan LED
font_led = pygame.font.SysFont("Courier New", 35, bold=True)
font_led_big = pygame.font.SysFont("Courier New", 70, bold=True)
font_ui = pygame.font.SysFont("Arial", 22, bold=True)

# --- DATABASE NEGARA & BAHASA ---
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

# --- DATA STATE ---
state = {
    "is_fast_money": False, "is_edit": False, "is_setting": False,
    "lang_idx": 0, "volume": 0.5, "wrong_timer": 0,
    "score_a": 0, "score_b": 0, "round_score": 0, "mult": 1,
    "names": ["TIM A", "TIM B"],
    "active_input": None, "buffer": ""
}

# --- ASSET LOADING ---
logos = {}
sfx = {"benar": {}, "salah": {}}

def load_assets():
    for lang in lang_list:
        code = LANG_CONFIG[lang]["code"]
        # Logo LED Processing
        try:
            img = pygame.image.load(f"logos/logo_{code}.png").convert_alpha()
            led_surf = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            led_surf.fill(LED_YELLOW)
            led_surf.blit(img, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            logos[code] = pygame.transform.scale(led_surf, (180, 100))
            # SFX
            sfx["benar"][code] = pygame.mixer.Sound(f"sfx/{code}_benar.wav")
            sfx["salah"][code] = pygame.mixer.Sound(f"sfx/{code}_salah.wav")
        except: pass

load_assets()

# Data Game
main_data = {"q": ["TEKAN E+Q UNTUK PERTANYAAN", ""], "a": [{"txt": "", "pts": 0, "rev": False} for _ in range(8)]}
fm_data = {"p1": [{"txt": "", "pts": 0, "sh_t": False, "sh_p": False} for _ in range(5)],
           "p2": [{"txt": "", "pts": 0, "sh_t": False, "sh_p": False} for _ in range(5)], "total": 0}

# --- HELPER FUNCTIONS ---
def draw_led(text, pos, font=font_led, color=LED_YELLOW, center=False):
    surf = font.render(str(text).upper(), True, color)
    rect = surf.get_rect(center=pos) if center else surf.get_rect(topleft=pos)
    screen.blit(surf, rect)

def play_sfx(kind):
    code = LANG_CONFIG[lang_list[state["lang_idx"]]]["code"]
    if code in sfx[kind] and sfx[kind][code]:
        sfx[kind][code].set_volume(state["volume"])
        sfx[kind][code].play()

# --- MAIN LOOP ---
def main():
    global main_data, fm_data # Untuk kemudahan edit
    clock = pygame.time.Clock()
    bg = pygame.image.load('board.png')
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

    while True:
        screen.blit(bg, (0, 0))
        cur_lang = LANG_CONFIG[lang_list[state["lang_idx"]]]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            
            if event.type == pygame.KEYDOWN:
                # Toggle Modes
                if event.key == pygame.K_b: state["is_setting"] = not state["is_setting"]; state["is_edit"] = False; state["active_input"] = None
                if event.key == pygame.K_e: state["is_edit"] = not state["is_edit"]; state["is_setting"] = False; state["active_input"] = None
                
                if state["is_edit"] or state["is_setting"]:
                    if event.key == pygame.K_RETURN and state["active_input"]:
                        cat, idx, field = state["active_input"]
                        val = state["buffer"]
                        if cat == "name": state["names"][idx] = val
                        elif cat == "vol": state["volume"] = max(0, min(1, int(val)/100))
                        elif cat == "mq": main_data["q"][idx] = val
                        elif cat == "ma": 
                            if field == "t": main_data["a"][idx]["txt"] = val[:36]; state["active_input"] = ("ma", idx, "p"); state["buffer"] = ""; continue
                            else: main_data["a"][idx]["pts"] = int(val) if val.isdigit() else 0
                        elif cat == "fm":
                            p = field # field holds 'p1' or 'p2'
                            if not fm_data[p][idx]["txt"]: fm_data[p][idx]["txt"] = val[:12]; state["buffer"] = ""; continue
                            else: fm_data[p][idx]["pts"] = int(val) if val.isdigit() else 0
                        state["active_input"] = None; state["buffer"] = ""
                    elif event.key == pygame.K_BACKSPACE: state["buffer"] = state["buffer"][:-1]
                    else:
                        if state["is_setting"]:
                            if event.key == pygame.K_a: state["active_input"] = ("name", 0, ""); state["buffer"] = ""
                            if event.key == pygame.K_l: state["active_input"] = ("name", 1, ""); state["buffer"] = ""
                            if event.key == pygame.K_v: state["active_input"] = ("vol", 0, ""); state["buffer"] = ""
                            if event.key == pygame.K_g: state["lang_idx"] = (state["lang_idx"] + 1) % len(lang_list); play_sfx("benar")
                        elif state["is_edit"]:
                            if not state["is_fast_money"]:
                                if event.key == pygame.K_q: state["active_input"] = ("mq", 0, ""); state["buffer"] = ""
                                if event.key == pygame.K_w: state["active_input"] = ("mq", 1, ""); state["buffer"] = ""
                                if pygame.K_1 <= event.key <= pygame.K_8: state["active_input"] = ("ma", event.key-pygame.K_1, "t"); state["buffer"] = ""
                            else:
                                if pygame.K_1 <= event.key <= pygame.K_5: state["active_input"] = ("fm", event.key-pygame.K_1, "p1"); state["buffer"] = ""
                                if pygame.K_6 <= event.key <= pygame.K_0: state["active_input"] = ("fm", (4 if event.key==pygame.K_0 else event.key-pygame.K_6), "p2"); state["buffer"] = ""
                        state["buffer"] += event.unicode if event.key not in [pygame.K_RETURN, pygame.K_BACKSPACE, pygame.K_e, pygame.K_b] else ""

                else: # GAMEPLAY
                    if event.key == pygame.K_f: state["is_fast_money"] = True
                    if event.key == pygame.K_m: state["is_fast_money"] = False
                    if event.key == pygame.K_SPACE: state["wrong_timer"] = 45; play_sfx("salah")
                    
                    if not state["is_fast_money"]:
                        if pygame.K_1 <= event.key <= pygame.K_8:
                            i = event.key-pygame.K_1
                            if not main_data["a"][i]["rev"]: main_data["a"][i]["rev"] = True; state["round_score"] += main_data["a"][i]["pts"]*state["mult"]; play_sfx("benar")
                        if event.key == pygame.K_s: state["mult"] = 1
                        if event.key == pygame.K_d: state["mult"] = 2
                        if event.key == pygame.K_t: state["mult"] = 3
                        if event.key == pygame.K_LEFT: state["score_a"] += state["round_score"]; state["round_score"] = 0
                        if event.key == pygame.K_RIGHT: state["score_b"] += state["round_score"]; state["round_score"] = 0
                    else:
                        # Fast Money Reveal Logic (1-5, 6-0, Q-T, Y-P)
                        p1_keys = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t]
                        if event.key in p1_keys: 
                            i = p1_keys.index(event.key)
                            if not fm_data["p1"][i]["sh_p"]: fm_data["p1"][i]["sh_p"] = True; fm_data["total"] += fm_data["p1"][i]["pts"]; play_sfx("benar")

        # --- DRAWING ---
        # Logo LED
        code = cur_lang["code"]
        if code in logos: screen.blit(logos[code], (WIDTH//2 - 90, 140))

        # Scores & Names
        draw_led(state["names"][0], (150, 40), font_ui, center=True)
        draw_led(state["score_a"], (150, 100), font_led_big, center=True)
        draw_led(cur_lang["label"], (780, 40), font_ui, center=True)
        draw_led(state["round_score"], (780, 100), font_led_big, center=True)
        draw_led(state["names"][1], (1410, 40), font_ui, center=True)
        draw_led(state["score_b"], (1410, 100), font_led_big, center=True)

        if not state["is_fast_money"]:
            draw_led(main_data["q"][0], (110, 185), font_ui)
            draw_led(main_data["q"][1], (110, 235), font_ui)
            for i in range(8):
                y = 338 + (i * 64)
                if main_data["a"][i]["rev"] or state["is_edit"]:
                    draw_led(main_data["a"][i]["txt"], (125, y))
                    draw_led(main_data["a"][i]["pts"], (1385, y))
                else: draw_led("."*30, (125, y), color=DARK_YELLOW)
        else:
            for i in range(5):
                y = 402 + (i * 64)
                if fm_data["p1"][i]["sh_t"] or state["is_edit"]: draw_led(fm_data["p1"][i]["txt"], (125, y))
                if fm_data["p1"][i]["sh_p"] or state["is_edit"]: draw_led(fm_data["p1"][i]["pts"], (650, y))
                if fm_data["p2"][i]["sh_t"] or state["is_edit"]: draw_led(fm_data["p2"][i]["txt"], (850, y))
                if fm_data["p2"][i]["sh_p"] or state["is_edit"]: draw_led(fm_data["p2"][i]["pts"], (1385, y))
            draw_led(f"{cur_lang['total']}: {fm_data['total']}", (810, 880), font_led_big, center=True)

        if state["is_setting"]: draw_led(f"SETTING: (G) LANG: {lang_list[state['lang_idx']]} | (V) VOL: {int(state['volume']*100)}%", (WIDTH//2, 250), font_ui, color=PURPLE, center=True)
        if state["active_input"]: draw_led(f"TYPE: {state['buffer']}_", (WIDTH//2, 300), font_led, color=CYAN, center=True)

        if state["wrong_timer"] > 0:
            draw_led("X", (WIDTH//2, HEIGHT//2), pygame.font.SysFont("Arial", 500), color=RED, center=True)
            state["wrong_timer"] -= 1

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__": main()
