import streamlit as st
import random

st.set_page_config(page_title="Minesweeper", layout="centered")

# ============== Theme ==============
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def apply_theme(dark: bool):
    bg_grad = "linear-gradient(135deg,#f8fbff 0%,#eef3ff 50%,#e9f7ff 100%)" if not dark else "linear-gradient(135deg,#0b1020 0%,#111831 50%,#0f1a2b 100%)"
    text = "#0b1a33" if not dark else "#e6eefc"
    card_bg = "rgba(255,255,255,0.75)" if not dark else "rgba(17,26,49,0.55)"
    border = "#d7e3ff" if not dark else "#2a3a5e"
    tile_bg = "#f5f7fb" if not dark else "#162343"
    tile_border = "#d6dbe8" if not dark else "#20325a"
    primary = "#1a73e8"

    st.markdown(f"""
<style>
:root {{
  --text: {text};
  --card-bg: {card_bg};
  --border: {border};
  --tile-bg: {tile_bg};
  --tile-border: {tile_border};
  --primary: {primary};
}}
html, body, .stApp {{
  background: {bg_grad} !important;
  color: var(--text) !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
.game-card {{
  background: var(--card-bg);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 18px 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}}
.status-bar {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom:8px; }}
.pill {{
  display:inline-flex; align-items:center; gap:6px; padding:6px 10px;
  border: 1px solid var(--border); border-radius:999px; background: var(--tile-bg);
  color: var(--text); font-weight:700; font-size: 13px;
}}
#minesweeper button {{
  background-color: var(--tile-bg) !important;
  border: 1px solid var(--tile-border) !important;
  border-radius: 8px !important;
  height: 36px !important; width: 36px !important;
  font-size: 18px !important; font-weight: 700 !important; color: var(--text) !important;
  transition: transform .08s ease, box-shadow .12s ease;
}}
#minesweeper button:hover {{ transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,.12); }}
div.stButton > button {{
  background-color: #e8f0fe !important; color: var(--primary) !important;
  border: 1px solid #b0c7ff !important; font-weight: 700 !important; border-radius: 10px !important;
}}
div[data-testid="stCheckbox"] label {{ color: #d93025 !important; font-weight: 800 !important; }}
</style>
""", unsafe_allow_html=True)

apply_theme(st.session_state.dark_mode)

# ================= CSS =================
st.markdown("""<div class='game-card'>""", unsafe_allow_html=True)

# ================= Minesweeper logic =================

def neighbors(r, c, R, C):
    for dr in (-1,0,1):
        for dc in (-1,0,1):
            if dr==0 and dc==0: continue
            rr, cc = r+dr, c+dc
            if 0 <= rr < R and 0 <= cc < C:
                yield rr, cc

def init_board(R, C): return [[0]*C for _ in range(R)]

def place(board, mines):
    R, C = len(board), len(board[0])
    # Ensure we never request more mines than available cells - 1
    mines = max(0, min(mines, R * C - 1))
    # Sample unique positions to avoid potential infinite loops
    all_cells = [(r, c) for r in range(R) for c in range(C)]
    mine_positions = set(random.sample(all_cells, mines)) if mines > 0 else set()

    # Place mines
    for r, c in mine_positions:
        board[r][c] = -1

    # Update adjacent counts
    for r, c in mine_positions:
        for nr, nc in neighbors(r, c, R, C):
            if board[nr][nc] != -1:
                board[nr][nc] += 1

def flood(board, vis, r, c):
    stack=[(r,c)]
    while stack:
        x,y = stack.pop()
        if (x,y) in vis: continue
        vis.add((x,y))
        if board[x][y]==0:
            for nx,ny in neighbors(x,y,len(board),len(board[0])):
                if (nx,ny) not in vis: stack.append((nx,ny))

def reveal(board, vis, flg, r, c):
    if (r,c) in flg: return True
    if board[r][c]==-1: return False
    if board[r][c]==0: flood(board, vis, r, c)
    else: vis.add((r,c))
    return True

def start(R,C,M):
    b = init_board(R,C)
    # Clamp M defensively in case the caller passes too many mines
    M = max(0, min(M, R * C - 1))
    place(b,M)
    st.session_state.board = b
    st.session_state.revealed=set()
    st.session_state.flags=set()
    st.session_state.rows=R
    st.session_state.cols=C
    st.session_state.mines=M
    st.session_state.running=True

if "running" not in st.session_state: st.session_state.running=False
if "flag" not in st.session_state: st.session_state.flag=False
if "last_message" not in st.session_state: st.session_state.last_message=None
if "last_message_type" not in st.session_state: st.session_state.last_message_type=None

# ================= UI =================
st.title("Minesweeper")

# Show one-time game result notices
if st.session_state.last_message:
    if st.session_state.last_message_type == "success":
        st.success(st.session_state.last_message)
    else:
        st.error(st.session_state.last_message)
    st.session_state.last_message = None
    st.session_state.last_message_type = None

if not st.session_state.running:
    R = st.slider("Rows",5,20,10)
    C = st.slider("Columns",5,20,10)
    diff = st.selectbox("Difficulty",["Easy","Medium","Hard"])
    M = max(1, int(R*C*{"Easy":.1,"Medium":.2,"Hard":.3}[diff]))

    if st.button("Start Game"):
        start(R,C,M)
        st.rerun()

else:
    board = st.session_state.board
    vis   = st.session_state.revealed
    flg   = st.session_state.flags
    R     = st.session_state.rows
    C     = st.session_state.cols
    M     = st.session_state.mines

    left_col, right_col = st.columns([1, 10])
    with left_col:
        st.checkbox("", key="flag")
    with right_col:
        st.markdown("<span style='color:#d93025;font-weight:700'>Flag Mode</span>", unsafe_allow_html=True)

    safe = R*C-M
    opened = sum((r,c) in vis for r in range(R) for c in range(C) if board[r][c]!=-1)
    st.write(f"Revealed {opened}/{safe} | Flags {len(flg)} | Mines {M}")

    num_color = {
        "1":"#1A73E8","2":"#188038","3":"#D93025","4":"#3457D5",
        "5":"#8C2F39","6":"#00796B","7":"#333333","8":"#757575"
    }

    with st.container():
        st.markdown('<div id="minesweeper">', unsafe_allow_html=True)
        for r in range(R):
            cols = st.columns(C)
            for c in range(C):
                if (r,c) in vis:
                    v = board[r][c]
                    t = "□" if v==0 else str(v)
                    color = num_color.get(t,"#000")
                    cols[c].markdown(f"<p style='text-align:center;font-size:20px;font-weight:600;color:{color}'>{t}</p>", unsafe_allow_html=True)
                else:
                    label = "⚑" if (r,c) in flg else "■"
                    if cols[c].button(label, key=f"{r}-{c}"):
                        if st.session_state.flag:
                            if (r,c) in flg: flg.remove((r,c))
                            else: flg.add((r,c))
                        else:
                            if not reveal(board, vis, flg, r, c):
                                st.session_state.last_message = "💥 BOOM — You lost"
                                st.session_state.last_message_type = "error"
                                st.session_state.running=False
                                st.rerun()
                        st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if opened==safe:
        st.session_state.last_message = "🎉 YOU WIN!"
        st.session_state.last_message_type = "success"
        st.session_state.running=False
        st.rerun()

    if st.button("Restart"):
        st.session_state.running=False
        st.rerun()
