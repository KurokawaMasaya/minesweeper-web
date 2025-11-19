import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="Perfect Layout", layout="centered", page_icon="🖍️")

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

# ================= 🎨 CSS (布局彻底修复) =================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    /* 1. 全局样式 */
    .stApp {
        background-color: #fdfcf0;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
        color: #000000 !important;
    }
    
    h1, p, label, span, div {
        color: #000000 !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    h1 { text-align: center; }

    /* ============================================================
       输入框 & 菜单 (保持白底黑字)
       ============================================================ */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    div[data-testid="stNumberInput"] > div {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        color: #000000 !important;
        border-radius: 4px !important;
        box-shadow: none !important;
    }
    
    /* 杀掉输入框高亮 */
    div[data-baseweb="select"] > div:focus-within,
    div[data-testid="stNumberInput"] > div:focus-within {
        border-color: #000000 !important;
        outline: none !important;
        box-shadow: none !important;
    }

    input[type="number"], div[data-baseweb="select"] span, div[data-testid="stNumberInput"] input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: bold !important;
        text-align: center;
    }

    div[data-baseweb="select"] svg { fill: #000000 !important; }
    div[data-testid="stNumberInput"] button { display: none !important; }

    ul[data-baseweb="menu"] { background-color: #ffffff !important; border: 2px solid #000000 !important; }
    li[data-baseweb="option"] { color: #000000 !important; background-color: #ffffff !important; }
    li[data-baseweb="option"]:hover { background-color: #e0e0e0 !important; }

    /* ============================================================
       🚨 棋盘布局修复 (Layout Fix) 🚨
       ============================================================ */

    /* 1. 移除列宽强制锁定！让顶部的 Home/Restart 按钮能自然展开 */
    div[data-testid="column"] {
        width: auto !important; 
        flex: 1 1 auto !important; /* 允许弹性伸缩 */
        padding: 0px 2px !important; /* 仅保留左右微小间距 */
        min-width: 0 !important;
    }

    /* 2. 但要强制【棋盘内的列】紧凑 */
    /* 这里的 trick 是：通过限制内部按钮的宽度，让列自然收缩 */

    /* 3. 锁死按钮容器高度 (防止塌陷) */
    div.stButton {
        width: 100% !important; /* 填满列 */
        height: 40px !important;
        min-height: 40px !important;
        margin: 0 !important;
        line-height: 1 !important;
    }

    /* ============================================================
       方块样式 (Tile Styles)
       ============================================================ */

    /* 通用方块定义 */
    .tile-std {
        width: 40px !important;       /* 锁死宽度 */
        height: 40px !important;      /* 锁死高度 */
        min-width: 40px !important;
        
        border: 2px solid #2c3e50 !important;
        border-radius: 4px !important;
        box-sizing: border-box !important;
        
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        
        margin: 0 auto !important; /* 居中 */
    }

    /* A. 未揭开 (按钮) */
    /* 注意：Secondary 按钮是棋盘格子 */
    button[kind="secondary"] {
        @extend .tile-std;
        background-color: #ffffff !important;
        color: transparent !important;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.15) !important;
        transition: none !important;
    }
    button[kind="secondary"]:hover {
        background-color: #f0f0f0 !important;
        border-color: #000 !important;
    }
    button[kind="secondary"]:active {
        background-color: #e0e0e0 !important;
        box-shadow: none !important;
        transform: translate(1px, 1px);
    }

    /* B. 已揭开 (Div) */
    .cell-revealed {
        @extend .tile-std;
        background-color: #dfe6e9 !important;
        color: #2c3e50 !important;
        font-size: 20px; font-weight: bold;
        cursor: default;
        box-shadow: none !important;
    }

    .cell-bomb { color: #d63031 !important; font-size: 26px !important; }

    /* ============================================================
       顶部功能按钮 (Home / Start / Restart)
       ============================================================ */
    /* 这些是 Primary 按钮，我们允许它们宽度自适应，不要锁死 40px */
    button[kind="primary"] {
        background-color: #2c3e50 !important;
        border: 2px solid #000 !important;
        width: 100% !important;     /* 填满列宽 */
        height: auto !important;    /* 高度自适应 */
        min-height: 42px !important;
        border-radius: 8px !important;
        padding: 5px 10px !important;
    }
    button[kind="primary"] p {
        color: #ffffff !important;
        font-size: 18px !important;
        line-height: 1.5 !important;
    }
    button[kind="primary"]:hover { background-color: #000 !important; }

    /* 数字颜色 */
    .c1 { color: #0984e3 !important; } .c2 { color: #00b894 !important; }
    .c3 { color: #d63031 !important; } .c4 { color: #6c5ce7 !important; }

</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

st.title("Minesweeper")

if not st.session_state.running:
    st.markdown("### ✏️ Setup")
    
    c1, sp1, c2, sp2, c3 = st.columns([1, 0.5, 1, 0.5, 2])
    
    with c1:
        R = st.number_input("Rows", 5, 20, 10)
    with sp1: st.empty()
    with c2:
        C = st.number_input("Cols", 5, 20, 10)
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
    # 顶部栏：分配足够的空间给 Home 和 Restart
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
        if st.button("🔄 Restart", type="primary", use_container_width=True):
            cfg = st.session_state.game_config
            start(cfg['R'], cfg['C'], cfg['M'])
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.lost: st.markdown("<h2 style='color:#d63031;text-align:center'>Oops! Boom!</h2>", unsafe_allow_html=True)
    if st.session_state.won: st.markdown("<h2 style='color:#00b894;text-align:center'>You Win!</h2>", unsafe_allow_html=True)

    # 棋盘容器：垂直居中
    st.markdown("<div style='display:flex; flex-direction:column; align-items:center;'>", unsafe_allow_html=True)
    
    board = st.session_state.board
    vis = st.session_state.revealed
    flg = st.session_state.flags
    
    for r in range(st.session_state.rows):
        # 重点：给棋盘的列指定固定的像素宽度，防止被拉伸
        # 44px = 40px 格子 + 4px 间隙
        # 这样即使屏幕很宽，格子也会紧凑地排在中间
        cols = st.columns([1] * st.session_state.cols) 
        
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
                        # 游戏进行中
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
                        # 游戏结束
                        st.markdown(f"<div class='cell-revealed' style='background:#fff !important; color:#ccc !important;'>{label}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
