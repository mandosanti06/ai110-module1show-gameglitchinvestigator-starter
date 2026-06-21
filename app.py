import random

import streamlit as st

from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
)

# Maps the logic outcome to the player-facing direction hint.
# "Too High" means the guess was too high, so the advice is to go LOWER.
HINTS = {
    "Win": "CORRECT",
    "Too High": "TOO HIGH — GO LOWER",
    "Too Low": "TOO LOW — GO HIGHER",
}
OUTCOME_CLASS = {"Win": "win", "Too High": "high", "Too Low": "low"}

# Inline brutalist SVG icons (thick stroke, square caps, currentColor) — they
# inherit color from the element, so a single set works on either theme.
_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square" stroke-linejoin="miter">{}</svg>'
ICONS = {
    "win": _SVG.format('<path d="M4 12l5 6L20 5"/>'),                         # check
    "high": _SVG.format('<path d="M12 3v16"/><path d="M5 13l7 7 7-7"/>'),    # arrow down -> go lower
    "low": _SVG.format('<path d="M12 21V5"/><path d="M5 11l7-7 7 7"/>'),     # arrow up -> go higher
    "error": _SVG.format('<path d="M12 3l9 18H3z"/><path d="M12 10v4"/><path d="M12 17h.01"/>'),  # alert
    "over": _SVG.format('<path d="M5 5l14 14"/><path d="M19 5L5 19"/>'),     # X
}
MARK = '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="2" y="2" width="20" height="20"/></svg>'

st.set_page_config(page_title="Glitchy Guesser", page_icon="◼", layout="centered")

# ---- Sidebar settings (read first so the theme is known before we inject CSS) -
st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Normal", "Hard"], index=1)

attempt_limit_map = {"Easy": 6, "Normal": 8, "Hard": 5}
attempt_limit = attempt_limit_map[difficulty]
low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")
show_hint = st.sidebar.toggle("Show direction hint", value=True)
dark = st.sidebar.toggle("Invert (dark)", value=False)
dev_mode = st.sidebar.toggle("Dev mode", value=False)

