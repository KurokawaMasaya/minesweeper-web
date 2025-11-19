import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="Crayon Tiles", layout="centered", page_icon="🖍️")

# ================= 核心逻辑 =================
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
    M = max(0, min(M, R * C - 1))
    place(b,M)
    st.session_state.board = b
    st.session_state.revealed=set()
    st.session_state.flags=set()
    st.session_state.rows=R
    st.session_state.cols=C
    st.session_state.mines=M
    st.session_state.running=True
    st.session_state.lost=False
    st.session_state.won=False

if "running" not in st.session_state: st.session_state.running=False
if "flag" not in st.session_state: st.session_state.flag=False
if "lost" not in st.session_state: st.session_state.lost=False
if "won" not in st.session_state: st.session_state.won=False

# ================= 🎨 CSS 样式 (精准控制版) =================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    /* 1. App 背景 */
    .stApp {
        background-color: #fdfcf0;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }

    /* 2. 仅针对游戏内的文字应用手写体和颜色，不破坏系统菜单 */
    .stMarkdown, .stButton, .stSelectbox, .stNumberInput, h1 {
        font-family: 'Patrick Hand', cursive, sans-serif !important;
        color: #2c3e50;
    }
    
    h1 { text-align: center; color: #000 !important; margin-bottom: 10px; }

    /* ============================================================
       修复: 输入框样式 (白底黑字)
       ============================================================ */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    div[data-testid="stNumberInput"] > div {
        background-color: #ffffff !important;
        border: 2px solid #2c3e50 !important;
        border-radius: 6px !important;
        color: #000 !important;
    }
    
    /* 输入框内文字 */
    input.st-bd, input.st-be, div[data-baseweb="select"] span {
        color: #000 !important;
        font-weight: bold !important;
        font-size: 18px !important;
        -webkit-text-fill-color: #000 !important;
    }
    
    /* 修复数字框右侧按钮 */
    div[data-testid="stNumberInput"] svg { fill: #000 !important; }
    div[data-testid="stNumberInput"] > div > div { background-color: #fff !important; border-left: 1px solid #ccc !important; }

    /* 下拉菜单选项 */
    ul[data-baseweb="menu"] { background-color: #fff !important; border: 2px solid #2c3e50 !important; }
    li[data-baseweb="option"] { color: #000 !important; }

    /* ============================================================
       样式: 蜡笔方块棋盘 (有缝隙版)
       ============================================================ */
    
    /* 恢复 Streamlit 默认间距，不再强制 gap: 0 */
    
    /* 限制列宽，让格子是正方形的 */
    div[data-testid="column"] {
        width: 44px !important;
        flex: 0 0 44px !important;
        min-width: 44px !important;
        padding: 2px !important; /* 这里的 padding 就是缝隙 */
    }
    
    /* 居中对齐 */
    div[data-testid="stHorizontalBlock"] {
        justify-content: center !important;
    }

    /* 统一方块样式 */
    .tile-box {
        width: 40px !important;
        height: 40px !important;
        border-radius: 4px !important; /* 轻微圆角，像手绘 */
        border: 2px solid #2c3e50 !important; /* 粗黑边 */
        display: flex;
        align-items: center;
        justify-content: center;
        box-sizing: border-box !important;
    }

    /* 1. 未揭开 (按钮) - 亮白悬浮 */
    button[kind="secondary"] {
        @extend .tile-box;
        width: 40px !important; height: 40px !important;
        border: 2px solid #2c3e50 !important;
        border-radius: 4px !important;
        background-color: #ffffff !important;
        color: transparent !important;
        
        /* 加一点手绘阴影 */
        box-shadow: 2px 2px 0px rgba(0,0,0,0.2) !important;
        transition: transform 0.1s;
    }
    button[kind="secondary"]:hover {
        transform: translate(-1px, -1px);
        box-shadow: 3px 3px 0px rgba(0,0,0,0.2) !important;
        background-color: #f9f9f9 !important;
    }
    button[kind="secondary"]:active {
        transform: translate(1px, 1px);
        box-shadow: 1px 1px 0px rgba(0,0,0,0.2) !important;
    }

    /* 2. 已揭开 (Div) - 浅灰平铺 */
    .cell-revealed {
        width: 40px !important; height: 40px !important;
        border: 2px solid #2c3e50 !important;
        border-radius: 4px !important;
        box-sizing: border-box !important;
        
        background-color: #e0e0e0 !important; /* 明显的灰 */
        color: #2c3e50 !important;
        font-size: 20px; font-weight: bold;
        cursor: default;
        
        display: flex; align-items: center; justify-content: center;
        /* 已揭开没有阴影，看起来是平的 */
        box-shadow: none !important;
    }

    /* 炸弹样式 */
    .cell-bomb {
        color: #d63031 !important; /* 蜡笔红 */
        font-size: 28px !important;
        line-height: 1;
    }

    /* 开始按钮 */
    button[kind="primary"] {
        background-color: #2c3e50 !important;
        border: 2px solid #000 !important;
        width: 100%;
    }
    button[kind="primary"] p { color: #fff !important; font-size: 20px !important; }
    button[kind="primary"]:hover { background-color: #000 !important; }

    /* 数字颜色 */
    .c1 { color: #0984e3 !important; }
    .c2 { color: #00b894 !important; }
    .c3 { color: #d63031 !important; }
    .c4 { color: #6c5ce7 !important; }

</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

st.title("Minesweeper")

if not st.session_state.running:
    st.markdown("### ✏️ Setup")
    
    # 这里不需要 spacer 了，因为有自然间距
    c1, c2, c3 = st.columns([1, 1, 1.5])
    
    with c1: R = st.number_input("Rows", 5, 20, 10)
    with c2: C = st.number_input("Cols", 5, 20, 10)
    with c3: 
        diff = st.selectbox("Diff", ["Easy (10%)", "Med (15%)", "Hard (20%)"])
        rate = 0.10 if "Easy" in diff else (0.15 if "Med" in diff else 0.20)
    
    M = max(1, int(R*C*rate))
    st.write(f"**Mines:** {M}")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("START GAME", type="primary", use_container_width=True):
        start(R, C, M)
        st.rerun()

else:
    c1, c2, c3 = st.columns([1.5, 2, 1.5])
    with c2:
        left = st.session_state.mines - len(st.session_state.flags)
        st.markdown(f"<div style='text-align:center; font-size:24px; font-weight:bold; padding-top:5px;'>{left} 💣</div>", unsafe_allow_html=True)
    with c1:
        mode = "🚩 Flag" if st.session_state.flag else "⛏️ Dig"
        if st.button(mode, type="primary", use_container_width=True):
            st.session_state.flag = not st.session_state.flag
            st.rerun()
    with c3:
        if st.button("Restart", type="primary", use_container_width=True):
            st.session_state.running = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.lost: st.markdown("<h2 style='color:#d63031;text-align:center'>Oops! Boom!</h2>", unsafe_allow_html=True)
    if st.session_state.won: st.markdown("<h2 style='color:#00b894;text-align:center'>You Win!</h2>", unsafe_allow_html=True)

    # === 渲染网格 (有缝隙版) ===
    # 不需要 board-wrap 了，因为是散开的方块
    st.markdown("<div style='display:flex; justify-content:center; flex-direction:column; align-items:center;'>", unsafe_allow_html=True)
    
    board = st.session_state.board
    vis = st.session_state.revealed
    flg = st.session_state.flags
    
    for r in range(st.session_state.rows):
        cols = st.columns(st.session_state.cols)
        for c in range(st.session_state.cols):
            with cols[c]:
                key = f"{r}_{c}"
                is_rev = (r,c) in vis
                is_flg = (r,c) in flg
                end = st.session_state.lost or st.session_state.won
                
                # 1. 已揭开
                if is_rev or (end and board[r][c] == -1):
                    val = board[r][c]
                    if val == -1:
                        # 红色蜡笔X
                        st.markdown("<div class='cell-revealed cell-bomb'>X</div>", unsafe_allow_html=True)
                    elif val == 0:
                        st.markdown("<div class='cell-revealed'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='cell-revealed c{val}'>{val}</div>", unsafe_allow_html=True)
                
                # 2. 未揭开
                else:
                    label = "P" if is_flg else " "
                    if not end:
                        if st.button(label, key=key, type="secondary"):
                            if st.session_state.flag:
                                if is_flg: flg.remove((r,c))
                                else: flg.add((r,c))
                                st.rerun()
                            elif not is_flg:
                                if not reveal(board, vis, flg, r, c):
                                    st.session_state.lost = True
                                st.rerun()
                    else:
                        st.markdown(f"<div class='cell-revealed' style='background:#fff !important; color:#ccc !important;'>{label}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
