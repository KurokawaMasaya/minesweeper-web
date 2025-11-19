import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="High Contrast Minesweeper", layout="centered", page_icon="📝")

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

# ================= 🎨 CSS 样式 =================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    .stApp {
        background-color: #fdfcf0;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    
    h1, p, label, span, div {
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }

    /* ============================================================
       修复 1: 输入框改为【深色背景 + 白色字体】
       ============================================================ */
    
    /* 覆盖输入框容器 */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div {
        background-color: #2c3e50 !important; /* 深色底 */
        border: 2px solid #000 !important;
        border-radius: 4px !important;
        color: white !important; /* 白字 */
    }

    /* 覆盖输入框内的文字 */
    div[data-baseweb="select"] span, 
    div[data-testid="stNumberInput"] input {
        color: #ffffff !important; /* 强制白色 */
        font-size: 18px !important;
        font-weight: bold !important;
        -webkit-text-fill-color: #ffffff !important; /* 兼容性强制 */
    }
    
    /* 下拉箭头颜色 */
    div[data-baseweb="select"] svg {
        fill: white !important;
        color: white !important;
    }
    
    /* 下拉菜单选项 */
    ul[data-baseweb="menu"] {
        background-color: #2c3e50 !important;
        color: white !important;
    }
    li[data-baseweb="option"] {
        color: white !important;
    }

    /* Label 颜色 (Rows, Cols, Diff) 保持深色以便在米色背景看清 */
    div[data-testid="stMarkdownContainer"] p, label {
        color: #2c3e50 !important;
        font-weight: bold !important;
    }

    /* ============================================================
       修复 2: 游戏格子极高对比度 (黑白灰分明)
       ============================================================ */

    /* 布局无缝 */
    div[data-testid="stHorizontalBlock"] { gap: 0 !important; }
    div[data-testid="column"] {
        width: 40px !important; min-width: 40px !important; flex: 0 0 40px !important;
        padding: 0 !important; margin: 0 !important;
    }

    /* 通用盒子 */
    button[kind="secondary"], .cell-revealed {
        width: 40px !important; height: 40px !important;
        border: 1px solid #000 !important; /* 纯黑边框 */
        border-radius: 0 !important;
        padding: 0 !important; margin: 0 !important;
        margin-right: -1px !important; margin-bottom: -1px !important;
        box-sizing: border-box !important;
        display: flex; align-items: center; justify-content: center;
    }

    /* A. 未揭开 (按钮) -> 亮白色 + 浮起感 */
    button[kind="secondary"] {
        background-color: #ffffff !important; 
        color: transparent !important;
        z-index: 10;
    }
    button[kind="secondary"]:hover {
        background-color: #f0f0f0 !important;
    }

    /* B. 已揭开 (坑) -> 深灰色 (#999) + 凹陷感 */
    /* 这个颜色比之前深很多，和白色的对比非常强烈 */
    .cell-revealed {
        background-color: #999999 !important; 
        color: white !important; /* 数字变成白色或亮色以便在深灰底阅读 */
        font-size: 24px;
        font-weight: bold;
        z-index: 1;
        box-shadow: inset 2px 2px 5px rgba(0,0,0,0.2); /* 内阴影增加凹陷感 */
    }
    
    /* 炸弹 */
    .cell-bomb {
        background-color: #000 !important; /* 炸弹是黑底 */
        color: red !important;
    }

    /* 数字颜色调整 (在深灰底上要亮一点) */
    .c1 { color: #cbf3f0 !important; text-shadow: 1px 1px 0 #000; } /* 亮青 */
    .c2 { color: #b5e48c !important; text-shadow: 1px 1px 0 #000; } /* 亮绿 */
    .c3 { color: #ff99c8 !important; text-shadow: 1px 1px 0 #000; } /* 亮粉 */
    .c4 { color: #a0c4ff !important; text-shadow: 1px 1px 0 #000; } /* 亮蓝 */
    
    /* 外框 */
    .board-wrap {
        display: inline-block;
        border-top: 3px solid #000;
        border-left: 3px solid #000;
        padding: 0; line-height: 0;
    }

    /* 功能按钮 */
    button[kind="primary"] {
        background: #2c3e50 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important; 
        font-size: 18px !important;
    }
    button[kind="primary"]:hover { background: #000 !important; }
    
</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

st.title("Minesweeper")

if not st.session_state.running:
    st.markdown("### ✏️ Setup")
    c1, c2, c3 = st.columns(3)
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
    
    if st.session_state.lost: st.markdown("<h2 style='color:#c0392b;text-align:center'>Game Over!</h2>", unsafe_allow_html=True)
    if st.session_state.won: st.markdown("<h2 style='color:#27ae60;text-align:center'>You Win!</h2>", unsafe_allow_html=True)

    # === 渲染网格 ===
    st.markdown("<div style='display:flex; justify-content:center;'>", unsafe_allow_html=True)
    st.markdown("<div class='board-wrap'>", unsafe_allow_html=True)
    
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
                
                # A. 已揭开 (深色凹陷)
                if is_rev or (end and board[r][c] == -1):
                    val = board[r][c]
                    if val == -1:
                        st.markdown("<div class='cell-revealed cell-bomb'>*</div>", unsafe_allow_html=True)
                    elif val == 0:
                        st.markdown("<div class='cell-revealed'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='cell-revealed c{val}'>{val}</div>", unsafe_allow_html=True)
                
                # B. 未揭开 (亮白浮起)
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
                        # 结束后的未揭开区域
                        st.markdown(f"<div class='cell-revealed' style='background:#fff !important; color:#ccc !important;'>{label}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
