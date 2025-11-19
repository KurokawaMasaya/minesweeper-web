import streamlit as st
import random

# 页面配置 (图标换个绿色的护眼一下)
st.set_page_config(page_title="Minesweeper Eye-Care", layout="centered", page_icon="🌿")

# ================= 核心逻辑 (完全不动) =================
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

# ================= 🎨 CSS (护眼调色版) =================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    /* 1. 护眼全局背景与文字 */
    .stApp {
        background-color: #F5F7F8; /* 这里的颜色很关键：柔和的云白色 */
        font-family: 'Patrick Hand', cursive, sans-serif !important;
        color: #333333 !important; /* 深灰字，比纯黑舒服 */
    }
    
    /* 标题和文本 */
    h1, h2, h3, p, label, span, div {
        color: #333333 !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    h1 { text-align: center; color: #2c3e50 !important; }

    /* ============================================================
       输入框 (柔和白底 + 深灰字)
       ============================================================ */
    
    /* 容器 */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    div[data-testid="stNumberInput"] > div {
        background-color: #FFFFFF !important;
        border: 2px solid #555555 !important; /* 边框变细灰 */
        color: #333333 !important;
        border-radius: 6px !important;
        box-shadow: none !important;
    }

    /* 内部文字 */
    input[type="number"], 
    div[data-baseweb="select"] span,
    div[data-testid="stNumberInput"] input {
        color: #333333 !important;
        -webkit-text-fill-color: #333333 !important;
        caret-color: #333333 !important;
        font-weight: bold !important;
        font-size: 18px !important;
        text-align: center;
    }

    /* 下拉箭头 */
    div[data-baseweb="select"] svg {
        fill: #555555 !important;
        color: #555555 !important;
    }

    /* 隐藏步进器 */
    div[data-testid="stNumberInput"] button { display: none !important; }

    /* 下拉菜单 */
    ul[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
        border: 2px solid #555555 !important;
    }
    li[data-baseweb="option"] {
        color: #333333 !important;
        background-color: #FFFFFF !important;
        font-weight: bold !important;
    }
    /* 悬停柔和灰 */
    li[data-baseweb="option"]:hover,
    li[data-baseweb="option"][aria-selected="true"] {
        background-color: #EAECEF !important;
        color: #333333 !important;
    }
    li[data-baseweb="option"] div { color: #333333 !important; }

    /* ============================================================
       棋盘 (防抖 + 护眼)
       ============================================================ */
    
    div[data-testid="stHorizontalBlock"] { gap: 0.4rem !important; justify-content: center !important; }
    div[data-testid="column"] { width: 40px !important; flex: 0 0 40px !important; min-width: 40px !important; padding: 0 !important; margin: 0 !important; }
    
    /* 锁死按钮容器 */
    div.stButton { width: 40px !important; height: 40px !important; min-height: 40px !important; margin: 0 !important; line-height: 1 !important; }

    /* 基础盒子 */
    .tile-base {
        width: 40px !important; height: 40px !important;
        border: 2px solid #555555 !important; /* 柔和边框 */
        border-radius: 5px !important;
        display: flex; align-items: center; justify-content: center;
        box-sizing: border-box !important;
    }

    /* 未揭开：柔和白 */
    button[kind="secondary"] {
        @extend .tile-base;
        background-color: #FFFFFF !important; 
        color: transparent !important;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.1) !important; /* 阴影变淡 */
        transition: none !important;
    }
    button[kind="secondary"]:hover {
        background-color: #F9FAFB !important;
        border-color: #333 !important;
    }
    button[kind="secondary"]:active {
        background-color: #EAECEF !important;
        box-shadow: none !important;
        transform: translate(1px, 1px);
    }

    /* 已揭开：柔和灰 */
    .cell-revealed {
        @extend .tile-base;
        background-color: #EAECEF !important; 
        color: #333333 !important;
        font-size: 20px; font-weight: 900; /* 加粗更好认 */
        cursor: default;
        box-shadow: none !important;
    }

    /* 炸弹颜色：稍微降低饱和度，不刺眼 */
    .cell-bomb { color: #c0392b !important; font-size: 26px !important; }
    
    /* 功能按钮：深蓝灰 */
    button[kind="primary"] {
        background-color: #34495e !important;
        border: 2px solid #2c3e50 !important;
        width: 100%; box-shadow: none !important;
    }
    button[kind="primary"] p { color: #fff !important; font-size: 18px !important; font-weight: bold !important; }
    button[kind="primary"]:hover { background-color: #2c3e50 !important; }

    /* 数字颜色：护眼色系 */
    .c1 { color: #2980b9 !important; } /* 稳重的蓝 */
    .c2 { color: #27ae60 !important; } /* 护眼绿 */
    .c3 { color: #c0392b !important; } /* 砖红 */
    .c4 { color: #8e44ad !important; } /* 紫色 */

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
    # 顶部栏
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
    
    if st.session_state.lost: st.markdown("<h2 style='color:#c0392b;text-align:center'>Oops! Boom!</h2>", unsafe_allow_html=True)
    if st.session_state.won: st.markdown("<h2 style='color:#27ae60;text-align:center'>You Win!</h2>", unsafe_allow_html=True)

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
                        st.markdown(f"<div class='cell-revealed' style='background-color:#fff !important; opacity:0.6;'>{label}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
