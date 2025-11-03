import streamlit as st
import random
import gspread
from google.oauth2.service_account import Credentials
import time
import datetime
import pandas as pd

# ===== Google Sheets =====
def get_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["GSPREAD_SERVICE_ACCOUNT"],
        scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    sheet = client.open("Minesweeper Scores").sheet1
    return sheet
    return sheet

def add_score(name, diff, result, elapsed):
    sheet = get_sheet()
    sheet.append_row([name, diff, result, elapsed, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

st.set_page_config(page_title="Minesweeper", layout="centered")

# ===== CSS =====
st.markdown("""
<style>
html, body, .stApp {
    background-color: #ffffff !important;
    color: #000000 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
#minesweeper button {
    background-color: #f5f6f7 !important;
    border: 1px solid #d1d1d1 !important;
    border-radius: 6px !important;
    height: 36px !important; width: 36px !important;
    font-size: 18px !important; font-weight: 600 !important;
}
div.stButton > button {
    background-color: #e8f0fe !important; color: #1a73e8 !important;
    border: 1px solid #b0c7ff !important; font-weight: 600 !important;
}
div.stButton > button:hover {
    background-color: #dce7ff !important;
}
div[data-testid="stCheckbox"] label {
    color: #d93025 !important; font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

# ===== Minesweeper Logic =====
def neighbors(r, c, R, C):
    for dr in (-1,0,1):
        for dc in (-1,0,1):
            if dr==0 and dc==0: continue
            rr, cc = r+dr, c+dc
            if 0 <= rr < R and 0 <= cc < C:
                yield rr, cc

def init_board(R, C): 
    return [[0]*C for _ in range(R)]

def place(board, mines):
    R, C = len(board), len(board[0])
    mines = max(0, min(mines, R*C - 1))
    cells = [(r,c) for r in range(R) for c in range(C)]
    mine_pos = set(random.sample(cells, mines))
    for r,c in mine_pos:
        board[r][c] = -1
    for r,c in mine_pos:
        for nr,nc in neighbors(r,c,R,C):
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
    M = max(0,min(M,R*C-1))
    place(b,M)
    st.session_state.board=b
    st.session_state.revealed=set()
    st.session_state.flags=set()
    st.session_state.rows=R
    st.session_state.cols=C
    st.session_state.mines=M
    st.session_state.running=True
    st.session_state.start_time=time.time()

# ===== State =====
if "running" not in st.session_state: st.session_state.running=False
if "flag" not in st.session_state: st.session_state.flag=False

# ===== Tabs =====
tab_game, tab_board = st.tabs(["💣 Game", "🏆 Leaderboard"])

# ===== GAME TAB =====
with tab_game:
    st.title("Minesweeper")

    if not st.session_state.running:
        name = st.text_input("Player name", "Player")
        st.session_state.player = name

        R = st.slider("Rows",5,20,10)
        C = st.slider("Columns",5,20,10)
        diff = st.selectbox("Difficulty",["Easy","Medium","Hard"])
        M = max(1, int(R*C*{"Easy":.1,"Medium":.2,"Hard":.3}[diff]))
        st.session_state.diff = diff

        if st.button("Start Game"):
            start(R,C,M)
            st.experimental_rerun()
    else:
        board = st.session_state.board
        vis   = st.session_state.revealed
        flg   = st.session_state.flags
        R,C,M = st.session_state.rows,st.session_state.cols,st.session_state.mines

        # === TIMER (Step 4) ===
        elapsed = time.time() - st.session_state.start_time
        st.write(f"⏱ Time: **{elapsed:.1f}s**")

        left,right = st.columns([1,9])
        with left: st.checkbox("", key="flag")
        with right: st.markdown("**Flag Mode**", unsafe_allow_html=True)

        safe = R*C-M
        opened=sum((r,c) in vis for r in range(R) for c in range(C) if board[r][c]!=-1)
        st.write(f"Revealed {opened}/{safe} | Flags {len(flg)} | Mines {M}")

        numc = {"1":"#1A73E8","2":"#188038","3":"#D93025","4":"#3457D5","5":"#8C2F39","6":"#00796B","7":"#333","8":"#777"}

        with st.container():
            st.markdown('<div id="minesweeper">', unsafe_allow_html=True)
            for r in range(R):
                row = st.columns(C)
                for c in range(C):
                    if (r,c) in vis:
                        v = board[r][c]
                        t="□" if v==0 else str(v)
                        color=numc.get(t,"#000")
                        row[c].markdown(f"<p style='text-align:center;font-size:20px;font-weight:600;color:{color}'>{t}</p>",unsafe_allow_html=True)
                    else:
                        label="⚑" if (r,c) in flg else "■"
                        if row[c].button(label, key=f"{r}-{c}"):
                            if st.session_state.flag:
                                if (r,c) in flg: flg.remove((r,c))
                                else: flg.add((r,c))
                            else:
                                ok=reveal(board,vis,flg,r,c)
                                if not ok:
                                    # === FAIL: write result (Step 5) ===
                                    add_score(st.session_state.player, st.session_state.diff, "Lose", round(elapsed,2))
                                    st.error("💥 BOOM! You lost")
                                    st.session_state.running=False
                                    st.experimental_rerun()
                            st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # Win condition
        if opened==safe:
            add_score(st.session_state.player, st.session_state.diff, "Win", round(elapsed,2))
            st.success("🎉 YOU WIN!")
            st.session_state.running=False
            st.experimental_rerun()

        if st.button("Restart"):
            st.session_state.running=False
            st.experimental_rerun()

# ===== LEADERBOARD TAB (Step 6) =====
with tab_board:
    st.title("🏆 Leaderboard")
    sheet = get_sheet()
    data = sheet.get_all_records()
    if not data:
        st.write("No scores recorded yet.")
    else:
        df = pd.DataFrame(data)
        df = df.sort_values(by=["Result","Time"], ascending=[False,True])
        st.dataframe(df)
