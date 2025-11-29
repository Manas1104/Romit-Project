import streamlit as st
import random, re, time

st.set_page_config(page_title="Password Game", layout="centered")

MODES = {
    "A": "Polished & Mild",
    "B": "Chaotic but Playable",
    "C": "Unhinged Chaos",
    "D": "Hardcore Hell"
}

INSULTS = [
    "You nincompoop!", "Try harder, fool!",
    "Is that all you got?", "Pathetic attempt!",
    "Epic fail!"
]

# ---------------------- STATE SETUP ----------------------
if "mode" not in st.session_state:
    st.session_state.mode = None
if "fire" not in st.session_state:
    st.session_state.fire = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "animal" not in st.session_state:
    st.session_state.animal = random.choice(["cat","dog","fox","owl","bear"])
if "egg_state" not in st.session_state:
    st.session_state.egg_state = "🥚"
if "turkey_pos" not in st.session_state:
    st.session_state.turkey_pos = random.randint(5,95)


# ---------------------- MODE PICKER ----------------------
if st.session_state.mode is None:
    st.title("🧩 The Password Game")
    st.write("Choose your chaos level:")

    for m, desc in MODES.items():
        if st.button(f"{m} — {desc}"):
            st.session_state.mode = m
            st.rerun()

    st.stop()


mode = st.session_state.mode
st.title(f"🔐 Password Game — Mode {mode}")
st.write("Enter a password… if you dare.")

# ---------------------- ANIMATED EMOJIS ----------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### {st.session_state.egg_state}")
with col2:
    if mode in ["C","D"]:
        st.markdown(f"### 🦃 (at {st.session_state.turkey_pos}%)")

st.progress(min(st.session_state.fire / 10, 1.0), text="🔥 Fire / Failure Meter")


# ---------------------- RULES GENERATOR ----------------------
def generate_rules(mode):
    base = [
        lambda p: len(p)>=6 or fail("Make it longer."),
        lambda p: any(x.isdigit() for x in p) or fail("Add a number."),
        lambda p: any(x.isupper() for x in p) or fail("SHOUT one letter."),
        lambda p: st.session_state.animal in p.lower() or fail(f"Where is the {st.session_state.animal}?"),
        lambda p: sum(int(x) for x in re.findall(r"\d",p))==10 or fail("Digits must add to 10."),
        lambda p: " " not in p or fail("No spaces allowed."),
    ]

    if mode == "A":
        return base

    if mode == "B":
        return base + [
            lambda p: "egg" in p.lower() or fail("Include the egg!")
        ]

    if mode == "C":
        return base + [
            lambda p: "egg" in p.lower() or fail("Find the moving egg!"),
            lambda p: st.session_state.fire < 2 or fail("🔥 Fire burned it."),
            lambda p: "gobble" in p.lower() or fail("Turkey wants gobble."),
        ]

    if mode == "D":
        return base + [
            lambda p: ("egg" in p.lower() and "fire" in p.lower()) or fail("Need egg AND fire!"),
            lambda p: p.count("A")==2 or fail("Exactly 2 capital A's."),
            lambda p: any(x in p for x in "#@$&") or fail("Add 1 special char."),
            lambda p: p[::-1]!=p or fail("No palindromes allowed!"),
        ]

rules = generate_rules(mode)


# ---------------------- FAIL HANDLER ----------------------
def fail(message):
    insult = random.choice(INSULTS)
    st.error(f"❌ {message} {insult}")
    st.session_state.fire += 1

    # Animate egg
    st.session_state.egg_state = "🐣"
    st.session_state.egg_state = "🥚"

    # Move turkey
    st.session_state.turkey_pos = random.randint(1, 99)

    st.stop()


# ---------------------- PASSWORD INPUT ----------------------
pwd = st.text_input("Password:", type="password")

if st.button("Submit"):
    passed_all = True
    for rule in rules:
        if rule(pwd) is False:
            passed_all = False
            break

    if passed_all:
        st.success("🎉 Password accepted… for now.")
        st.balloons()
        st.write("Game over. Restart to try another mode.")
        st.stop()


# ---------------------- GIVE UP ----------------------
if st.button("Give Up"):
    st.warning("You gave up. Understandable 😔")
    st.session_state.mode = None
    st.rerun()
