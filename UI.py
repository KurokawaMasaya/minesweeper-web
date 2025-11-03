import streamlit as st
import random
import gspread
from google.oauth2.service_account import Credentials
import time
import datetime

def get_sheet():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("service_key.json", scopes=scope)
    client = gspread.authorize(creds)
    
    sheet = client.open("Minesweeper Scores").sheet1  # 你的表名
    return sheet
st.set_page_config(page_title="Minesweeper", layout="centered")

# ================= CSS =================
st.markdown("""
<style>

html, body, .stApp {
    background-color: #ffffff !important;
    color: #000000 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* ====== Sweep cell button style ====== */
#minesweeper button {
    background-color: #f5f6f7 !important;
    border: 1px solid #d1d1d1 !important;
    border-radius: 6px !important;
    color: #000000 !important;
    height: 36px !important;
    width: 36px !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    padding: 0 !important;
    cursor: pointer;
}
#minesweeper button:hover {
    background-color: #e9ebed !important;
    border-color: #bcbcbc !important;
}
#minesweeper button:active {
    background-color: #dcdedf !important;
    border-color: #a0a0a0 !important;
}

/* ====== Start / Restart buttons ====== */
div.stButton > button {
    background-color: #e8f0fe !important;
    color: #1a73e8 !important;
    border: 1px solid #b0c7ff !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
}
div.stButton > button:hover {
    background-color: #dce7ff !important;
    border-color: #8bb2ff !important;
}

/* ====== Checkbox (Flag Mode) text ====== */
div[data-testid="stCheckbox"] label {
    color: #d93025 !important; /* red */
    font-weight: 700 !important;
}

</style>
""", unsafe_allow_html=True)

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
