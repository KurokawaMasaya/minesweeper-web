import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="Contrast Fixed", layout="centered", page_icon="📝")

# ================= 核心逻辑 (不变) =================
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

# ================= 🎨 高对比度修复版 CSS =================

st.markdown("""
<style>
    /* 1. 字体 */
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    .stApp {
        background-color: #fdfcf0;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    
    h1, p, label, span, div {
        color: #2c3e50 !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }

    /* 2. 输入框可见性修复 (白底黑字) */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div {
        background-color: #ffffff !important;
        border: 2px solid #2c3e50 !important;
        color: #2c3e50 !important;
        border-radius: 0px !important;
    }
    div[data-baseweb="select"] span, 
    div[data-testid="stNumberInput"] input {
        color: #2c3e50 !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }
    ul[data-baseweb="menu"] { background-color: #fff !important; border: 2px solid #2c3e50 !important; }

    /* 3. 布局修复 (消除缝隙) */
    div[data-testid="stHorizontalBlock"] { gap: 0 !important; }
    div[data-testid="column"] {
        width: 40px !important; min-width: 40px !important; flex: 0 0 40px !important;
        padding: 0 !important; margin: 0 !important;
    }

    /* ============================================================
       ✨ 核心修复：高对比度区分 (High Contrast)
       ============================================================ */

    /* 通用格子设置 (负边距重叠) */
    button[kind="secondary"], .cell-revealed {
        width: 40px !important;
        height: 40px !important;
        border: 1px solid #2c3e50 !important;
        border-radius: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        margin-right: -1px !important;
        margin-bottom: -1px !important;
        box-sizing: border-box !important;
        display: flex; align-items: center; justify-content: center;
    }

    /* A. 未揭开 (按钮) -> 纯白高亮 (#ffffff) */
    /* 这样看起来像一张张白纸盖在上面 */
    button[kind="secondary"] {
        background-color: #ffffff !important; 
        color: transparent !important;
        z-index: 2; /* 浮在上面 */
    }
    button[kind="secondary"]:hover {
        background-color: #f0f0f0 !important; /* 悬停微灰 */
    }

    /* B. 已揭开 (背景) -> 明显的灰色 (#dcdcdc) */
    /* 这样看起来像纸被揭开了，露出了底色，形成凹陷感 */
    .cell-revealed {
        background-color: #dcdcdc !important; 
        color: #2c3e50;
        font-size: 24px;
        font-weight: bold;
        cursor: default;
        z-index: 1; /* 沉在下面 */
    }
    
    /* 炸弹背景加深 */
    .cell-bomb-hit {
        background-color: #e74c3c !important; /* 红色 */
        color: white !important;
    }

    /* ============================================================ */

    .board-wrap {
        display: inline-block;
        border-top: 2px solid #2c3e50;
        border-left: 2px solid #2c3e50;
        padding: 0; line-height: 0;
    }

    button[kind="primary"] {
        background: transparent !important;
        color: #2c3e50 !important;
        border: 3px solid #2c3e50 !important;
        border-radius: 255px 15px 225px 15px / 15px 225px 15px 255px !important;
        font-size: 18px !important;
    }
    button[kind="primary"]:hover { background: #2c3e50 !important; color: #fff !important; }

    .c1 { color: #2980b9; } .c2 { color: #27ae60; } .c3 { color: #c0392b; } .c4{color:#8e44ad;}
    .bomb { color: #000; font-size: 28px; }
    
</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

st.title("Minesweeper")

if not st.session_state.running:
    st.markdown("### ✏️ Game Setup")
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
                
                # A. 显示内容 (已揭开)
                if is_rev or (end and board[r][c] == -1):
                    val = board[r][c]
                    if val == -1:
                        # 踩到的雷红色高亮，没踩到的只是显示
                        bg_cls = "cell-bomb-hit" if (is_rev and val == -1) else ""
                        st.markdown(f"<div class='cell-revealed {bg_cls} bomb'>*</div>", unsafe_allow_html=True)
                    elif val == 0:
                        st.markdown("<div class='cell-revealed'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='cell-revealed c{val}'>{val}</div>", unsafe_allow_html=True)
                
                # B. 按钮 (未揭开)
                else:
                    label = "P" if is_flg else " "
                    if not end:
                        # 按钮背景强制为白色，对比灰色已揭开区域
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
                        # 游戏结束后，未揭开的显示为淡白色
                        st.markdown(f"<div class='cell-revealed' style='background:#fff; color:#ccc'>{label}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
