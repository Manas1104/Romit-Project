import streamlit as st
import random
import time
import re
import json
import os

# ------------------------------------
# Page Setup
# ------------------------------------
st.set_page_config(page_title="Chaotic Password Game", page_icon="🔥", layout="centered")

# ------------------------------------
# Persistent Local Scoreboard
# ------------------------------------
SCORE_FILE = "scoreboard.json"

if not os.path.exists(SCORE_FILE):
    with open(SCORE_FILE, "w") as f:
        json.dump({}, f)

def load_scores():
    with open(SCORE_FILE, "r") as f:
        return json.load(f)

def save_scores(scores):
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f, indent=4)

# ------------------------------------
# Initialize Session State
# ------------------------------------
if "username" not in st.session_state:
    st.session_state.username = None

if "mode" not in st.session_state:
    st.session_state.mode = "A"

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

if "fire" not in st.session_state:
    st.session_state.fire = 0

if "message" not in st.session_state:
    st.session_state.message = "Enter a password… if you dare."

if "chosen_animal" not in st.session_state:
    st.session_state.chosen_animal = random.choice(["cat","dog","fox","owl","bear"])

if "achievements" not in st.session_state:
    st.session_state.achievements = set()

# ------------------------------------
# Utility Functions
# ------------------------------------
def add_achievement(name):
    st.session_state.achievements.add(name)

def fail(msg):
    insults = [
        "You nincompoop!", "Try harder, fool!", "Try again, mortal!",
        "Pathetic attempt!", "Epic fail!", "The turkey laughs at you."
    ]
    st.session_state.fire += 1
    st.session_state.message = f"❌ {msg} {random.choice(insults)}"

    # Insanity Achievements
    if st.session_state.fire == 5:
        add_achievement("🔥 Mild Insanity")
    if st.session_state.fire == 10:
        add_achievement("💀 Total Madness")

    return False

# ------------------------------------
# Rule Generator
# ------------------------------------
def build_rules(mode):
    base = [
        lambda p: len(p)>=6 or fail("Make it longer."),
        lambda p: any(x.isdigit() for x in p) or fail("Add a number."),
        lambda p: any(x.isupper() for x in p) or fail("Add a capital letter."),
        lambda p: st.session_state.chosen_animal in p.lower() or fail(f"Where is the {st.session_state.chosen_animal}?"),
        lambda p: sum(int(x) for x in re.findall(r"\d",p))==10 or fail("Digits must add to 10."),
        lambda p: " " not in p or fail("No spaces allowed."),
    ]

    if mode == "A":
        return base

    if mode == "B":
        return base + [lambda p: "egg" in p.lower() or fail("Include the egg!")]

    if mode == "C":
        return base + [
            lambda p: "egg" in p.lower() or fail("Find the egg!"),
            lambda p: st.session_state.fire < 3 or fail("🔥 Fire burned it."),
            lambda p: "gobble" in p.lower() or fail("The turkey wants GOBBLE."),
        ]

    if mode == "D":
        return base + [
            lambda p: "egg" in p.lower() and "fire" in p.lower() or fail("Need egg + fire!"),
            lambda p: p.count("A")==2 or fail("Exactly 2 capital A's."),
            lambda p: any(x in p for x in "#@$&") or fail("Add a special character."),
            lambda p: p[::-1] != p or fail("No palindromes!"),
        ]

# ------------------------------------
# UI HEADER
# ------------------------------------
st.title("🔥 The Chaotic Password Game")
st.markdown("<h4 style='text-align:center;'>Where sanity comes to die.</h4>", unsafe_allow_html=True)

# ------------------------------------
# Username & Profile
# ------------------------------------
if not st.session_state.username:
    username = st.text_input("Enter Username to Start")
    if username:
        st.session_state.username = username
        st.rerun()
else:
    st.success(f"🎮 Player: **{st.session_state.username}**")

# ------------------------------------
# Mode Selection
# ------------------------------------
mode = st.selectbox("Choose Difficulty Mode", ["A","B","C","D"])
st.session_state.mode = mode

rules = build_rules(mode)

# ------------------------------------
# Difficulty Timer UI
# ------------------------------------
elapsed = int(time.time() - st.session_state.start_time)
st.progress(min(elapsed/600, 1.0))
st.caption(f"⏳ Time Played: {elapsed}s / 10 min")

# ------------------------------------
# Animated Moving Emojis
# ------------------------------------
turkey_x = random.randint(0, 100)
egg_x = random.randint(0, 100)

st.markdown(
    f"""
    <div style="font-size:30px; position:relative;">
        <span style="position:absolute; left:{turkey_x}%;">🦃</span>
        <span style="position:absolute; left:{egg_x}%;">🥚</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------------------------
# Sound Effects (JS)
# ------------------------------------
sound_button = """
<script>
function playSound(){
    var audio = new Audio('https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg');
    audio.play();
}
</script>
<button onclick="playSound()">🔊 Play Sound</button>
"""

st.markdown(sound_button, unsafe_allow_html=True)

# ------------------------------------
# Password Entry
# ------------------------------------
pwd = st.text_input("Enter Password", type="password")

if st.button("Submit"):
    ok = True
    for rule in rules:
        if rule(pwd) is False:
            ok = False
            break

    if ok:
        st.balloons()
