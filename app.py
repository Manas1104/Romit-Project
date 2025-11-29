import tkinter as tk
from tkinter import messagebox
import re, random, threading, time
import winsound
import sys

MODES = {"A": "Polished & Mild","B": "Chaotic but Playable","C": "Unhinged Chaos","D": "Hardcore Hell"}
INSULTS = ["You nincompoop!", "Try harder, fool!", "Is that all you got?", "Pathetic attempt!", "Epic fail!"]

class Game:
    def _init_(self, root, mode):
        self.root = root
        self.mode = mode
        self.fire = 0
        self.chosen_animal = random.choice(["cat","dog","fox","owl","bear"])
        self.root.title("Password Game – Mode " + mode)
        self.root.geometry("600x450")
        self.root.configure(bg="#222")  # static background color

        self.start_time = time.time()  # Track game start

        self.msg = tk.StringVar()
        self.msg.set("Enter a password… if you dare.")
        tk.Label(root,textvariable=self.msg,bg="#222",fg="white",font=("Arial",14),wraplength=560).pack(pady=20)

        self.show_password = tk.BooleanVar(value=False)
        self.entry = tk.Entry(root,font=("Arial",16),width=32,show="*")
        self.entry.pack(pady=10)

        tk.Checkbutton(root,text="Show Password",variable=self.show_password,bg="#222",fg="white",
                       command=self.toggle_password).pack(pady=5)

        tk.Button(root,text="Submit",command=self.check,bg="#444",fg="white",font=("Arial",14)).pack(pady=10)
        tk.Button(root,text="Give Up",command=self.give_up,bg="#555",fg="white",font=("Arial",12)).pack(pady=5)

        # Turkey & Egg as labels (no files)
        if mode in ["C","D"]:
            self.turkey_label = tk.Label(root,text="🦃",font=("Arial",20),bg="#222")
            self.turkey_label.place(x=400,y=300)
        if mode in ["B","C","D"]:
            self.egg_label = tk.Label(root,text="🥚",font=("Arial",20),bg="#222")
            self.egg_label.place(x=50,y=300)

        self.rules = self.generate_rules()
        self.original_rules = self.rules.copy()  # Keep original rules for reference

        # Schedule smooth dynamic difficulty check
        self.root.after(60000, self.dynamic_difficulty_check)  # every 60 seconds
        # Schedule 10-minute explosion
        self.root.after(600000, self.explode_game)  # 10 minutes = 600,000ms

    def toggle_password(self):
        self.entry.config(show="" if self.show_password.get() else "*")

    def generate_rules(self):
        base = [
            lambda p: len(p)>=6 or self.fail("Make it longer."),
            lambda p: any(x.isdigit() for x in p) or self.fail("Add a number."),
            lambda p: any(x.isupper() for x in p) or self.fail("SHOUT one letter."),
            lambda p: self.chosen_animal in p.lower() or self.fail(f"Where is the {self.chosen_animal}?"),
            lambda p: sum(int(x) for x in re.findall(r"\d",p))==10 or self.fail("Digits must add to 10."),
            lambda p: " " not in p or self.fail("No spaces."),
        ]
        if self.mode=="A": return base
        if self.mode=="B": return base + [lambda p: "egg" in p.lower() or self.fail("Include the egg!")]
        if self.mode=="C": return base + [
            lambda p: "egg" in p.lower() or self.fail("Find the moving egg!"),
            lambda p: self.fire<2 or self.fail("🔥 Fire burned it."),
            lambda p: "gobble" in p.lower() or self.fail("Turkey wants gobble."),
        ]
        if self.mode=="D": return base + [
            lambda p: "egg" in p.lower() and "fire" in p.lower() or self.fail("Need egg AND fire!"),
            lambda p: p.count("A")==2 or self.fail("Exactly 2 capital A's."),
            lambda p: any(x in p for x in "#@$&") or self.fail("Add 1 special char."),
            lambda p: p[::-1]!=p or self.fail("No palindromes allowed!"),
        ]

    def fail(self, message):
        insult = random.choice(INSULTS)
        self.msg.set(f"❌ {message} {insult}")
        self.fire += 1
        self.shake_window()
        if self.mode in ["C","D"]:
            self.move_turkey()
            self.hatch_egg()
            threading.Thread(target=self.play_sound).start()
        return False

    def check(self):
        pwd = self.entry.get()
        for rule in self.rules:
            if rule(pwd) is False: return
        messagebox.showinfo("Victory","🎉 Password accepted… for now.")
        self.root.destroy()

    def give_up(self):
        if messagebox.askyesno("Give Up","Do you really want to give up?"):
            self.root.destroy()

    # ---------------- Chaos Effects ----------------
    def shake_window(self):
        x, y = self.root.winfo_x(), self.root.winfo_y()
        for _ in range(5):
            for dx,dy in [(-10,0),(10,0),(0,-10),(0,10)]:
                self.root.geometry(f"+{x+dx}+{y+dy}")
                self.root.update()
                time.sleep(0.02)
        self.root.geometry(f"+{x}+{y}")

    def move_turkey(self):
        if hasattr(self,"turkey_label"):
            x, y = random.randint(0,500), random.randint(100,350)
            self.turkey_label.place(x=x,y=y)

    def hatch_egg(self):
        if hasattr(self,"egg_label"):
            self.egg_label.config(text="🐣")
            self.root.after(1000, lambda: self.egg_label.config(text="🥚"))

    def play_sound(self):
        for _ in range(2):
            winsound.Beep(800+random.randint(0,400),150)
            time.sleep(0.05)

    # ---------------- Smooth Dynamic Difficulty ----------------
    def dynamic_difficulty_check(self):
        elapsed = time.time() - self.start_time
        if elapsed > 180:  # After 3 minutes
            relaxed_rules = []
            for r in self.rules:
                try:
                    test_pwd = "Aa1"+self.chosen_animal+"egg"
                    if r(test_pwd) is not False:
                        relaxed_rules.append(r)
                except:
                    continue
            if len(relaxed_rules) < len(self.rules):
                self.rules = relaxed_rules
                self.msg.set(f"⏱ Time's passing… some rules are easing.")
        self.root.after(60000, self.dynamic_difficulty_check)  # check again in 1 min

    # ---------------- 10-minute Explosion ----------------
    def explode_game(self):
        if self.root.winfo_exists():
            explosion = tk.Toplevel(self.root)
            explosion.attributes("-fullscreen", True)
            explosion.configure(bg="red")
            tk.Label(explosion, text="💥 BOOM! 💥", font=("Arial", 80), fg="yellow", bg="red").pack(expand=True)
            self.root.withdraw()
            threading.Thread(target=self.play_explosion_sound, args=(explosion,)).start()

    def play_explosion_sound(self, explosion):
        for _ in range(10):
            winsound.Beep(1000+random.randint(0,500), 150)
            time.sleep(0.05)
        time.sleep(1)
        explosion.destroy()
        self.restart_game()

    def restart_game(self):
        python = sys.executable
        self.root.destroy()
        threading.Thread(target=lambda: _import_("os").execv(python, [python] + sys.argv)).start()

def choose_mode():
    picker = tk.Tk()
    picker.title("Select Mode")
    picker.geometry("350x260")
    picker.configure(bg="#222")
    tk.Label(picker,text="Choose a Password Game Mode:",fg="white",bg="#222",font=("Arial",14)).pack(pady=20)
    def start(mode):
        picker.destroy()
        root = tk.Tk()
        Game(root, mode)
        root.mainloop()
    for m,desc in MODES.items():
        tk.Button(picker,text=f"{m} — {desc}",width=25,bg="#444",fg="white",font=("Arial",12),
                  command=lambda mm=m: start(mm)).pack(pady=5)
    picker.mainloop()

choose_mode()
