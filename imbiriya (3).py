#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Имбирия пряников — ивент I (tkinter, только стандартная библиотека)."""

import json
import os
import random
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox

CODE = "имбирь12"
REWARDS = [50, 75, 100, 135, 150, 190, 210, 250, 300, 320]
START = datetime(2026, 11, 27, 15, 0, 0)  # локальное время компьютера

# --- Игра «Почисти мандарин» ---
TRIES_PER_DAY = 3
GAME_FROM = datetime(2026, 11, 24, 0, 0, 0)   # игра открыта уже сейчас
GAME_UNTIL = datetime(2026, 12, 1, 15, 0, 0)  # и закрывается 1 декабря в 15:00
CLICKS_TO_PEEL = 5
# (название, пряников, шанс в %) — сумма шансов = 100
TANGERINES = [
    ("Гнилой мандарин 🤢", 0, 30),
    ("Обычный мандарин", 5, 30),
    ("Сочный мандарин", 15, 20),
    ("Сладкий мандарин", 30, 12),
    ("Золотой мандарин ✨", 60, 6),
    ("Имбирный мандарин 🍪", 100, 2),
]
SAVE_FILE = os.path.join(os.path.expanduser("~"), ".imbiriya_save.json")

BG, CARD, TX, MUT = "#fff6e8", "#ffffff", "#4a2a14", "#8a6a50"
AC, OK, BD = "#c4672a", "#3f8f4f", "#ecd3b4"


def load():
    try:
        with open(SAVE_FILE, encoding="utf-8") as f:
            d = json.load(f)
        return {"claimed": list(d.get("claimed", [])),
                "bal": int(d.get("bal", 0)),
                "rub": int(d.get("rub", 0)),
                "tries_date": str(d.get("tries_date", "")),
                "tries_used": int(d.get("tries_used", 0))}
    except Exception:
        return {"claimed": [], "bal": 0, "rub": 0, "tries_date": "", "tries_used": 0}


def save(state):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False)
    except Exception:
        pass


def draw_ginger(c, ox=0, oy=0):
    """Рисует Имбирника на canvas."""
    def P(*pts):
        return [v + (ox if i % 2 == 0 else oy) for i, v in enumerate(pts)]

    body = dict(fill="#c98a4b", outline="#7a3f18", width=2)
    # руки
    c.create_polygon(P(45, 62, 12, 74, 10, 86, 24, 88, 52, 80), **body)
    c.create_polygon(P(75, 62, 108, 74, 110, 86, 96, 88, 68, 80), **body)
    # ноги
    c.create_polygon(P(44, 90, 28, 130, 30, 138, 52, 132, 60, 108,
                       68, 132, 90, 138, 92, 130, 76, 90), **body)
    # тело и голова
    c.create_rectangle(40 + ox, 56 + oy, 80 + ox, 106 + oy, **body)
    c.create_oval(34 + ox, 8 + oy, 86 + ox, 60 + oy, **body)
    # глаза
    for x in (51, 69):
        c.create_oval(x - 4 + ox, 26 + oy, x + 4 + ox, 34 + oy, fill="white", outline="")
        c.create_oval(x - 2 + ox, 28 + oy, x + 2 + ox, 32 + oy, fill=TX, outline="")
    # щёки и улыбка
    c.create_oval(39 + ox, 37 + oy, 45 + ox, 43 + oy, fill="#e8a0a0", outline="")
    c.create_oval(75 + ox, 37 + oy, 81 + ox, 43 + oy, fill="#e8a0a0", outline="")
    c.create_arc(50 + ox, 32 + oy, 70 + ox, 50 + oy, start=200, extent=140,
                 style="arc", outline="white", width=3)
    # пуговицы и глазурь
    c.create_oval(56 + ox, 68 + oy, 64 + ox, 76 + oy, fill="#d33333", outline="")
    c.create_oval(56 + ox, 84 + oy, 64 + ox, 92 + oy, fill="#3a9a4a", outline="")
    c.create_line(P(16, 80, 26, 82), fill="white", width=3)
    c.create_line(P(104, 80, 94, 82), fill="white", width=3)


