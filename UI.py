import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="Crayon Minesweeper", layout="centered", page_icon="🖍️")

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

# ================= 🎨 CSS 样式 =================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    .stApp {
        background-color: #fdfcf0;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    
    /* 全局文字颜色 */
    h1, h2, h3, p, span, div, label, button {
        color: #2c3e50 !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }

    /* 输入框样式：白底黑字 */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #fff !important;
        border: 2px solid #2c3e50 !important;
        color: #000 !important;
        border-radius: 4px !important;
    }
    div[data-testid="stNumberInput"] input { color: #000 !important; font-weight:bold;}

    /* === 棋盘核心 CSS ===
       为了保证棋盘无缝，我们必须全局禁用 Gap。
       但是为了让设置栏分开，我们在Python代码里用了空白列 (Spacer) 
    */
    div[data-testid="stHorizontalBlock"] { gap: 0 !important; }
    
    /* 棋盘列宽固定 */
    div[data-testid="column"] {
        min-width: 0 !important; /* 允许变得很窄(用于spacer) */
        padding: 0 !important; margin: 0 !important;
    }

    /* 统一盒子模型 */
    .unified-box {
        width: 40px !important; height: 40px !important;
        box-sizing: border-box !important;
        border: 1px solid #2c3e50 !important;
        margin-right: -1px !important; margin-bottom: -1px !important;
        display: flex; align-items: center; justify-content: center;
        line-height: 1 !important;
    }

    /* 1. 按钮 (未揭开) - 纯白悬浮 */
    button[kind="secondary"] {
        width: 40px !important; height: 40px !important;
        border: 1px solid #2c3e50 !important;
        border-radius: 0 !important; padding: 0 !important;
        margin: 0 !important; margin-right: -1px !important; margin-bottom: -1px !important;
        background-color: #ffffff !important;
        color: transparent !important;
        z-index: 10;
    }
    button[kind="secondary"]:hover { background-color: #f0f0f0 !important; }

    /* 2. 已揭开 (深灰凹陷) */
    .cell-revealed {
        width: 40px !important; height: 40px !important;
        border: 1px solid #2c3e50 !important;
        box-sizing: border-box !important;
        margin-right: -1px !important; margin-bottom: -1px !important;
        
        background-color: #b2bec3 !important; /* 稍浅一点的灰，看得更清 */
        color: #fff !important; 
        font-size: 22px; font-weight: bold;
        cursor: default; z-index: 1;
        
        display: flex; align-items: center; justify-content: center;
    }

    /* 3. 炸弹样式 (Crayon Style X) */
    .cell-bomb {
        background-color: #b2bec3 !important; /* 背景保持灰色 */
        color: #d63031 !important; /* 蜡笔红 */
        font-size: 32px !important; /* 大一点 */
        font-family: 'Patrick Hand', cursive !important;
        line-height: 36px !important;
    }

    /* 开始按钮 */
    button[kind="primary"] {
        background-color: #2c3e50 !important;
        border: 2px solid #000 !important;
        border-radius: 8px !important;
    }
    button[kind="primary"] p { color: #fff !important; font-size: 20px !important; }
    button[kind="primary"]:hover { background-color: #000 !important; }
    
    /* 数字颜色 */
    .c1 { color: #00cec9 !important; text-shadow: 1px 1px 0 #555; }
    .c2 { color: #a29bfe !important; text-shadow: 1px 1px 0 #555; }
    .c3 { color: #ffeaa7 !important; text-shadow: 1px 1px 0 #555; }
    
    .board-wrap {
        display: inline-block;
        border-top: 2px solid #2c3e50; border-left: 2px solid #2c3e50;
        line-height: 0;
    }
</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

st.title("Minesweeper")

if not st.session_state.running:
    st.markdown("### ✏️ Setup")
    
    # 【关键修改】使用 5 列布局，中间插入 0.2 比例的空列来强制隔开
    c1, sp1, c2, sp2, c3 = st.columns([1, 0.2, 1, 0.2, 1.5])
    
    with c1: R = st.number_input("Rows", 5, 20, 10)
    with sp1: st.empty() # 空占位
    with c2: C = st.number_input("Cols", 5, 20, 10)
    with sp2: st.empty() # 空占位
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
    # 状态栏同样加上 spacer 保持美观
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
                        # 炸弹改用红色 X
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
    st.markdown("</div>", unsafe_allow_html=True)
