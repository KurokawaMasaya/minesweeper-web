import streamlit as st
import random

# 页面配置 (宽屏模式，给手机更多空间)
st.set_page_config(page_title="Mobile Minesweeper", layout="wide", page_icon="🖍️")

# ================= 核心逻辑 (不变) =================
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

# ================= 🎨 CSS (全端适配 + 涂鸦风) =================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    /* 1. 颜色变量 (自适应深浅模式) */
    :root {
        /* ☀️ 浅色模式 */
        --bg-color: #fdfcf0;
        --text-color: #2c3e50;
        --box-bg: #ffffff;
        --box-border: #2c3e50;
        --revealed-bg: #dfe6e9;
        --accent-bg: #2c3e50;
        --accent-text: #ffffff;
        --bomb-color: #d63031;
        --hover-bg: #f0f0f0;
    }
    @media (prefers-color-scheme: dark) {
        :root {
            /* 🌙 深色模式 */
            --bg-color: #1a1a1a;
            --text-color: #ecf0f1;
            --box-bg: #2d3436;
            --box-border: #ecf0f1;
            --revealed-bg: #404040;
            --accent-bg: #ecf0f1;
            --accent-text: #2c3e50;
            --bomb-color: #ff7675;
            --hover-bg: #3d3d3d;
        }
    }

    /* 2. 全局应用 */
    .stApp {
        background-color: var(--bg-color) !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
        color: var(--text-color) !important;
    }
    h1, h2, h3, p, label, span, div, button {
        color: var(--text-color) !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    h1 { text-align: center; }

    /* ============================================================
       🚨 手机适配核心 (Mobile Responsive Core) 🚨
       ============================================================ */
    
    /* 1. 强制棋盘所在的行【不换行】，并在溢出时【横向滚动】 */
    /* 这里的 selector 必须很精准，防止影响顶部菜单 */
    .board-container div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important; /* 禁止手机自动换行 */
        overflow-x: auto !important;  /* 允许左右滑动 */
        justify-content: flex-start !important; /* 从左对齐，方便滑动 */
        gap: 2px !important; /* 极小间隙 */
        
        /* 隐藏滚动条但保持功能 (Chrome/Safari) */
        scrollbar-width: none; 
        -ms-overflow-style: none;
    }
    .board-container div[data-testid="stHorizontalBlock"]::-webkit-scrollbar { 
        display: none; 
    }

    /* 2. 限制列宽：既不能太小(按不到)，也不能太大 */
    .board-container div[data-testid="column"] {
        flex: 0 0 auto !important;
        width: 38px !important;     /* 手机上最佳触控尺寸 */
        min-width: 38px !important; /* 绝对不许小于这个 */
        padding: 0 !important;
        margin: 0 !important;
    }

    /* 3. 锁死格子高度 */
    div.stButton {
        width: 38px !important;
        height: 38px !important;
        min-height: 38px !important;
        margin: 0 !important;
        line-height: 1 !important;
    }

    /* ============================================================
       棋盘格子样式
       ============================================================ */

    .tile-std {
        width: 38px !important;
        height: 38px !important;
        border: 2px solid var(--box-border) !important;
        border-radius: 4px !important;
        box-sizing: border-box !important;
        display: flex; align-items: center; justify-content: center;
        line-height: 1 !important;
    }

    /* A. 未揭开 (按钮) */
    button[kind="secondary"] {
        @extend .tile-std;
        background-color: var(--box-bg) !important;
        color: transparent !important;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.15) !important;
        padding: 0 !important;
        transition: none !important;
    }
    button[kind="secondary"]:hover {
        background-color: var(--hover-bg) !important;
        border-color: var(--box-border) !important;
    }
    button[kind="secondary"]:active {
        background-color: var(--revealed-bg) !important;
        box-shadow: none !important;
    }

    /* B. 已揭开 (Div) */
    .cell-revealed {
        @extend .tile-std;
        background-color: var(--revealed-bg) !important;
        color: var(--text-color) !important;
        font-size: 18px; font-weight: bold;
        cursor: default;
        box-shadow: none !important;
        margin: 0 !important;
    }

    .cell-bomb { color: var(--bomb-color) !important; font-size: 24px !important; }

    /* ============================================================
       其他控件 (输入框、按钮)
       ============================================================ */
    
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    div[data-testid="stNumberInput"] > div {
        background-color: var(--box-bg) !important;
        border: 2px solid var(--box-border) !important;
        color: var(--text-color) !important;
    }
    input[type="number"], div[data-baseweb="select"] span, div[data-testid="stNumberInput"] input {
        color: var(--text-color) !important;
        -webkit-text-fill-color: var(--text-color) !important;
        caret-color: var(--text-color) !important;
        font-weight: bold !important;
        text-align: center;
    }
    div[data-baseweb="select"] svg { fill: var(--text-color) !important; }
    div[data-testid="stNumberInput"] button { display: none !important; }

    ul[data-baseweb="menu"] {
        background-color: var(--box-bg) !important;
        border: 2px solid var(--box-border) !important;
    }
    li[data-baseweb="option"] {
        background-color: var(--box-bg) !important;
        color: var(--text-color) !important;
    }
    li[data-baseweb="option"]:hover, li[data-baseweb="option"][aria-selected="true"] {
        background-color: var(--hover-bg) !important;
        color: var(--text-color) !important;
    }

    /* 功能按钮 */
    button[kind="primary"] {
        background-color: var(--accent-bg) !important;
        border: 2px solid var(--box-border) !important;
        width: 100%;
    }
    button[kind="primary"] p { color: var(--accent-text) !important; }
    button[kind="primary"]:hover { opacity: 0.9; }

    .c1 { color: #3498db !important; } .c2 { color: #2ecc71 !important; }
    .c3 { color: #e74c3c !important; } .c4 { color: #9b59b6 !important; }

</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

st.title("Minesweeper")

if not st.session_state.running:
    st.markdown("### ✏️ Setup")
    
    # 设置栏：为了手机显示正常，使用正常的列宽
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1: R = st.number_input("Rows", 5, 20, 10)
    with c2: C = st.number_input("Cols", 5, 20, 10)
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
    # 顶部控制栏：手机上可能需要两行，这里使用自动布局
    # Home | Mode
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 Home", type="primary", use_container_width=True):
            st.session_state.running = False
            st.rerun()
    with c2:
        mode = "🚩 Flag" if st.session_state.flag else "⛏️ Dig"
        if st.button(mode, type="primary", use_container_width=True):
            st.session_state.flag = not st.session_state.flag
            st.rerun()
    
    # Status | Restart
    c3, c4 = st.columns([2, 1])
    with c3:
        left = st.session_state.mines - len(st.session_state.flags)
        st.markdown(f"<div style='text-align:center; font-size:22px; font-weight:bold; padding-top:8px;'>{left} 💣 Left</div>", unsafe_allow_html=True)
    with c4:
        if st.button("🔄", type="primary", use_container_width=True):
            cfg = st.session_state.game_config
            start(cfg['R'], cfg['C'], cfg['M'])
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.lost: st.markdown(f"<h2 style='text-align:center; color:var(--bomb-color);'>Oops! Boom!</h2>", unsafe_allow_html=True)
    if st.session_state.won: st.markdown("<h2 style='text-align:center; color:#2ecc71;'>You Win!</h2>", unsafe_allow_html=True)

    # ================= 渲染棋盘 (带横向滚动容器) =================
    # 使用一个特殊的 div 包裹整个棋盘，加上 class='board-container'
    st.markdown('<div class="board-container">', unsafe_allow_html=True)
    
    # 外层容器居中
    st.markdown("<div style='display:flex; justify-content:center;'><div>", unsafe_allow_html=True)
    
    board = st.session_state.board
    vis = st.session_state.revealed
    flg = st.session_state.flags
    
    for r in range(st.session_state.rows):
        # 这里生成的 columns 会被 CSS 强制不换行 + 允许滑动
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
                        st.markdown(f"<div class='cell-revealed' style='background-color:var(--box-bg) !important; opacity:0.6;'>{label}</div>", unsafe_allow_html=True)

    st.markdown("</div></div></div>", unsafe_allow_html=True)