def fmt_left(delta):
    s = max(0, int(delta.total_seconds()))
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return (f"{d} д " if d else "") + f"{h} ч {m} м {s} с"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Имбирия пряников — ивент I")
        self.configure(bg=BG)
        self.geometry("520x720")
        self.minsize(480, 600)
        self.state_ = load()
        self.gate()

    # ---------- экран с кодом ----------
    def gate(self):
        self.gate_frame = tk.Frame(self, bg=BG)
        self.gate_frame.pack(expand=True)
        c = tk.Canvas(self.gate_frame, width=120, height=145, bg=BG, highlightthickness=0)
        c.pack()
        draw_ginger(c)
        tk.Label(self.gate_frame, text="Имбирия пряников", bg=BG, fg=TX,
                 font=("Arial", 22, "bold")).pack(pady=(8, 0))
        tk.Label(self.gate_frame, text="Ивент I · введите код для запуска",
                 bg=BG, fg=MUT, font=("Arial", 11)).pack(pady=(0, 10))
        self.code_var = tk.StringVar()
        e = tk.Entry(self.gate_frame, textvariable=self.code_var, font=("Arial", 14),
                     justify="center", width=18)
        e.pack(pady=4)
        e.focus_set()
        e.bind("<Return>", lambda _e: self.check_code())
        tk.Button(self.gate_frame, text="Войти", command=self.check_code,
                  bg=AC, fg="white", font=("Arial", 12, "bold"), relief="flat",
                  padx=18, pady=6).pack(pady=8)
        self.err = tk.Label(self.gate_frame, text="", bg=BG, fg="#d33333")
        self.err.pack()

    def check_code(self):
        if self.code_var.get().strip().lower() == CODE:
            self.gate_frame.destroy()
            self.main_screen()
        else:
            self.err.config(text="Неверный код")

    # ---------- главный экран ----------
    def main_screen(self):
        top = tk.Frame(self, bg=CARD, highlightbackground=BD, highlightthickness=1)
        top.pack(fill="x", padx=12, pady=(12, 6))
        c = tk.Canvas(top, width=120, height=145, bg=CARD, highlightthickness=0)
        c.pack(side="left", padx=8, pady=8)
        draw_ginger(c)
        info = tk.Frame(top, bg=CARD)
        info.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(info, text="Имбирник · твои пряники", bg=CARD, fg=MUT).pack(anchor="w", pady=(10, 0))
        self.bal_lbl = tk.Label(info, text="", bg=CARD, fg=TX, font=("Arial", 22, "bold"))
        self.bal_lbl.pack(anchor="w")
        self.rub_lbl = tk.Label(info, text="", bg=CARD, fg=MUT)
        self.rub_lbl.pack(anchor="w")
        self.say_lbl = tk.Label(info, text="Привет! Я Имбирник!", bg=BG, fg=MUT,
                                wraplength=250, justify="left", padx=8, pady=6)
        self.say_lbl.pack(anchor="w", pady=8, fill="x")

        ex = tk.Frame(self, bg=CARD, highlightbackground=BD, highlightthickness=1)
        ex.pack(fill="x", padx=12, pady=6)
        tk.Label(ex, text="Обмен на деньги", bg=CARD, fg=TX,
                 font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(8, 0))
        tk.Label(ex, text="10 пряников = 12 рублей (кратно 10)", bg=CARD, fg=MUT).pack(anchor="w", padx=10)
        row = tk.Frame(ex, bg=CARD)
        row.pack(fill="x", padx=10, pady=8)
        self.amt = tk.Spinbox(row, from_=10, to=100000, increment=10, width=8, font=("Arial", 12))
        self.amt.pack(side="left")
        tk.Button(row, text="Обменять", command=self.do_exchange, bg=AC, fg="white",
                  relief="flat", padx=10).pack(side="left", padx=6)
        tk.Button(row, text="Всё", command=lambda: self.do_exchange(all_=True), bg=AC,
                  fg="white", relief="flat", padx=10).pack(side="left")

        self.game_btn = tk.Button(self, text="", command=self.open_game, bg="#f5821f",
                                  fg="white", font=("Arial", 12, "bold"), relief="flat", pady=8)
        self.game_btn.pack(fill="x", padx=12, pady=6)

        box = tk.Frame(self, bg=CARD, highlightbackground=BD, highlightthickness=1)
        box.pack(fill="both", expand=True, padx=12, pady=(6, 12))
        self.rows = []
        for i, r in enumerate(REWARDS):
            f = tk.Frame(box, bg=CARD)
            f.pack(fill="x", padx=8, pady=3)
            n = tk.Label(f, text=str(i + 1), bg="#e8a05a", fg="white", width=3,
                         font=("Arial", 11, "bold"))
            n.pack(side="left", padx=(0, 8))
            t = tk.Frame(f, bg=CARD)
            t.pack(side="left", fill="x", expand=True)
            tk.Label(t, text=f"День {i + 1}: {r} пряников", bg=CARD, fg=TX,
                     font=("Arial", 11, "bold")).pack(anchor="w")
            sub = tk.Label(t, text="", bg=CARD, fg=MUT, font=("Arial", 9))
            sub.pack(anchor="w")
            btn = tk.Button(f, text="🔒", width=10, relief="flat",
                            command=lambda k=i: self.claim(k))
            btn.pack(side="right")
            self.rows.append((n, sub, btn))
        self.refresh()
        self.tick()

    def say(self, text):
        self.say_lbl.config(text=text)

    def unlock_time(self, i):
        return START + timedelta(days=i)

    def claim(self, i):
        s = self.state_
        if i in s["claimed"] or datetime.now() < self.unlock_time(i):
            return
        s["claimed"].append(i)
        s["bal"] += REWARDS[i]
        save(s)
        self.say(f"Ура! +{REWARDS[i]} пряников!")
        self.refresh()

    def do_exchange(self, all_=False):
        s = self.state_
        try:
            n = s["bal"] if all_ else int(self.amt.get())
        except ValueError:
            messagebox.showwarning("Обмен", "Введите число.")
            return
        n = n // 10 * 10
        if n < 10 or n > s["bal"]:
            messagebox.showinfo("Обмен", "Недостаточно пряников (нужно минимум 10).")
            return
        rub = n // 10 * 12
        s["bal"] -= n
        s["rub"] += rub
        save(s)
        self.say(f"Звенят монетки! +{rub} ₽")
        self.refresh()

    # ---------- игра «Почисти мандарин» ----------
    def tries_left(self):
        s = self.state_
        today = datetime.now().strftime("%Y-%m-%d")
        if s.get("tries_date") != today:
            s["tries_date"] = today
            s["tries_used"] = 0
            save(s)
        return max(0, TRIES_PER_DAY - s["tries_used"])

    def open_game(self):
        if datetime.now() < GAME_FROM:
            messagebox.showinfo("Мандарин", f"Игра откроется {GAME_FROM:%d.%m в %H:%M}.")
            return
        if datetime.now() >= GAME_UNTIL:
            messagebox.showinfo("Мандарин", "Игра закончилась (до 1 декабря 15:00).")
            return
        if getattr(self, "game_win", None) and self.game_win.winfo_exists():
            self.game_win.lift()
            return
        w = tk.Toplevel(self)
        self.game_win = w
        w.title("Почисти мандарин")
        w.configure(bg=BG)
        w.resizable(False, False)
        tk.Label(w, text="🍊 Почисти мандарин", bg=BG, fg=TX,
                 font=("Arial", 18, "bold")).pack(pady=(10, 0))
        tk.Label(w, text=f"Кликай по мандарину {CLICKS_TO_PEEL} раз, чтобы очистить его!",
                 bg=BG, fg=MUT).pack()
        self.g_tries = tk.Label(w, text="", bg=BG, fg=TX, font=("Arial", 12, "bold"))
        self.g_tries.pack(pady=4)
        self.g_cv = tk.Canvas(w, width=240, height=240, bg=BG, highlightthickness=0, cursor="hand2")
        self.g_cv.pack()
        self.g_cv.bind("<Button-1>", self.game_click)
        self.g_msg = tk.Label(w, text="Нажми на мандарин, чтобы начать", bg=BG, fg=TX,
                              font=("Arial", 12), wraplength=300, height=2)
        self.g_msg.pack(pady=4)
        tbl = tk.Frame(w, bg=CARD, highlightbackground=BD, highlightthickness=1)
        tbl.pack(fill="x", padx=14, pady=(2, 12))
        tk.Label(tbl, text="Что можно найти:", bg=CARD, fg=TX,
                 font=("Arial", 10, "bold")).pack(anchor="w", padx=8, pady=(6, 0))
        for name, amount, chance in TANGERINES:
            tk.Label(tbl, text=f"{name}: {amount} 🍪 — шанс {chance}%", bg=CARD,
                     fg=MUT, font=("Arial", 10)).pack(anchor="w", padx=8)
        tk.Frame(tbl, bg=CARD, height=6).pack()
        self.g_clicks = 0
        self.g_active = False
        self.game_draw(0)
        self.game_update_tries()

    def game_update_tries(self):
        self.g_tries.config(text=f"Попыток сегодня: {self.tries_left()} из {TRIES_PER_DAY}")

    def game_draw(self, stage, result=None):
        c = self.g_cv
        c.delete("all")
        c.create_oval(30, 40, 210, 220, fill="#f5821f", outline="#c4561a", width=3)
        for k in range(min(stage, CLICKS_TO_PEEL)):
            ext = 360 / CLICKS_TO_PEEL
            c.create_arc(30, 40, 210, 220, start=90 + k * ext, extent=ext, fill="#ffd27a",
                         outline="#e8a05a", width=2)
        if stage >= CLICKS_TO_PEEL:
            c.create_oval(60, 70, 180, 190, fill="#ffbf4d", outline="#e8a05a", width=2)
            if result and result[1] == 0:
                c.create_text(120, 130, text="🤢", font=("Arial", 44))
        # листик и хвостик
        c.create_polygon(120, 40, 150, 14, 175, 30, 150, 44, fill="#3f8f4f", outline="#2c6a38")
        c.create_line(120, 40, 120, 28, fill="#5a3a1a", width=4)

    def game_click(self, _event):
        if not self.g_active:
            if datetime.now() >= GAME_UNTIL:
                self.g_msg.config(text="Игра закончилась.")
                return
            if self.tries_left() <= 0:
                self.g_msg.config(text="Попытки на сегодня закончились. Приходи завтра!")
                return
            self.state_["tries_used"] += 1  # попытка тратится сразу
            save(self.state_)
            self.g_active = True
            self.g_clicks = 0
            self.game_update_tries()
        self.g_clicks += 1
        self.game_draw(self.g_clicks)
        if self.g_clicks < CLICKS_TO_PEEL:
            self.g_msg.config(text=f"Чистим... {self.g_clicks}/{CLICKS_TO_PEEL}")
            return
        result = random.choices(TANGERINES, weights=[t[2] for t in TANGERINES], k=1)[0]
        self.g_active = False
        self.state_["bal"] += result[1]
        save(self.state_)
        self.game_draw(CLICKS_TO_PEEL, result)
        if result[1]:
            self.g_msg.config(text=f"{result[0]}! +{result[1]} пряников 🍪")
            self.say(f"Вкусный мандарин! +{result[1]} пряников!")
        else:
            self.g_msg.config(text=f"{result[0]}... Пряников нет, повезёт в другой раз!")
            self.say("Фу, мандарин гнилой!")
        self.game_update_tries()
        self.refresh()

    def refresh(self):
        s = self.state_
        now = datetime.now()
        left = self.tries_left()
        if now < GAME_FROM:
            self.game_btn.config(text=f"🍊 Почисти мандарин (откроется {GAME_FROM:%d.%m %H:%M})")
        elif now >= GAME_UNTIL:
            self.game_btn.config(text="🍊 Мандарин: игра закончилась")
        else:
            self.game_btn.config(text=f"🍊 Почистить мандарин (попыток: {left}/{TRIES_PER_DAY}) · до 01.12 15:00")
        self.bal_lbl.config(text=f"{s['bal']} 🍪")
        self.rub_lbl.config(text=f"Получено рублей: {s['rub']} ₽")
        for i, (n, sub, btn) in enumerate(self.rows):
            t = self.unlock_time(i)
            if i in s["claimed"]:
                n.config(bg=OK)
                sub.config(text="Забрано")
                btn.config(text="Получено ✓", state="disabled", bg=BD, fg=MUT)
            elif now >= t:
                sub.config(text="Доступно сейчас!")
                btn.config(text="Забрать", state="normal", bg=AC, fg="white")
            else:
                sub.config(text=f"Откроется {t:%d.%m %H:%M} · через {fmt_left(t - now)}")
                btn.config(text="🔒", state="disabled", bg=BD, fg=MUT)

    def tick(self):
        self.refresh()
        self.after(1000, self.tick)


if __name__ == "__main__":
    App().mainloop()
