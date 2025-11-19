import streamlit as st
import random

# 页面配置 (宽屏模式)
st.set_page_config(page_title="Mobile Fixed", layout="wide", page_icon="🖍️")

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

# ================= 🎨 修复版 CSS =================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    /* 1. 全局样式 */
    .stApp {
        background-color: #fdfcf0;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
        color: #000000 !important;
    }
    h1, h2, h3, p, label, span, div, button {
        color: #000000 !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    h1 { text-align: center; }

    /* ============================================
       输入框 & 菜单 (白底黑字修复)
       ============================================ */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    div[data-testid="stNumberInput"] > div {
        background-color: #ffffff !important;
        border: 2px solid #2c3e50 !important;
        color: #000000 !important;
        border-radius: 6px !important;
    }
    input[type="number"], div[data-baseweb="select"] span, div[data-testid="stNumberInput"] input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: bold !important;
        text-align: center;
    }
    div[data-baseweb="select"] svg { fill: #000000 !important; }
    div[data-testid="stNumberInput"] button { display: none !important; }

    ul[data-baseweb="menu"] { background-color: #ffffff !important; border: 2px solid #2c3e50 !important; }
    li[data-baseweb="option"] { color: #000000 !important; background-color: #ffffff !important; }
    li[data-baseweb="option"]:hover { background-color: #e0e0e0 !important; }

    /* ============================================
       🚨 布局核心修复 (Layout Fix) 🚨
       ============================================ */

    /* 1. 全局行布局：禁止自动换行，允许横向滚动 */
    /* 这解决了手机上棋盘变成竖列的问题 */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        gap: 2px !important;
        padding-bottom: 5px;
        align-items: center !important;
    }
    
    /* 隐藏滚动条但保留功能 */
    div[data-testid="stHorizontalBlock"]::-webkit-scrollbar { display: none; }

    /* 2. 列宽：不做全局限制！让它自适应！ */
    /* 这解决了顶部菜单被挤扁的问题 */
    div[data-testid="column"] {
        width: auto !important;
        flex: 1 1 auto !important;
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* ============================================
       棋盘格子专用样式 (40px 锁定)
       ============================================ */

    /* A. 未揭开 (Secondary Button) */
    button[kind="secondary"] {
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important; /* 手机上保证不被压缩 */
        
        background-color: #ffffff !important;
        border: 2px solid #2c3e50 !important;
        border-radius: 4px !important;
        color: transparent !important;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.15) !important;
        padding: 0 !important;
        margin: 0 auto !important; /* 居中 */
    }
    button[kind="secondary"]:hover { background-color: #f9f9f9 !important; }
    button[kind="secondary"]:active { box-shadow: none !important; transform: translate(1px, 1px); }

    /* B. 已揭开 (Div) */
    .cell-revealed {
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        
        border: 2px solid #2c3e50 !important;
        border-radius: 4px !important;
        box-sizing: border-box !important;
        background-color: #dfe6e9 !important; 
        color: #2c3e50 !important;
        font-size: 20px; font-weight: bold;
        cursor: default;
        display: flex; align-items: center; justify-content: center;
        box-shadow: none !important;
        margin: 0 auto !important;
    }

    .cell-bomb { color: #d63031 !important; font-size: 28px !important; }

    /* ============================================
       顶部功能按钮 (Primary)
       ============================================ */
    button[kind="primary"] {
        background-color: #2c3e50 !important;
        border: 2px solid #000 !important;
        width: 100%;
        min-height: 45px !important; /* 保证高度适合手指点击 */
        border-radius: 8px !important;
    }
    button[kind="primary"] p { color: #fff !important; font-size: 18px !important; }
    button[kind="primary"]:hover { background-color: #000 !important; }

    .c1 { color: #0984e3 !important; } .c2 { color: #00b894 !important; }
    .c3 { color: #d63031 !important; } .c4 { color: #6c5ce7 !important; }

</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

st.title("Minesweeper")

if not st.session_state.running:
    st.markdown("### ✏️ Setup")
    
    # 设置栏：分行显示，保证手机不拥挤
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
    # 顶部菜单改版：两行布局，防止手机挤扁
    # Row 1: Home | Restart
    c1, c2 = st.columns([1, 1], gap="small")
    with c1:
        if st.button("🏠 Home", type="primary", use_container_width=True):
            st.session_state.running = False
            st.rerun()
    with c2:
        if st.button("🔄 Restart", type="primary", use_container_width=True):
            cfg = st.session_state.game_config
            start(cfg['R'], cfg['C'], cfg['M'])
            st.rerun()
            
    # Row 2: Mode | Status
    c3, c4 = st.columns([1, 1.5], gap="small")
    with c3:
        mode_txt = "Flag" if st.session_state.flag else "Dig"
        icon = "🚩" if st.session_state.flag else "⛏️"
        if st.button(f"{icon} {mode_txt}", type="primary", use_container_width=True):
            st.session_state.flag = not st.session_state.flag
            st.rerun()
    with c4:
        left = st.session_state.mines - len(st.session_state.flags)
        st.markdown(
            f"<div style='text-align:center; font-size:22px; font-weight:bold; padding-top:10px; color:#000;'>{left} 💣 Left</div>",
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.lost: st.markdown("<h2 style='color:#d63031;text-align:center'>Oops! Boom!</h2>", unsafe_allow_html=True)
    if st.session_state.won: st.markdown("<h2 style='color:#00b894;text-align:center'>You Win!</h2>", unsafe_allow_html=True)

    # 渲染棋盘容器
    st.markdown("<div style='display:flex; justify-content:center;'>", unsafe_allow_html=True)
    st.markdown("<div style='display:inline-block;'>", unsafe_allow_html=True) # 包裹以适应内容宽度
    
    board = st.session_state.board
    vis = st.session_state.revealed
    flg = st.session_state.flags
    
    for r in range(st.session_state.rows):
        # 允许水平滑动，不强制换行
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
                        st.markdown(f"<div class='cell-revealed' style='background-color:#fff !important; opacity:0.6;'>{label}</div>", unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
