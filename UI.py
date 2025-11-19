import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="Final Grid Fix", layout="centered", page_icon="📐")

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

# ================= 🎨 强制统一 CSS =================

st.markdown("""
<style>
    /* 1. 字体引入 */
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    /* 2. 全局颜色重置：防止白字 */
    .stApp {
        background-color: #fdfcf0;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    
    /* 暴力覆盖所有文字颜色为深色 */
    h1, h2, h3, p, span, div, label, button {
        color: #2c3e50 !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    
    /* 标题特殊处理 */
    h1 {
        color: #000 !important;
        font-weight: 900 !important;
        font-size: 3rem !important;
        text-align: center;
        margin-bottom: 20px;
    }

    /* ============================================================
       修复: 开始按钮 (Start Game)
       ============================================================ */
    button[kind="primary"] {
        background-color: #2c3e50 !important; /* 深蓝底 */
        border: 2px solid #000 !important;
        border-radius: 8px !important;
        min-height: 50px !important;
    }
    /* 强制按钮内部文字颜色为白 */
    button[kind="primary"] p {
        color: #ffffff !important; 
        font-size: 24px !important;
        font-weight: bold !important;
    }
    button[kind="primary"]:hover {
        background-color: #000 !important;
    }
    
    /* 输入框样式 */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #fff !important;
        border: 2px solid #2c3e50 !important;
        color: #000 !important;
    }
    div[data-testid="stNumberInput"] input { color: #000 !important; }


    /* ============================================================
       核心修复: 统一网格 (The Perfect Grid)
       ============================================================ */

    /* 1. 布局归零 */
    div[data-testid="stHorizontalBlock"] { gap: 0 !important; }
    div[data-testid="column"] {
        width: 40px !important; min-width: 40px !important; flex: 0 0 40px !important;
        padding: 0 !important; margin: 0 !important;
    }

    /* 2. 定义统一的“盒子”标准 */
    /* 不管是 button 还是 div，都必须遵守这个规则 */
    .unified-box {
        width: 40px !important;
        height: 40px !important;
        box-sizing: border-box !important; /* 关键：边框算在宽度内 */
        border: 1px solid #000 !important; /* 统一 1px 黑边 */
        border-radius: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        
        /* 负边距：消除双重边框 */
        margin-right: -1px !important;
        margin-bottom: -1px !important;
        
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1 !important;
    }

    /* 3. 应用到 Streamlit 按钮 (未揭开) */
    button[kind="secondary"] {
        /* 继承 unified-box 的属性需要手动再写一遍，因为无法直接给组件加 class */
        width: 40px !important;
        height: 40px !important;
        box-sizing: border-box !important;
        border: 1px solid #000 !important;
        border-radius: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        margin-right: -1px !important;
        margin-bottom: -1px !important;
        
        background-color: #ffffff !important; /* 纯白 */
        color: transparent !important;
        z-index: 10; /* 浮在上面 */
    }
    button[kind="secondary"]:hover {
        background-color: #e0e0e0 !important;
        z-index: 20;
    }
    
    /* 4. 应用到 Markdown Div (已揭开) */
    .cell-revealed {
        /* 完全复刻上面的属性 */
        width: 40px !important;
        height: 40px !important;
        box-sizing: border-box !important;
        border: 1px solid #000 !important;
        border-radius: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        margin-right: -1px !important;
        margin-bottom: -1px !important;
        
        background-color: #999 !important; /* 深灰 */
        color: #fff !important; /* 白字 */
        font-weight: bold;
        font-size: 20px;
        cursor: default;
        z-index: 1;
        
        /* Flex 居中 */
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* 炸弹特殊色 */
    .cell-bomb { background-color: #000 !important; color: red !important; }
    
    /* 5. 外框容器 (Border Wrapper) */
    .board-wrap {
        display: inline-block;
        border-top: 2px solid #000; /* 加粗外框 */
        border-left: 2px solid #000;
        line-height: 0;
    }

    /* 颜色微调 */
    .c1 { color: #cbf3f0 !important; text-shadow: 1px 1px 0 #000; }
    .c2 { color: #b5e48c !important; text-shadow: 1px 1px 0 #000; }
    .c3 { color: #ff99c8 !important; text-shadow: 1px 1px 0 #000; }
    
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
                
                # 1. 已揭开 (Markdown DIV)
                if is_rev or (end and board[r][c] == -1):
                    val = board[r][c]
                    if val == -1:
                        st.markdown("<div class='cell-revealed cell-bomb'>*</div>", unsafe_allow_html=True)
                    elif val == 0:
                        st.markdown("<div class='cell-revealed'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='cell-revealed c{val}'>{val}</div>", unsafe_allow_html=True)
                
                # 2. 未揭开 (Streamlit Button)
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
