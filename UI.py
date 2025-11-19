import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="Minesweeper Crayon Final", layout="centered", page_icon="🖍️")

# ================= 核心逻辑 =================
def neighbors(r, c, R, C):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0: continue
            rr, cc = r + dr, c + dc
            if 0 <= rr < R and 0 <= cc < C:
                yield rr, cc

def init_board(R, C): return [[0] * C for _ in range(R)]

def place(board, mines):
    R, C = len(board), len(board[0])
    mines = max(0, min(mines, R * C - 1))
    all_cells = [(r, c) for r in range(R) for c in range(C)]
    mine_positions = set(random.sample(all_cells, mines)) if mines > 0 else set()
    for r, c in mine_positions:
        board[r][c] = -1
    for r, c in mine_positions:
        for nr, nc in neighbors(r, c, R, C):
            if board[nr][nc] != -1:
                board[nr][nc] += 1

def flood(board, vis, r, c):
    stack = [(r, c)]
    while stack:
        x, y = stack.pop()
        if (x, y) in vis: continue
        vis.add((x, y))
        if board[x][y] == 0:
            for nx, ny in neighbors(x, y, len(board), len(board[0])):
                if (nx, ny) not in vis: stack.append((nx, ny))

def reveal(board, vis, flg, r, c):
    if (r, c) in flg: return True
    if board[r][c] == -1: return False
    if board[r][c] == 0:
        flood(board, vis, r, c)
    else:
        vis.add((r, c))
    return True

def start(R, C, M):
    b = init_board(R, C)
    M = max(0, min(M, R * C - 1))
    place(b, M)
    st.session_state.board = b
    st.session_state.revealed = set()
    st.session_state.flags = set()
    st.session_state.rows = R
    st.session_state.cols = C
    st.session_state.mines = M
    st.session_state.running = True
    st.session_state.lost = False
    st.session_state.won = False
    st.session_state.game_config = {'R': R, 'C': C, 'M': M}

if "running" not in st.session_state: st.session_state.running = False
if "flag" not in st.session_state: st.session_state.flag = False
if "lost" not in st.session_state: st.session_state.lost = False
if "won" not in st.session_state: st.session_state.won = False

