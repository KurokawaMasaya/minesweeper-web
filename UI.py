import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="Fixed Minesweeper", layout="centered", page_icon="🖍️")

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

# ================= 🎨 CSS (布局修复 + 防抖 + 可见性) =================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    /* 1. 颜色变量定义 (自适应) */
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
            /* 🌙 深色模式修正：背景纯黑，格子深灰，文字白 */
            --bg-color: #1a1a1a;
            --text-color: #ecf0f1;
            --box-bg: #2d3436;
            --box-border: #ecf0f1;
            --revealed-bg: #4a4a4a; /* 调亮一点，防止和纯黑背景混淆 */
            --accent-bg: #ecf0f1;
            --accent-text: #2c3e50;
            --bomb-color: #ff7675;
            --hover-bg: #3d3d3d;
        }
    }

    /* 全局应用 */
    .stApp {
        background-color: var(--bg-color) !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
        color: var(--text-color) !important;
    }
    
    h1, h2, h3, p, label, span, div {
        color: var(--text-color) !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    h1 { text-align: center; }

    /* ============================================
       输入框 & 菜单
       ============================================ */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    div[data-testid="stNumberInput"] > div {
        background-color: var(--box-bg) !important;
        border: 2px solid var(--box-border) !important;
        color: var(--text-color) !important;
        border-radius: 4px !important;
        box-shadow: none !important;
    }

    input[type="number"], div[data-baseweb="select"] span, div[data-testid="stNumberInput"] input {
        color: var(--text-color) !important;
        -webkit-text-fill-color: var(--text-color) !important;
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

    /* ============================================
       🚨 布局核心修复 🚨
       ============================================ */

    /* 1. 让列内容居中，但不强制锁死列宽，防止顶部按钮被挤扁 */
    div[data-testid="column"] {
        display: flex !important;
        justify-content: center !important; /* 让格子在列里居中 */
        align-items: center !important;
        min-width: 0 !important;
    }

    /* 2. 棋盘行间距 */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.3rem !important; /* 稍微紧凑一点 */
        justify-content: center !important;
    }

    /* 3. ⚡️ 棋盘格子 (Secondary Button) 物理锁定 ⚡️ */
    button[kind="secondary"] {
        width: 40px !important;
        height: 40px !important;
        min-height: 40px !important;
        max-height: 40px !important;
        
        border: 2px solid var(--box-border) !important;
        border-radius: 4px !important;
        background-color: var(--box-bg) !important;
        
        padding: 0 !important;
        margin: 0 !important;
        
        /* 防止变色 */
        color: transparent !important;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.2) !important;
        transition: none !important;
    }
    button[kind="secondary"]:hover {
        background-color: var(--hover-bg) !important;
        border-color: var(--box-border) !important;
    }
    button[kind="secondary"]:active {
        box-shadow: none !important;
        transform: translate(1px, 1px);
    }

    /* 4. ⚡️ 已揭开方块 (Div) 物理锁定 ⚡️ */
    /* 必须和上面的 button 尺寸属性 100% 一致 */
    .cell-revealed {
        width: 40px !important;
        height: 40px !important;
        min-height: 40px !important; /* 关键防抖 */
        
        border: 2px solid var(--box-border) !important;
        border-radius: 4px !important;
        box-sizing: border-box !important;
        
        background-color: var(--revealed-bg) !important;
        color: var(--text-color) !important;
        
        font-family: 'Patrick Hand', cursive, sans-serif !important;
        font-size: 20px !important;
        font-weight: bold !important;
        line-height: 1 !important;
        
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: default;
        margin: 0 !important;
    }

    /* 5. 顶部大按钮 (Primary Button) 恢复正常 */
    button[kind="primary"] {
        width: 100% !important;
        height: auto !important;
        min-height: 45px !important;
        background-color: var(--accent-bg) !important;
        border: 2px solid var(--box-border) !important;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.2) !important;
    }
    button[kind="primary"] p { color: var(--accent-text) !important; font-size: 18px !important; }
    button[kind="primary"]:hover { opacity: 0.9; }
    button[kind="primary"]:active { transform: translate(1px, 1px); box-shadow: none !important; }

    .cell-bomb { color: var(--bomb-color) !important; font-size: 28px !important; }
    .c1 { color: #3498db !important; } .c2 { color: #2ecc71 !important; }
    .c3 { color: #e74c3c !important; } .c4 { color: #9b59b6 !important; }

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
    # 顶部栏：Home | Mode | Status | Restart
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
        st.markdown(f"<div style='text-align:center; font-size:22px; font-weight:bold; padding-top:8px;'>{left} 💣 Left</div>", unsafe_allow_html=True)
    with c4:
        if st.button("🔄", type="primary", use_container_width=True, help="Restart"):
            cfg = st.session_state.game_config
            start(cfg['R'], cfg['C'], cfg['M'])
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.lost: st.markdown("<h2 style='text-align:center; color:var(--bomb-color);'>Oops! Boom!</h2>", unsafe_allow_html=True)
    if st.session_state.won: st.markdown("<h2 style='text-align:center; color:#2ecc71;'>You Win!</h2>", unsafe_allow_html=True)

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
                        # 游戏结束后，未揭开的格子保持背景色
                        st.markdown(f"<div class='cell-revealed' style='background-color:var(--box-bg) !important; opacity:0.6;'>{label}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
