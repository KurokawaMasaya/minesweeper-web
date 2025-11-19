import streamlit as st
import random

# 页面配置：手绘风
st.set_page_config(page_title="Tic-Tac-Toe Minesweeper", layout="centered", page_icon="❌")

# ================= 核心逻辑 (保持不变) =================
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

# ================= 🖍️ 井字棋风格 CSS =================

st.markdown("""
<style>
    /* 1. 引入手写字体 Patrick Hand */
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    .stApp {
        background-color: #fdfcf0;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    
    h1, div, button, span, p {
        font-family: 'Patrick Hand', cursive, sans-serif !important;
        color: #2c3e50;
    }

    /* ============================================
       关键 CSS：消除缝隙的黑魔法
       ============================================ */

    /* 1. 强制移除 st.columns 之间的 Gap */
    div[data-testid="stHorizontalBlock"] {
        gap: 0 !important; 
    }
    
    /* 2. 移除列的所有 Padding，确保宽度被格子撑满 */
    div[data-testid="column"] {
        width: 42px !important;
        flex: 0 0 42px !important;
        padding: 0 !important;
        margin: 0 !important;
        min-width: 0 !important;
    }

    /* 3. 按钮/格子样式：负边距重叠 */
    
    /* 通用格子大小 */
    .grid-cell {
        width: 42px !important;
        height: 42px !important;
        box-sizing: border-box !important; /* 确保边框算在宽度内 */
    }

    /* 未揭开的按钮 (Secondary) */
    button[kind="secondary"] {
        width: 42px !important;
        height: 42px !important;
        border-radius: 0 !important; /* 直角 */
        border: 1px solid #2c3e50 !important; /* 深色网格线 */
        background-color: transparent !important;
        color: transparent !important;
        
        /* 关键：负边距，让边框重叠，形成单线网格 */
        margin-right: -1px !important;
        margin-bottom: -1px !important;
        z-index: 1;
    }
    button[kind="secondary"]:hover {
        background-color: rgba(0,0,0,0.05) !important;
        z-index: 2; /* 悬浮时浮起，防止边框被遮挡 */
    }

    /* 已揭开的格子 */
    .cell-revealed {
        width: 42px; height: 42px;
        display: flex; align-items: center; justify-content: center;
        border: 1px solid #2c3e50;
        background-color: rgba(0,0,0,0.02);
        font-size: 24px;
        font-weight: bold;
        cursor: default;
        
        /* 同样使用负边距重叠 */
        margin-right: -1px;
        margin-bottom: -1px;
        box-sizing: border-box;
    }

    /* 4. 外层大边框 (包裹整个棋盘) */
    .board-wrapper {
        display: inline-block;
        border-top: 2px solid #2c3e50;
        border-left: 2px solid #2c3e50;
        /* 右下边框由里面的格子溢出撑开，或者这里补齐 */
        padding: 0;
        line-height: 0; /* 消除行高导致的垂直间隙 */
    }

    /* ============================================ */

    /* 功能按钮 (Start/Restart) - 手绘圆角 */
    button[kind="primary"] {
        background: transparent !important;
        color: #2c3e50 !important;
        border: 2px solid #2c3e50 !important;
        border-radius: 255px 15px 225px 15px / 15px 225px 15px 255px !important;
        font-size: 20px !important;
    }
    button[kind="primary"]:hover {
        background-color: #fff !important;
    }

    /* 颜色 */
    .c1 { color: #2980b9; } .c2 { color: #27ae60; } .c3 { color: #c0392b; }
    .bomb-drawn { color: #000; font-size: 30px; line-height: 40px; }
    
</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

st.title("Minesweeper")

# 1. 设置
if not st.session_state.running:
    st.markdown("### ✏️ Setup")
    c1, c2, c3 = st.columns(3)
    with c1: R = st.number_input("Rows", 5, 20, 10)
    with c2: C = st.number_input("Cols", 5, 20, 10)
    with c3: 
        diff = st.selectbox("Diff", ["Easy (10%)", "Med (15%)", "Hard (20%)"])
        rate = 0.10 if "Easy" in diff else (0.15 if "Med" in diff else 0.20)
    
    M = max(1, int(R*C*rate))
    st.write(f"Mines: **{M}**")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Start Game", type="primary", use_container_width=True):
        start(R, C, M)
        st.rerun()

# 2. 游戏界面
else:
    # 顶部状态
    c1, c2, c3 = st.columns([1.5, 2, 1.5])
    with c2:
        left = st.session_state.mines - len(st.session_state.flags)
        st.markdown(f"<div style='text-align:center; font-size:24px;'>{left} 💣 Left</div>", unsafe_allow_html=True)
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

    if st.session_state.lost: st.markdown("<h2 style='color:#c0392b;text-align:center'>Game Over!</h2>", unsafe_allow_html=True)
    if st.session_state.won: st.markdown("<h2 style='color:#27ae60;text-align:center'>You Win!</h2>", unsafe_allow_html=True)

    # === 渲染井字棋盘 ===
    
    # 使用 Flexbox 居中
    st.markdown("<div style='display:flex; justify-content:center;'>", unsafe_allow_html=True)
    
    # 外层包裹器：负责左上边框
    st.markdown("<div class='board-wrapper'>", unsafe_allow_html=True)
    
    board = st.session_state.board
    vis = st.session_state.revealed
    flg = st.session_state.flags
    
    for r in range(st.session_state.rows):
        # Streamlit 的 columns 默认有 Gap，CSS 已强制设为 0
        cols = st.columns(st.session_state.cols)
        
        for c in range(st.session_state.cols):
            with cols[c]:
                key = f"{r}_{c}"
                is_rev = (r,c) in vis
                is_flg = (r,c) in flg
                end = st.session_state.lost or st.session_state.won
                
                # A. 显示内容 (已揭开)
                if is_rev or (end and board[r][c] == -1):
                    val = board[r][c]
                    if val == -1:
                        # 手绘风的炸弹：X
                        st.markdown("<div class='cell-revealed bomb-drawn'>X</div>", unsafe_allow_html=True)
                    elif val == 0:
                        st.markdown("<div class='cell-revealed'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='cell-revealed c{val}'>{val}</div>", unsafe_allow_html=True)
                
                # B. 按钮 (未揭开)
                else:
                    # 用 P 代表旗子
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
                        st.markdown(f"<div class='cell-revealed' style='color:#ccc'>{label}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True) # End board-wrapper
    st.markdown("</div>", unsafe_allow_html=True) # End center