# ================= 🎨 CSS (还原蜡笔手绘风 + 修复抖动) =================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    /* 1. 还原背景与字体 */
    .stApp {
        background-color: #fdfcf0;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    h1, p, label, span, div {
        color: #2c3e50 !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    h1 { text-align: center; color: #000 !important; }

    /* ============================================================
       输入框 & 下拉框 (保持白底黑字，清晰可见)
       ============================================================ */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    div[data-testid="stNumberInput"] > div {
        background-color: #ffffff !important;
        border: 2px solid #2c3e50 !important;
        color: #000000 !important;
        border-radius: 4px !important;
        box-shadow: none !important;
    }
    input[type="number"], div[data-baseweb="select"] span, div[data-testid="stNumberInput"] input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: bold !important;
        font-size: 18px !important;
        text-align: center;
        caret-color: #000;
    }
    div[data-baseweb="select"] svg { fill: #000000 !important; }
    div[data-testid="stNumberInput"] button { display: none !important; }

    /* 下拉菜单无特效 */
    ul[data-baseweb="menu"] { background-color: #fff !important; border: 2px solid #2c3e50 !important; }
    li[data-baseweb="option"] { color: #000 !important; background-color: #fff !important; }
    li[data-baseweb="option"]:hover, li[data-baseweb="option"][aria-selected="true"] {
        background-color: #e0e0e0 !important; color: #000 !important;
    }

    /* ============================================================
       棋盘样式 (还原手绘圆角 + 有缝隙)
       ============================================================ */
    
    /* 保持缝隙 */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.4rem !important;
        justify-content: center !important;
    }

    /* 固定列宽 */
    div[data-testid="column"] {
        width: 44px !important;
        flex: 0 0 44px !important;
        min-width: 44px !important;
        padding: 0 !important;
    }
    
    /* ⚡️ 修复缩动问题的核心：强制按钮容器高度 ⚡️ */
    div.stButton {
        height: 44px !important;
        min-height: 44px !important;
    }

    /* 通用蜡笔方块样式 */
    .crayon-box {
        width: 40px !important;
        height: 40px !important;
        border: 2px solid #2c3e50 !important; /* 蜡笔黑边 */
        border-radius: 5px !important; /* 还原圆角 */
        display: flex; align-items: center; justify-content: center;
        box-sizing: border-box !important;
        font-size: 20px; font-weight: bold;
    }

    /* 未揭开 (按钮) */
    button[kind="secondary"] {
        @extend .crayon-box;
        background-color: #ffffff !important;
        color: transparent !important;
        /* 还原阴影，这才是手绘风的精髓 */
        box-shadow: 2px 2px 0px rgba(0,0,0,0.15) !important;
        transition: none !important;
    }
    /* 简单的按下效果，不变色 */
    button[kind="secondary"]:hover {
        background-color: #fff !important;
        border-color: #000 !important;
        transform: translate(-1px, -1px);
    }
    button[kind="secondary"]:active {
        box-shadow: none !important;
        transform: translate(1px, 1px);
    }

    /* 已揭开 (Div) - 必须和按钮高度完全一致 */
    .cell-revealed {
        @extend .crayon-box;
        background-color: #dfe6e9 !important; 
        color: #2c3e50 !important;
        cursor: default;
        box-shadow: none !important; /* 凹陷 */
    }

    .cell-bomb { color: #d63031 !important; font-size: 28px !important; }

    /* 功能按钮 (Start/Restart/Home) */
    button[kind="primary"] {
        background-color: #2c3e50 !important;
        border: 2px solid #000 !important;
        border-radius: 6px !important;
        width: 100%;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.2) !important;
    }
    button[kind="primary"] p { color: #fff !important; font-size: 18px !important; }
    button[kind="primary"]:hover { background-color: #000 !important; transform: translate(-1px, -1px); }
    button[kind="primary"]:active { transform: translate(1px, 1px); box-shadow: none !important; }

    .c1 { color: #0984e3 !important; } .c2 { color: #00b894 !important; }
    .c3 { color: #d63031 !important; } .c4 { color: #6c5ce7 !important; }

</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

st.title("Minesweeper")

if not st.session_state.running:
    st.markdown("### ✏️ Setup")
    
    c1, sp1, c2, sp2, c3 = st.columns([1, 0.5, 1, 0.5, 2])
    
    with c1: R = st.number_input("Rows", 5, 20, 10)
    with sp1: st.empty()
    with c2: C = st.number_input("Cols", 5, 20, 10)
    with sp2: st.empty()
    with c3: 
        diff = st.selectbox("Diff", ["Easy (10%)", "Med (15%)", "Hard (20%)"])
        rate = 0.10 if "Easy" in diff else (0.15 if "Med" in diff else 0.20)
    
    M = max(1, int(R * C * rate))
    st.write(f"**Mines:** {M}")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("START GAME", type="primary", use_container_width=True):
        start(R, C, M)
        st.rerun()

else:
    c1, c2, c3, c4 = st.columns([1, 1.2, 1.8, 1])
    
    with c1:
        if st.button("🏠 Home", type="primary", use_container_width=True):
            st.session_state.running = False
            st.rerun()

    with c2:
        mode = "🚩 Flag" if st.session_state.flag else "⛏️ Dig"
        if st.button(mode, type="primary", use_container_width=True):
            st.session_state.flag = not st.session_state.flag
            st.rerun()
            
    with c3:
        left = st.session_state.mines - len(st.session_state.flags)
        st.markdown(
            f"<div style='text-align:center; font-size:22px; font-weight:bold; padding-top:8px; color:#000;'>{left} 💣 Left</div>",
            unsafe_allow_html=True)
            
    with c4:
        if st.button("🔄", type="primary", use_container_width=True, help="Restart"):
            cfg = st.session_state.game_config
            start(cfg['R'], cfg['C'], cfg['M'])
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.lost: st.markdown("<h2 style='color:#d63031;text-align:center'>Oops! Boom!</h2>", unsafe_allow_html=True)
    if st.session_state.won: st.markdown("<h2 style='color:#00b894;text-align:center'>You Win!</h2>", unsafe_allow_html=True)

    st.markdown("<div style='display:flex; justify-content:center; flex-direction:column; align-items:center;'>", unsafe_allow_html=True)
    
    board = st.session_state.board
    vis = st.session_state.revealed
    flg = st.session_state.flags
    
    for r in range(st.session_state.rows):
        cols = st.columns(st.session_state.cols)
        for c in range(st.session_state.cols):
            with cols[c]:
                key = f"{r}_{c}"
                is_rev = (r, c) in vis
                is_flg = (r, c) in flg
                end = st.session_state.lost or st.session_state.won
                
                if is_rev or (end and board[r][c] == -1):
                    val = board[r][c]
                    if val == -1:
                        st.markdown("<div class='cell-revealed cell-bomb'>X</div>", unsafe_allow_html=True)
                    elif val == 0:
                        st.markdown("<div class='cell-revealed'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='cell-revealed c{val}'>{val}</div>", unsafe_allow_html=True)
                else:
                    label = "P" if is_flg else " "
                    if not end:
                        if st.button(label, key=key, type="secondary"):
                            if st.session_state.flag:
                                if is_flg: flg.remove((r, c))
                                else: flg.add((r, c))
                                st.rerun()
                            elif not is_flg:
                                if not reveal(board, vis, flg, r, c):
                                    st.session_state.lost = True
                                st.rerun()
                    else:
                        st.markdown(f"<div class='cell-revealed' style='background:#fff !important; color:#ccc !important;'>{label}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
