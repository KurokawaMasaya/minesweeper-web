import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="Scalable Paper Minesweeper", layout="centered", page_icon="🖍️")

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

# ================= 🎨 CSS (等比缩放·纸张版) =================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    /* 1. 全局背景与文字 */
    .stApp {
        background-color: #333333 !important; /* 桌面背景深色，突显中间的纸 */
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    
    h1, h2, h3, p, label, span, div, button {
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    h1 { color: #fdfcf0 !important; text-align: center; margin-bottom: 20px; }

    /* ============================================================
       📜 核心容器：那张“纸” (Paper Container)
       ============================================================ */
    .paper-sheet {
        background-color: #fdfcf0; /* 米色纸张 */
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); /* 纸张投影 */
        margin: 0 auto;
        
        /* ⚡️ 核心缩放逻辑 ⚡️ */
        width: min(600px, 95vw); /* 电脑上600px，手机上占95%屏幕宽 */
        /* 这样里面的内容就会随纸张大小自动缩放 */
    }
    
    /* 纸张里的所有文字变成深色 */
    .paper-sheet h2, .paper-sheet div, .paper-sheet p, .paper-sheet span, .paper-sheet button {
        color: #2c3e50 !important;
    }

    /* ============================================================
       棋盘网格 (Flexible Grid)
       ============================================================ */
    
    /* 1. 行布局：自动平分宽度 */
    div[data-testid="stHorizontalBlock"] {
        gap: 2px !important; /* 极小间隙 */
        justify-content: center !important;
    }

    /* 2. 列容器：按比例伸缩 */
    div[data-testid="column"] {
        flex: 1 1 0 !important; /* 所有列平分宽度 */
        width: auto !important;
        min-width: 0 !important; /* 允许无限缩小 */
        padding: 0 !important;
        margin: 0 !important;
    }

    /* 3. ⚡️ 方块自适应核心 ⚡️ */
    
    /* 按钮容器 */
    div.stButton {
        width: 100% !important;
        height: auto !important; /* 高度随宽度变 */
        aspect-ratio: 1 / 1 !important; /* 强制正方形 */
        padding: 0 !important;
        margin: 0 !important;
        line-height: 0 !important;
    }

    /* 通用样式 (按钮 & Div) */
    .responsive-tile {
        width: 100% !important;
        height: 100% !important; /* 填满正方形容器 */
        
        border: 1.5px solid #2c3e50 !important; /* 稍微细一点的边框适应手机 */
        border-radius: 15% !important; /* 相对圆角 */
        box-sizing: border-box !important;
        
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        
        /* ⚡️ 字体大小随视口变化 ⚡️ */
        /* 在小屏幕小字，大屏幕大字 */
        font-size: clamp(12px, 3.5vw, 24px) !important; 
        font-weight: bold !important;
        padding: 0 !important;
    }

    /* A. 未揭开 */
    button[kind="secondary"] {
        @extend .responsive-tile;
        background-color: #ffffff !important;
        color: transparent !important;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.1) !important;
        transition: none !important;
    }
    button[kind="secondary"]:hover { background-color: #f9f9f9 !important; }
    button[kind="secondary"]:active { box-shadow: none !important; transform: translate(1px, 1px); }

    /* B. 已揭开 */
    .cell-revealed {
        @extend .responsive-tile;
        background-color: #dfe6e9 !important;
        color: #2c3e50 !important;
        cursor: default;
        box-shadow: none !important;
    }
    
    .cell-bomb { color: #d63031 !important; }

    /* ============================================================
       输入框 & 按钮 (保证清晰度)
       ============================================================ */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, div[data-testid="stNumberInput"] > div {
        background-color: #fff !important; border: 2px solid #2c3e50 !important; color: #000 !important;
    }
    input, div[data-baseweb="select"] span { color: #000 !important; font-weight: bold; text-align: center;}
    div[data-testid="stNumberInput"] button { display: none !important; }
    div[data-baseweb="select"] svg { fill: #000 !important; }
    
    ul[data-baseweb="menu"] { background-color: #fff !important; border: 2px solid #2c3e50 !important; }
    li[data-baseweb="option"] { color: #000 !important; background-color: #fff !important; }
    li[data-baseweb="option"]:hover { background-color: #eee !important; }

    button[kind="primary"] {
        background-color: #2c3e50 !important; border: 2px solid #000 !important; width: 100%;
    }
    button[kind="primary"] p { color: #fff !important; }
    button[kind="primary"]:hover { background-color: #000 !important; }

    /* 顶部布局调整 */
    .top-bar-text { font-size: 20px; font-weight: bold; text-align: center; padding-top: 10px; }
    
    .c1 { color: #0984e3 !important; } .c2 { color: #00b894 !important; }
    .c3 { color: #d63031 !important; } .c4 { color: #6c5ce7 !important; }

</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

st.title("Minesweeper")

# 包裹整个内容的“纸张”
st.markdown('<div class="paper-sheet">', unsafe_allow_html=True)

# 1. 设置界面
if not st.session_state.running:
    st.markdown("### ✏️ Setup")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1: R = st.number_input("Rows", 5, 20, 10)
    with c2: C = st.number_input("Cols", 5, 20, 10)
    with c3: 
        diff = st.selectbox("Diff", ["Easy (10%)", "Med (15%)", "Hard (20%)"])
        rate = 0.10 if "Easy" in diff else (0.15 if "Med" in diff else 0.20)
    
    M = max(1, int(R * C * rate))
    st.markdown(f"<div style='text-align:center; margin:10px 0;'>Mines: <b>{M}</b></div>", unsafe_allow_html=True)
    
    if st.button("START GAME", type="primary", use_container_width=True):
        start(R, C, M)
        st.rerun()

# 2. 游戏界面
else:
    # 顶部栏 (两行布局，适应窄屏)
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🏠 Home", type="primary", use_container_width=True):
            st.session_state.running = False
            st.rerun()
    with c2:
        if st.button("🔄 Restart", type="primary", use_container_width=True):
            cfg = st.session_state.game_config
            start(cfg['R'], cfg['C'], cfg['M'])
            st.rerun()
    
    c3, c4 = st.columns([1, 1.5])
    with c3:
        mode_txt = "Flag" if st.session_state.flag else "Dig"
        icon = "🚩" if st.session_state.flag else "⛏️"
        if st.button(f"{icon} {mode_txt}", type="primary", use_container_width=True):
            st.session_state.flag = not st.session_state.flag
            st.rerun()
    with c4:
        left = st.session_state.mines - len(st.session_state.flags)
        st.markdown(f"<div class='top-bar-text'>{left} 💣 Left</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border-top: 2px dashed #ccc; margin: 15px 0;'>", unsafe_allow_html=True)

    if st.session_state.lost: st.markdown("<h2 style='color:#d63031;text-align:center'>Oops! Boom!</h2>", unsafe_allow_html=True)
    if st.session_state.won: st.markdown("<h2 style='color:#00b894;text-align:center'>You Win!</h2>", unsafe_allow_html=True)

    # === 棋盘渲染 (自动缩放) ===
    board = st.session_state.board
    vis = st.session_state.revealed
    flg = st.session_state.flags
    
    for r in range(st.session_state.rows):
        # 这里不加宽度限制，让CSS的flex布局自动平分
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
                        st.markdown(f"<div class='cell-revealed' style='background-color:#fff !important; opacity:0.6;'>{label}</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # End paper-sheet
