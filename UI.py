import streamlit as st
import random

# -------------------- Basic Config --------------------
st.set_page_config(page_title="Minesweeper", layout="centered")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# -------------------- Theme --------------------
def apply_theme(dark):
    bg = "#ffffff" if not dark else "#0f172a"
    text = "#111827" if not dark else "#f1f5f9"
    tile_bg = "#f8fafc" if not dark else "#1e293b"
    border = "#e5e7eb" if not dark else "#334155"
    primary = "#2563eb"

    st.markdown(f"""
    <style>
    html, body, .stApp {{
        background:{bg} !important;
        color:{text} !important;
        font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
    }}
    #minesweeper button {{
        background:{tile_bg} !important;
        border:1px solid {border} !important;
        border-radius:6px !important;
        height:36px !important;
        width:36px !important;
        font-size:18px !important;
        font-weight:700;
        color:{text} !important;
        cursor:pointer;
    }}
    #minesweeper button:hover {{
        background:#e2e8f0 !important;
    }}
    div.stButton > button {{
        background-color:#e8f0fe !important;
        color:{primary} !important;
        border:1px solid #b0c7ff !important;
        font-weight:700 !important;
        border-radius:8px !important;
        padding:8px 14px !important;
    }}
    div[data-testid="stCheckbox"] label {{
        color:#d93025 !important;
        font-weight:800 !important;
    }}
    </style>
    """, unsafe_allow_html=True)


apply_theme(st.session_state.dark_mode)

# -------------------- Game Logic --------------------
def neighbors(r, c, R, C):
    for dr in (-1,0,1):
        for dc in (-1,0,1):
            if dr==0 and dc==0: continue
            nr, nc = r+dr, c+dc
            if 0 <= nr < R and 0 <= nc < C:
                yield nr, nc

def init_board(R, C):
    return [[0]*C for _ in range(R)]

def place_mines(board, M):
    R, C = len(board), len(board[0])
    import random
    mines = set(random.sample([(r,c) for r in range(R) for c in range(C)], M))
    for r,c in mines:
        board[r][c] = -1
    for r,c in mines:
        for nr, nc in neighbors(r,c,R,C):
            if board[nr][nc] != -1:
                board[nr][nc] += 1

def flood(board, vis, r, c):
    stack = [(r,c)]
    while stack:
        x,y = stack.pop()
        if (x,y) in vis: continue
        vis.add((x,y))
        if board[x][y] == 0:
            for nx,ny in neighbors(x,y,len(board),len(board[0])):
                if (nx,ny) not in vis:
                    stack.append((nx,ny))

def reveal(board, vis, flg, r, c):
    if (r,c) in flg: return True
    if board[r][c] == -1: return False
    if board[r][c] == 0: flood(board, vis, r, c)
    else: vis.add((r,c))
    return True

def start_game(R,C,M):
    board = init_board(R,C)
    place_mines(board, M)
    st.session_state.board = board
    st.session_state.revealed = set()
    st.session_state.flags = set()
    st.session_state.running = True
    st.session_state.rows = R
    st.session_state.cols = C
    st.session_state.mines = M

if "running" not in st.session_state:
    st.session_state.running = False

# -------------------- UI --------------------
top_left, top_right = st.columns([6,2])
with top_left:
    st.title("Minesweeper")
with top_right:
    st.toggle("Dark mode", key="dark_mode")
    apply_theme(st.session_state.dark_mode)

if not st.session_state.running:
    R = st.slider("Rows", 5, 20, 10)
    C = st.slider("Columns", 5, 20, 10)
    diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    M = int(R*C*{"Easy":0.1,"Medium":0.2,"Hard":0.3}[diff])

    if st.button("Start Game"):
        start_game(R,C,M)
        st.rerun()

else:
    board = st.session_state.board
    vis   = st.session_state.revealed
    flg   = st.session_state.flags
    R, C, M = st.session_state.rows, st.session_state.cols, st.session_state.mines

    st.session_state.flag_mode = st.checkbox("Flag Mode (like holding Shift)")

    safe = R*C-M
    opened = sum((r,c) in vis for r in range(R) for c in range(C) if board[r][c]!=-1)
    st.write(f"Revealed {opened}/{safe} | Flags {len(flg)} | Mines {M}")

    num_color = {
        "1":"#1E40AF","2":"#15803D","3":"#B91C1C","4":"#1E3A8A",
        "5":"#BE123C","6":"#0F766E","7":"#000","8":"#475569"
    }

    st.markdown('<div id="minesweeper">', unsafe_allow_html=True)
    for r in range(R):
        cols = st.columns(C)
        for c in range(C):
            if (r,c) in vis:
                v = board[r][c]
                show = "□" if v==0 else str(v)
                color = num_color.get(show, "#fff")
                cols[c].markdown(
                    f"<p style='text-align:center;font-size:20px;font-weight:700;color:{color}'>{show}</p>",
                    unsafe_allow_html=True
                )
            else:
                label = "🚩" if (r,c) in flg else "▪️"
                if cols[c].button(label, key=f"{r}-{c}"):
                    if st.session_state.flag_mode:
                        if (r,c) in flg: flg.remove((r,c))
                        else: flg.add((r,c))
                    else:
                        if not reveal(board, vis, flg, r, c):
                            st.error("💥 BOOM — You lost")
                            st.session_state.running = False
                            st.rerun()
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if opened == safe:
        st.success("🎉 YOU WIN!")
        st.session_state.running = False
        st.rerun()

    if st.button("Restart"):
        st.session_state.running = False
        st.rerun()
