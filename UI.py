import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="Fixed Minesweeper", layout="centered", page_icon="🖍️")


# ================= 核心逻辑 =================
def neighbors(r, c, R, C):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if 0 <= rr < R and 0 <= cc < C:
                yield rr, cc


def init_board(R, C):
    return [[0] * C for _ in range(R)]


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
        if (x, y) in vis:
            continue
        vis.add((x, y))
        if board[x][y] == 0:
            for nx, ny in neighbors(x, y, len(board), len(board[0])):
                if (nx, ny) not in vis:
                    stack.append((nx, ny))


def reveal(board, vis, flg, r, c):
    if (r, c) in flg:
        return True
    if board[r][c] == -1:
        return False
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


if "running" not in st.session_state:
    st.session_state.running = False
if "flag" not in st.session_state:
    st.session_state.flag = False
if "lost" not in st.session_state:
    st.session_state.lost = False
if "won" not in st.session_state:
    st.session_state.won = False

# ================= 🎨 CSS (布局修复 + 防抖 + 可见性) =================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    /* 1. 颜色变量定义 (自适应) */
    :root {
        /* ☀️ 浅色模式 */
        --bg-color: #fdfcf0;
        --text-color: #2c3e50;
        --box-bg: #ffffff;
        --box-border: #2c3e50;
        --revealed-bg: #dfe6e9;
        --accent-bg: #2c3e50;
        --accent-text: #ffffff;
        --bomb-color: #d63031;
        --hover-bg: #f0f0f0;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            /* 🌙 深色模式修正：背景纯黑，格子深灰，文字白 */
            --bg-color: #1a1a1a;
            --text-color: #ecf0f1;
            --box-bg: #2d3436;
            --box-border: #ecf0f1;
            --revealed-bg: #4a4a4a; /* 调亮一点，防止和纯黑背景混淆 */
            --accent-bg: #ecf0f1;
            --accent-text: #2c3e50;
            --bomb-color: #ff7675;
            --hover-bg: #3d3d3d;
        }
    }

    /* 全局应用 */
    .stApp {
        background-color: var(--bg-color) !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
        color: var(--text-color) !important;
    }

    h1, h2, h3, p, label, span, div {
        color: var(--text-color) !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }

    /* 标题居中且有一点手写感 */
    h1 {
        text-align: center;
        font-size: 3.2rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.2rem !important;
    }

    /* 设定顶部描述文字 */
    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 0.8rem;
        opacity: 0.8;
    }

    /* 设置 number_input 等控件更圆润 */
    .stNumberInput input, .stSelectbox div, .stButton button {
        border-radius: 8px !important;
    }

    /* 首页上方的 Setup 卡片 */
    .setup-card {
        border-radius: 16px;
        padding: 1rem 1.2rem;
        background: rgba(255,255,255,0.7);
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }

    /* 顶部控制栏卡片 */
    .top-bar {
        border-radius: 12px;
        padding: 0.6rem 0.8rem;
        background: rgba(255,255,255,0.8);
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 3px 10px rgba(0,0,0,0.06);
    }

    /* 状态文字 */
    .status-text {
        font-size: 1.2rem;
        text-align: center;
        margin-top: 0.3rem;
    }

    /* Selectbox 样式略微调整 */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(255,255,255,0.9) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(0,0,0,0.15) !important;
    }

    /* 下拉菜单项目 */
    li[data-baseweb="option"] {
        font-family: 'Patrick Hand', cursive, sans-serif !important;
        color: var(--text-color) !important;
    }
    li[data-baseweb="option"]:hover, li[data-baseweb="option"][aria-selected="true"] {
        background-color: var(--hover-bg) !important;
        color: var(--text-color) !important;
    }

    /* ============================================
       🚨 布局核心修复 🚨
       ============================================ */

    /* 1. 让列内容居中，但不强制锁死列宽，防止顶部按钮被挤扁 */
    div[data-testid="column"] {
        display: flex !important;
        justify-content: center !important; /* 让格子在列里居中 */
        align-items: center !important;
        min-width: 0 !important;
    }

    /* 2. 棋盘行间距 */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.3rem !important; /* 稍微紧凑一点 */
        justify-content: center !important;
    }

    /* 3. ⚡️ 棋盘格子 (Secondary Button) 物理锁定 ⚡️ */
    button[kind="secondary"] {
        width: 40px !important;
        height: 40px !important;
        min-height: 40px !important;
        max-height: 40px !important;

        border: 2px solid var(--box-border) !important;
        border-radius: 4px !important;
        background-color: var(--box-bg) !important;

        padding: 0 !important;
        margin: 0 !important;

        /* 防止变色 */
        color: transparent !important;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.2) !important;
        transition: none !important;
    }
    button[kind="secondary"]:hover {
        background-color: var(--hover-bg) !important;
        border-color: var(--box-border) !important;
    }
    button[kind="secondary"]:active {
        box-shadow: none !important;
        transform: translate(1px, 1px);
    }

    /* 4. ⚡️ 已揭开方块 (Div) 物理锁定 ⚡️ */
    /* 必须和上面的 button 尺寸属性 100% 一致 */
    .cell-revealed {
        width: 40px !important;
        height: 40px !important;
        min-height: 40px !important; /* 关键防抖 */

        border: 2px solid var(--box-border) !important;
        border-radius: 4px !important;
        box-sizing: border-box !important;

        background-color: var(--revealed-bg) !important;
        color: var(--text-color) !important;

        font-family: 'Patrick Hand', cursive, sans-serif !important;
        font-size: 20px !important;
        font-weight: bold !important;
        line-height: 1 !important;

        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: default;
        margin: 0 !important;
    }

    /* 5. 顶部大按钮 (Primary Button) 恢复正常 */
    button[kind="primary"] {
        width: auto !important;
        min-width: 0 !important;
        max-width: none !important;

        height: auto !important;
        min-height: 32px !important;
        max-height: none !important;

        padding: 0.35rem 0.8rem !important;
        margin: 0.1rem !important;

        font-size: 16px !important;
        border-radius: 999px !important;
        border: 1px solid var(--accent-bg) !important;

        background: var(--accent-bg) !important;
        color: var(--accent-text) !important;
        box-shadow: 0 3px 8px rgba(0,0,0,0.15) !important;
    }
    button[kind="primary"]:hover {
        background-color: var(--accent-text) !important;
        color: var(--accent-bg) !important;
        border-color: var(--accent-bg) !important;
    }

    /* 6. 不同数字颜色区分 */
    .c1 { color: #2980b9 !important; }
    .c2 { color: #27ae60 !important; }
    .c3 { color: #e74c3c !important; }
    .c4 { color: #9b59b6 !important; }
    .c5 { color: #f39c12 !important; }
    .c6 { color: #16a085 !important; }
    .c7 { color: #2c3e50 !important; }
    .c8 { color: #7f8c8d !important; }

    .cell-bomb {
        color: var(--bomb-color) !important;
        font-weight: 900 !important;
    }

</style>
""", unsafe_allow_html=True)

# === 自适应尺寸覆盖：根据列数自动缩放格子大小 ===
st.markdown(f"""
<style>
:root {{
    --cols: {st.session_state.get('cols', 10)};
}}
button[kind="secondary"] {{
    width: min(42px, calc(90vw / var(--cols))) !important;
    height: min(42px, calc(90vw / var(--cols))) !important;
    min-height: min(42px, calc(90vw / var(--cols))) !important;
    max-height: min(42px, calc(90vw / var(--cols))) !important;
}}
.cell-revealed {{
    width: min(42px, calc(90vw / var(--cols))) !important;
    height: min(42px, calc(90vw / var(--cols))) !important;
    min-height: min(42px, calc(90vw / var(--cols))) !important;
}}
</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

st.title("Minesweeper")

if not st.session_state.running:
    st.markdown("### ✏️ Setup")

    c1, sp1, c2, sp2, c3 = st.columns([1, 0.5, 1, 0.5, 2])

    with c1:
        R = st.number_input("Rows", 5, 20, 10)
    with sp1:
        st.empty()
    with c2:
        C = st.number_input("Cols", 5, 20, 10)
    with sp2:
        st.empty()
    with c3:
        diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        ratio = {"Easy": 0.12, "Medium": 0.18, "Hard": 0.25}[diff]
        M = int(R * C * ratio)
        st.markdown(f"<div class='status-text'>Mines: {M}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    center = st.columns([1, 1, 1])
    with center[1]:
        if st.button("Start Game", type="primary", use_container_width=True):
            start(R, C, M)
            st.rerun()

else:
    # 顶部栏：Home | Mode | Status | Restart
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
        st.markdown(
            f"<div style='text-align:center; font-size:22px; font-weight:bold; padding-top:8px;'>{left} 💣 Left</div>",
            unsafe_allow_html=True
        )
    with c4:
        if st.button("🔄", type="primary", use_container_width=True, help="Restart"):
            cfg = st.session_state.game_config
            start(cfg['R'], cfg['C'], cfg['M'])
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.lost:
        st.markdown("<h2 style='text-align:center; color:var(--bomb-color);'>Oops! Boom!</h2>",
                    unsafe_allow_html=True)
    if st.session_state.won:
        st.markdown("<h2 style='text-align:center; color:#2ecc71;'>You Win!</h2>",
                    unsafe_allow_html=True)

    st.markdown("<div style='display:flex; justify-content:center; flex-direction:column; align-items:center;'>",
                unsafe_allow_html=True)

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
                                if is_flg:
                                    flg.remove((r, c))
                                else:
                                    flg.add((r, c))
                                st.rerun()
                            elif not is_flg:
                                if not reveal(board, vis, flg, r, c):
                                    st.session_state.lost = True
                                st.rerun()
                    else:
                        # 游戏结束后，未揭开的格子保持背景色
                        st.markdown(
                            f"<div class='cell-revealed' style='background-color:var(--box-bg) !important; opacity:0.6;'>{label}</div>",
                            unsafe_allow_html=True
                        )

    st.markdown("</div>", unsafe_allow_html=True)