# ---- RawBlock skin: thick borders, zero radius, no shadows, full inversion. --
# Dark mode = RawBlock's "Surface Inverted": swap ink/paper, everything else
# is expressed through border weight, not color.
# ponytail: deep BaseWeb popovers (open selectbox) aren't fully re-themed.
THEME = {
    "light": {"bg": "#FFFFFF", "ink": "#000000", "inbg": "#F0F0F0",
              "ok": "#008000", "err": "#FF0000", "muted": "#555555"},
    "dark":  {"bg": "#000000", "ink": "#FFFFFF", "inbg": "#141414",
              "ok": "#00C853", "err": "#FF3B30", "muted": "#AAAAAA"},
}
t = THEME["dark" if dark else "light"]
root_vars = ";".join(f"--{k}:{v}" for k, v in t.items())
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Work+Sans:wght@400;600;700&family=Space+Mono&display=swap');
    :root { __ROOT__ }

    .stApp { background: var(--bg); color: var(--ink); }
    .stApp, .stMarkdown, .stMarkdown p, [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p, .stApp label {
        font-family: 'Work Sans', sans-serif; color: var(--ink);
    }
    h1, h2, h3 { font-family: 'Archivo Black', sans-serif; color: var(--ink); text-transform: uppercase; }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { background: var(--bg); border-right: 3px solid var(--ink); }
    [data-testid="stSidebar"] * { color: var(--ink); }
    [data-testid="stSidebar"] h2 { font-family: 'Archivo Black', sans-serif; text-transform: uppercase; }
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: var(--inbg) !important; border: 3px solid var(--ink) !important; border-radius: 0 !important;
    }
    /* Selectbox dropdown — rendered in a body-level portal, so select globally */
    [data-testid="stSelectboxVirtualDropdown"], [data-baseweb="popover"] [role="listbox"], [data-baseweb="menu"] {
        background: var(--bg) !important; border: 3px solid var(--ink) !important; border-radius: 0 !important; box-shadow: none !important;
    }
    [data-testid="stSelectboxVirtualDropdown"] li, [data-baseweb="popover"] li[role="option"] {
        background: var(--bg) !important; color: var(--ink) !important; border-radius: 0 !important; font-family: 'Space Mono', monospace !important;
    }
    [data-testid="stSelectboxVirtualDropdown"] li:hover, [data-baseweb="popover"] li[role="option"]:hover,
    [data-baseweb="popover"] li[aria-selected="true"] {
        background: var(--ink) !important; color: var(--bg) !important;
    }
    hr { border: none !important; border-top: 3px solid var(--ink) !important; }

    /* Header / logo mark */
    .logo { display:flex; align-items:center; gap:16px; font-family:'Archivo Black',sans-serif;
            font-size:clamp(34px,8vw,60px); line-height:1; text-transform:uppercase; margin:0 0 8px; }
    .logo svg { width:46px; height:46px; color:var(--ink); flex:none; }
    .sub { font-family:'Space Mono',monospace; font-size:14px; letter-spacing:1px; color:var(--muted); margin:0 0 4px; }

    /* Buttons — square, thick border, uppercase, full inversion on hover */
    .stButton > button {
        border-radius:0 !important; border:3px solid var(--ink) !important; box-shadow:none !important;
        font-family:'Work Sans',sans-serif; font-weight:700; text-transform:uppercase; letter-spacing:2px;
        padding:10px 24px; transition:none;
    }
    [data-testid="stBaseButton-primary"] { background:var(--ink) !important; color:var(--bg) !important; }
    [data-testid="stBaseButton-primary"]:hover { background:var(--bg) !important; color:var(--ink) !important; }
    [data-testid="stBaseButton-secondary"] { background:var(--bg) !important; color:var(--ink) !important; }
    [data-testid="stBaseButton-secondary"]:hover { background:var(--ink) !important; color:var(--bg) !important; }
    .stButton > button:active { border-width:5px !important; }
    .stButton > button:disabled { background:#F5F5F5 !important; color:#999 !important; border-color:#CCC !important; opacity:1 !important; }

    /* Input — sunken grey, Space Mono, square, thick border */
    .stTextInput input {
        border-radius:0 !important; border:3px solid var(--ink) !important; background:var(--inbg) !important;
        color:var(--ink) !important; font-family:'Space Mono',monospace; font-size:15px; padding:10px 12px;
    }
    .stTextInput input::placeholder { color:var(--muted); }
    .stTextInput input:focus { border-width:5px !important; outline:none !important; box-shadow:none !important; }

    /* Stat blocks (RawBlock cards: 3px border, square) */
    .blocks { display:flex; gap:0; margin:8px 0 16px; border:3px solid var(--ink); }
    .block { flex:1; padding:16px; border-right:3px solid var(--ink); }
    .block:last-child { border-right:none; }
    .block .lbl { font-family:'Archivo Black',sans-serif; font-size:11px; letter-spacing:1px; text-transform:uppercase; color:var(--muted); }
    .block .val { font-family:'Archivo Black',sans-serif; font-size:30px; line-height:1.1; color:var(--ink); }

    /* Progress — bordered bar, solid ink fill, no gradient */
    .track { height:20px; border:3px solid var(--ink); background:var(--bg); }
    .fill { height:100%; background:var(--ink); }

    /* Feedback block — white fill, heavy 5px border in status color */
    .card { display:flex; align-items:center; gap:16px; padding:16px 20px; margin:12px 0;
            background:var(--bg); border:5px solid var(--c); }
    .card.win { --c:var(--ok); } .card.high, .card.low { --c:var(--ink); } .card.error, .card.over { --c:var(--err); }
    .card .ico { color:var(--c); flex:none; }
    .card .ico svg { width:34px; height:34px; display:block; }
    .card .t { font-family:'Archivo Black',sans-serif; font-size:20px; text-transform:uppercase; color:var(--ink); }
    .card .d { font-family:'Space Mono',monospace; font-size:13px; color:var(--muted); margin-top:2px; }

    /* History — status chips: square, 2px colored border, colored text */
    .seclbl { font-family:'Archivo Black',sans-serif; font-size:11px; letter-spacing:1px; text-transform:uppercase; color:var(--muted); margin-top:8px; }
    .pills { display:flex; flex-wrap:wrap; gap:8px; margin-top:8px; }
    .pill { font-family:'Space Mono',monospace; font-weight:700; font-size:13px; padding:4px 12px;
            border:2px solid var(--c2); color:var(--c2); background:var(--bg); }
    .pill.win { --c2:var(--ok); } .pill.high, .pill.low { --c2:var(--ink); }
    </style>
    """.replace("__ROOT__", root_vars),
    unsafe_allow_html=True,
)


def new_game_state():
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.last = None


# Start fresh on first load and whenever difficulty changes (the range changes,
# so the old secret may be out of bounds).
# ponytail: difficulty change resets the game; add a confirm dialog if that bites.
if st.session_state.get("difficulty") != difficulty:
    st.session_state.difficulty = difficulty
    new_game_state()

playing = st.session_state.status == "playing"

# ---- Header -----------------------------------------------------------------
st.markdown(
    f'<h1 class="logo">{MARK}<span>Glitchy Guesser</span></h1>'
    f'<p class="sub">GUESS THE SECRET NUMBER. THE BUGS HAVE BEEN EVICTED.</p>',
    unsafe_allow_html=True,
)

# ---- Stat blocks + progress (reflect committed state) -----------------------
left = max(0, attempt_limit - st.session_state.attempts)
st.markdown(
    f'<div class="blocks">'
    f'<div class="block"><div class="lbl">Score</div><div class="val">{st.session_state.score}</div></div>'
    f'<div class="block"><div class="lbl">Guesses left</div><div class="val">{left}</div></div>'
    f'<div class="block"><div class="lbl">Range</div><div class="val">{low}&ndash;{high}</div></div>'
    f'</div>',
    unsafe_allow_html=True,
)
pct = min(100, int(100 * st.session_state.attempts / attempt_limit))
st.markdown(f'<div class="track"><div class="fill" style="width:{pct}%"></div></div>', unsafe_allow_html=True)

# ---- Input + actions --------------------------------------------------------
raw_guess = st.text_input(
    "Enter your guess",
    key=f"guess_input_{difficulty}",
    placeholder=f"A number from {low} to {high}",
    disabled=not playing,
)
c1, c2 = st.columns([2, 1])
with c1:
    submit = st.button("Submit guess", type="primary", use_container_width=True, disabled=not playing)
with c2:
    new_game = st.button("New game", use_container_width=True)

if new_game:
    new_game_state()
    st.rerun()

if submit and playing:
    guess_int, err = parse_guess(raw_guess)
    if err:
        st.session_state.last = {"kind": "error", "title": err.upper(), "detail": ""}
    elif not (low <= guess_int <= high):  # bug #13: reject out-of-range guesses
        st.session_state.last = {"kind": "error", "title": "OUT OF RANGE", "detail": f"ENTER {low}–{high}"}
    else:
        st.session_state.attempts += 1
        outcome = check_guess(guess_int, st.session_state.secret)
        st.session_state.history.append({"guess": guess_int, "outcome": outcome})
        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )
        if outcome == "Win":
            st.session_state.status = "won"
            st.session_state.last = {
                "kind": "win",
                "title": f"Correct — secret was {st.session_state.secret}",
                "detail": f"FINAL SCORE: {st.session_state.score}",
            }
        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"
            st.session_state.last = {
                "kind": "over",
                "title": "Out of guesses",
                "detail": f"SECRET WAS {st.session_state.secret} · SCORE {st.session_state.score}",
            }
        else:
            st.session_state.last = {
                "kind": "high" if outcome == "Too High" else "low",
                "title": outcome,
                "detail": HINTS[outcome] if show_hint else "HINT HIDDEN",
            }
    # Rerun so the blocks/progress above render the updated state.
    st.rerun()

# ---- Feedback block ---------------------------------------------------------
fb = st.session_state.last
if fb:
    detail = f'<div class="d">{fb["detail"]}</div>' if fb["detail"] else ""
    st.markdown(
        f'<div class="card {fb["kind"]}">'
        f'<div class="ico">{ICONS[fb["kind"]]}</div>'
        f'<div><div class="t">{fb["title"]}</div>{detail}</div></div>',
        unsafe_allow_html=True,
    )

# ---- Guess history ----------------------------------------------------------
if st.session_state.history:
    pills = "".join(
        f'<span class="pill {OUTCOME_CLASS[h["outcome"]]}">{h["guess"]}</span>'
        for h in st.session_state.history
    )
    st.markdown(f'<div class="seclbl">Your guesses</div><div class="pills">{pills}</div>', unsafe_allow_html=True)

# ---- Dev mode (hidden from players by default) ------------------------------
if dev_mode:
    with st.expander("Developer Debug Info", expanded=True):
        st.write("Secret:", st.session_state.secret)
        st.write("Attempts:", st.session_state.attempts)
        st.write("Score:", st.session_state.score)
        st.write("Difficulty:", difficulty)
        st.write("History:", st.session_state.history)

st.divider()
st.caption("NOW ACTUALLY PLAYABLE.")
