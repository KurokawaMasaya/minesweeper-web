import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="Perfect Grid Minesweeper", layout="centered", page_icon="📐")

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

# ================= 🎨 终极 CSS 修复 =================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    /* 全局字体和背景 */
    .stApp {
        background-color: #fdfcf0;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    
    /* 强制所有文本深色 */
    h1, p, label, span, div, button {
        color: #2c3e50 !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    
    /* 标题居中加黑 */
    h1 { color: #000 !important; text-align: center; }

    /* ============================================================
       🔧 修复 1: 输入框样式 (黑底白字)
       ============================================================ */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div {
        background-color: #2c3e50 !important;
        border: 2px solid #000 !important;
        color: white !important;
        border-radius: 4px !important;
    }
    div[data-baseweb="select"] span, 
    div[data-testid="stNumberInput"] input {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: white !important;
        font-weight: bold !important;
    }
    div[data-baseweb="select"] svg { fill: white !important; }

    /* ============================================================
       🔧 修复 2: 棋盘完全无缝 (井字棋)
       关键在于：强制列宽收缩 (flex: 0 0 auto)，不让它自动拉伸
       ============================================================ */

    /* 1. 行容器：去除间距，居中对齐 */
    div[data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        justify-content: center !important; /* 关键：让挤在一起的列居中 */
    }
    
    /* 2. 列容器：强制收缩！禁止拉伸！ */
    div[data-testid="column"] {
        flex: 0 0 auto !important; /* 关键：宽度由内容决定，不要自动平分屏幕 */
        width: auto !important;
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* 3. 统一格子模型 (按钮 & 已揭开) */
    button[kind="secondary"], .cell-revealed {
        width: 40px !important;
        height: 40px !important;
        border: 1px solid #000 !important;
        border-radius: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        
        /* 负边距：消除双重边框 */
        margin-right: -1px !important;
        margin-bottom: -1px !important;
        
        box-sizing: border-box !important;
        display: flex !important; 
        align-items: center !important; 
        justify-content: center !important;
    }

    /* 4. 未揭开 (白纸) */
    button[kind="secondary"] {
        background-color: #ffffff !important;
        color: transparent !important;
        z-index: 10; /* 浮在上面 */
    }
    button[kind="secondary"]:hover {
        background-color: #f0f0f0 !important;
        z-index: 20;
    }

    /* 5. 已揭开 (深灰凹陷) */
    .cell-revealed {
        background-color: #999999 !important;
        color: #fff !important;
        font-size: 22px; font-weight: bold;
        cursor: default; z-index: 1;
    }

    /* 炸弹样式 (蜡笔红X) */
    .cell-bomb {
        background-color: #999999 !important; /* 背景同普通已揭开 */
        color: #d63031 !important;
        font-size: 30px !important;
    }

    /* 外框装饰 (包裹整个棋盘) */
    .board-wrap {
        display: inline-block;
        border-top: 2px solid #000;
        border-left: 2px solid #000;
        line-height: 0;
        margin-top: 20px;
    }

    /* ============================================================
       🔧 修复 3: 开始按钮
       ============================================================ */
    button[kind="primary"] {
        background-color: #2c3e50 !important;
        border: 3px solid #000 !important;
        width: 100%;
    }
    button[kind="primary"] p {
        color: #ffffff !important;
        font-size: 20px !important;
    }
    button[kind="primary"]:hover { background-color: #000 !important; }

    /* 数字颜色 */
    .c1 { color: #cbf3f0 !important; text-shadow: 1px 1px 0 #000; }
    .c2 { color: #b5e48c !important; text-shadow: 1px 1px 0 #000; }
    .c3 { color: #ff99c8 !important; text-shadow: 1px 1px 0 #000; }
    
</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

st.title("Minesweeper")

if not st.session_state.running:
    st.markdown("### ✏️ Setup")
    
    # 使用 Spacer 列来物理隔开输入框
    c1, sp1, c2, sp2, c3 = st.columns([1, 0.2, 1, 0.2, 1.5])
    
    with c1: R = st.number_input("Rows", 5, 20, 10)
    with sp1: st.empty()
    with c2: C = st.number_input("Cols", 5, 20, 10)
    with sp2: st.empty()
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
    c1, sp1, c2, sp2, c3 = st.columns([1.5, 0.2, 2, 0.2, 1.5])
    with c2:
        left = st.session_state.mines - len(st.session_state.flags)
        st.markdown(f"<div style='text-align:center; font-size:24px; font-weight:bold;'>{left} 💣</div>", unsafe_allow_html=True)
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
    
    if st.session_state.lost: st.markdown("<h2 style='color:#d63031;text-align:center'>Oops! X_X</h2>", unsafe_allow_html=True)
    if st.session_state.won: st.markdown("<h2 style='color:#00b894;text-align:center'>You Win!</h2>", unsafe_allow_html=True)

    # === 渲染网格 ===
    st.markdown("<div style='display:flex; justify-content:center;'>", unsafe_allow_html=True)
    st.markdown("<div class='board-wrap'>", unsafe_allow_html=True)
    
    board = st.session_state.board
    vis = st.session_state.revealed
    flg = st.session_state.flags
    
    for r in range(st.session_state.rows):
        # 注意：这里必须把 columns 对象存下来，利用上下文管理器逐个渲染
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
                        # 炸弹：蜡笔红 X
                        st.markdown("<div class='cell-revealed cell-bomb'>X</div>", unsafe_allow_html=True)
                    elif val == 0:
                        st.markdown("<div class='cell-revealed'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='cell-revealed c{val}'>{val}</div>", unsafe_allow_html=True)
                
                # 2. 未揭开 (按钮)
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
                        # 游戏结束后的未揭开区域
                        st.markdown(f"<div class='cell-revealed' style='background:#fff !important; color:#ccc !important;'>{label}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
