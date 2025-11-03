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
.status-bar {{ 
  display:flex; gap:12px; align-items:center; flex-wrap:wrap; 
  margin-bottom:16px; padding:12px; 
  background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,248,255,0.9) 100%);
  border-radius:12px; border: 1px solid var(--border);
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}}
.pill {{
  display:inline-flex; align-items:center; gap:8px; padding:8px 14px;
  border: none; border-radius:20px; 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff; font-weight:700; font-size: 13px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}}
.pill:nth-child(2) {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
.pill:nth-child(3) {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
.pill:nth-child(4) {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}

.flag-indicator {{
  display:inline-flex; align-items:center; gap:8px; padding:8px 16px;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white; border-radius:20px; font-weight:700; font-size:14px;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
}}

#minesweeper {{
  background: linear-gradient(135deg, rgba(255,255,255,0.5) 0%, rgba(240,248,255,0.5) 100%);
  padding:16px; border-radius:16px; border: 2px solid var(--border);
  box-shadow: inset 0 2px 8px rgba(0,0,0,0.05), 0 4px 16px rgba(0,0,0,0.1);
}}

#minesweeper button {{
  background: linear-gradient(135deg, #e8efff 0%, #d6e4ff 100%) !important;
  border: 2px solid #b8d4ff !important;
  border-radius: 10px !important;
  height: 40px !important; width: 40px !important;
  font-size: 20px !important; font-weight: 800 !important; 
  color: var(--text) !important;
  transition: all 0.15s ease !important;
  box-shadow: 0 3px 8px rgba(0,0,0,0.1), inset 0 1px 2px rgba(255,255,255,0.6);
  cursor: pointer !important;
}}
#minesweeper button:hover {{ 
  transform: translateY(-2px) scale(1.05) !important; 
  box-shadow: 0 6px 16px rgba(0,0,0,0.15), inset 0 1px 2px rgba(255,255,255,0.8) !important;
  background: linear-gradient(135deg, #d6e4ff 0%, #c4d9ff 100%) !important;
}}
#minesweeper button:active {{ 
  transform: translateY(0) scale(0.98) !important;
}}

.revealed-cell {{
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
  border: 2px solid #dee2e6 !important;
  border-radius: 10px !important;
  height: 40px !important; width: 40px !important;
  display: flex !important; align-items: center !important; justify-content: center !important;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.1) !important;
  font-size: 20px !important; font-weight: 700 !important;
}}
div.stButton > button {{
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: #ffffff !important;
  border: none !important;
  font-weight: 700 !important; 
  border-radius: 12px !important;
  padding: 10px 24px !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
  transition: all 0.2s ease !important;
}}
div.stButton > button:hover {{
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4) !important;
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

    # Flag mode indicator
    if st.session_state.flag:
        st.markdown('<div class="flag-indicator">🚩 Flag Mode ACTIVE</div>', unsafe_allow_html=True)
    else:
        left_col, right_col = st.columns([1, 20])
        with left_col:
            st.checkbox("", key="flag")
        with right_col:
            st.markdown("<span style='color:#666;font-weight:600'>Toggle Flag Mode</span>", unsafe_allow_html=True)

    # Status bar with pills
    safe = R*C-M
    opened = sum((r,c) in vis for r in range(R) for c in range(C) if board[r][c]!=-1)
    st.markdown(f"""
    <div class="status-bar">
        <span class="pill">📊 Revealed: {opened}/{safe}</span>
        <span class="pill">🚩 Flags: {len(flg)}</span>
        <span class="pill">💣 Mines: {M}</span>
        <span class="pill">🎯 Progress: {int(opened/safe*100) if safe > 0 else 0}%</span>
    </div>
    """, unsafe_allow_html=True)

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
                    cols[c].markdown(
                        f"<div class='revealed-cell' style='color:{color}'>{t}</div>", 
                        unsafe_allow_html=True
                    )
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
