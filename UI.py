import streamlit as st
from streamlit.components.v1 import declare_component
import streamlit.components.v1 as components
import random

st.set_page_config(page_title="Minesweeper", layout="centered")

# ============== Theme ==============
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def apply_theme(dark: bool):
    bg_grad = "#ffffff" if not dark else "#0f172a"
    text = "#111827" if not dark else "#e5e7eb"
    card_bg = "#ffffff" if not dark else "#111827"
    border = "#e5e7eb" if not dark else "#334155"
    tile_bg = "#f8fafc" if not dark else "#1f2937"
    tile_border = "#e5e7eb" if not dark else "#334155"
    primary = "#2563eb"

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
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 12px;
}}
#minesweeper button {{
  background-color: var(--tile-bg) !important;
  border: 1px solid var(--tile-border) !important;
  border-radius: 6px !important;
  height: 36px !important; width: 36px !important;
  font-size: 18px !important; font-weight: 700 !important; color: var(--text) !important;
  transition: background-color .08s ease, border-color .08s ease;
}}
#minesweeper button:hover {{ background-color: #eef2f7 !important; }}
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
top_left, top_right = st.columns([6,2])
with top_left:
    st.title("Minesweeper")
with top_right:
    st.toggle("Dark mode", key="dark_mode")
    apply_theme(st.session_state.dark_mode)

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

    # No separate flag mode; tiles handle flag toggling inline

    safe = R*C-M
    opened = sum((r,c) in vis for r in range(R) for c in range(C) if board[r][c]!=-1)
    st.write(f"Revealed {opened}/{safe} | Flags {len(flg)} | Mines {M}")

    num_color = {
        "1":"#1A73E8","2":"#188038","3":"#D93025","4":"#3457D5",
        "5":"#8C2F39","6":"#00796B","7":"#333333","8":"#757575"
    }

    with st.container():
        st.markdown('<div id="minesweeper">', unsafe_allow_html=True)
        right_click_cell = declare_component("right_click_cell", path="components/right_click_cell")
        for r in range(R):
            cols = st.columns(C)
            for c in range(C):
                if (r,c) in vis:
                    v = board[r][c]
                    t = "□" if v==0 else str(v)
                    color = num_color.get(t,"#000")
                    cols[c].markdown(f"<p style='text-align:center;font-size:20px;font-weight:600;color:{color}'>{t}</p>", unsafe_allow_html=True)
                else:
                    result = right_click_cell(r=r, c=c, flagged=(r,c) in flg, key=f"tile-{r}-{c}")
                    if result:
                        action = result.get("action")
                        rr = result.get("r")
                        cc = result.get("c")
                        if action == "flag":
                            flg.add((rr,cc))
                            st.rerun()
                        elif action == "unflag":
                            if (rr,cc) in flg: flg.remove((rr,cc))
                            st.rerun()
                        elif action == "reveal":
                            if not reveal(board, vis, flg, rr, cc):
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

st.markdown("""</div>""", unsafe_allow_html=True)
