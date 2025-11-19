import streamlit as st
import random

# 设置页面，必须在第一行
st.set_page_config(page_title="Minesweeper Pro", layout="centered", page_icon="💣")


# ================= 核心逻辑 (保持不变) =================

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
    st.session_state.last_message = None


# Session State Initialization
if "running" not in st.session_state: st.session_state.running = False
if "flag" not in st.session_state: st.session_state.flag = False
if "lost" not in st.session_state: st.session_state.lost = False
if "won" not in st.session_state: st.session_state.won = False
if "last_message" not in st.session_state: st.session_state.last_message = None

# ================= 🎨 重新设计的 UI 样式 (CSS) =================

st.markdown("""
<style>
    /* 全局背景：深色渐变 */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #2e3b55 0%, #1a1d29 50%, #0f111a 100%);
        font-family: 'Inter', sans-serif;
    }

    /* 标题样式 */
    h1 {
        color: #fff;
        text-align: center;
        text-shadow: 0 0 20px rgba(100, 149, 237, 0.5);
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 10px !important;
    }

    /* 游戏主容器：玻璃拟态 */
    .game-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 30px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
        text-align: center;
    }

    /* 状态栏 Pills */
    .status-bar {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-bottom: 25px;
        flex-wrap: wrap;
    }

    .stat-pill {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #e0e0e0;
        padding: 8px 16px;
        border-radius: 50px;
        font-size: 14px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
    }

    /* 🚩 插旗模式激活状态 */
    .flag-mode-active {
        background: rgba(255, 99, 71, 0.2) !important;
        border: 1px solid #ff6347 !important;
        color: #ff6347 !important;
        box-shadow: 0 0 15px rgba(255, 99, 71, 0.3) !important;
        transition: all 0.3s ease;
    }

    /* Streamlit 按钮深度定制 (为了消除间隙和做成方块) */
    div.stButton > button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        border-radius: 8px !important;
        border: none !important;
        background: linear-gradient(145deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)) !important;
        color: transparent !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    div.stButton > button:hover {
        background: rgba(255,255,255,0.2) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.4), 0 0 10px rgba(100,149,237,0.3) !important;
    }

    div.stButton > button:active {
        transform: scale(0.95) !important;
    }

    /* 已揭开的格子样式 */
    .revealed-cell {
        width: 100%;
        aspect-ratio: 1/1;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(0, 0, 0, 0.4);
        border-radius: 6px;
        font-weight: 900;
        font-size: 18px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.02);
    }

    /* 🚩 插旗的格子 (Overlay) */
    .flagged-overlay {
        pointer-events: none;
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        font-size: 20px;
        z-index: 10;
    }

    /* 数字颜色 */
    .num-1 { color: #5c9aff; text-shadow: 0 0 10px rgba(92,154,255,0.4); }
    .num-2 { color: #5cdb95; text-shadow: 0 0 10px rgba(92,219,149,0.4); }
    .num-3 { color: #ff6b6b; text-shadow: 0 0 10px rgba(255,107,107,0.4); }
    .num-4 { color: #a55eea; }
    .num-5 { color: #fab1a0; }
    .num-6 { color: #63cdda; }
    .num-7 { color: #dfe6e9; }
    .num-8 { color: #74b9ff; }
    .mine  { color: #ff0000; font-size: 22px; animation: shake 0.5s; }

    @keyframes shake {
        0% { transform: translate(1px, 1px) rotate(0deg); }
        10% { transform: translate(-1px, -2px) rotate(-1deg); }
        20% { transform: translate(-3px, 0px) rotate(1deg); }
        30% { transform: translate(3px, 2px) rotate(0deg); }
        100% { transform: translate(1px, -2px) rotate(-1deg); }
    }

    /* 调整 Grid 间隙，非常重要 */
    div[data-testid="column"] {
        padding: 2px !important;
    }

    /* 胜利/失败 弹窗样式 */
    .result-banner {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .win-banner { background: linear-gradient(90deg, #11998e, #38ef7d); color: #fff; }
    .loss-banner { background: linear-gradient(90deg, #cb2d3e, #ef473a); color: #fff; }

    @keyframes popIn { from { transform: scale(0.8); opacity:0; } to { transform: scale(1); opacity:1; } }

    /* 隐藏 checkbox 默认样式，只保留功能 */
    div[data-testid="stCheckbox"] { display: none; }

</style>
""", unsafe_allow_html=True)

# ================= UI 逻辑 =================

st.title("Minesweeper")

# 胜利/失败 提示逻辑
if st.session_state.last_message:
    msg = st.session_state.last_message
    css_class = "win-banner" if st.session_state.last_message_type == "success" else "loss-banner"
    st.markdown(f"""
    <div class="result-banner {css_class}">
        <h2 style='margin:0;color:white'>{msg}</h2>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.last_message = None

# 游戏未开始的设置界面
if not st.session_state.running:
    st.markdown("<div class='game-container'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        R = st.number_input("Rows", 5, 20, 10)
    with col2:
        C = st.number_input("Cols", 5, 12, 10)  # 限制列宽以防在手机上溢出
    with col3:
        diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        factor = {"Easy": 0.12, "Medium": 0.18, "Hard": 0.25}

    M = max(1, int(R * C * factor[diff]))

    st.write("")  # Spacer
    if st.button("🚀 START GAME", use_container_width=True):
        start(R, C, M)
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# 游戏进行中界面
else:
    board = st.session_state.board
    vis = st.session_state.revealed
    flg = st.session_state.flags
    R = st.session_state.rows
    C = st.session_state.cols
    M = st.session_state.mines

    # 状态栏逻辑
    safe = R * C - M
    opened = sum((r, c) in vis for r in range(R) for c in range(C) if board[r][c] != -1)

    # 判定胜利
    if opened == safe and not st.session_state.won:
        st.session_state.won = True
        st.session_state.last_message = "🎉 VICTORY! You cleared the field!"
        st.session_state.last_message_type = "success"
        st.session_state.running = False
        for r in range(R):
            for c in range(C):
                if board[r][c] == -1:
                    flg.add((r, c))  # 自动插旗
                else:
                    vis.add((r, c))
        st.rerun()

    # 插旗模式控制 (自定义按钮)
    flag_mode_css = "flag-mode-active" if st.session_state.flag else ""
    flag_icon = "🚩" if st.session_state.flag else "⚓️"
    flag_text = "FLAG MODE: ON" if st.session_state.flag else "Mode: Reveal"

    # 渲染状态栏
    st.markdown(f"""
    <div class="status-bar">
        <div class="stat-pill">💣 {M} Mines</div>
        <div class="stat-pill">📊 {int(opened / safe * 100) if safe > 0 else 0}% Done</div>
    </div>
    """, unsafe_allow_html=True)

    # 模式切换按钮
    col_mode_1, col_mode_2, col_mode_3 = st.columns([1, 2, 1])
    with col_mode_2:
        # 使用 Streamlit 原生按钮来切换状态，但用 CSS 美化它
        mode_btn = st.button(f"{flag_icon}  {flag_text}", key="mode_toggle", use_container_width=True)
        if mode_btn:
            st.session_state.flag = not st.session_state.flag
            st.rerun()

    if st.session_state.flag:
        st.markdown("""
        <style>div[data-testid="stButton"] button { border: 1px solid #ff6347 !important; color: #ff6347 !important; }</style>
        """, unsafe_allow_html=True)

    # 渲染游戏棋盘
    st.markdown("<div class='game-container' style='padding: 15px;'>", unsafe_allow_html=True)

    # 预先计算每个 Grid 里的内容
    for r in range(R):
        cols = st.columns(C)
        for c in range(C):
            with cols[c]:
                # 唯一 Key
                k = f"{r}_{c}"

                # 已经揭开 或 游戏结束
                if (r, c) in vis or (st.session_state.lost and board[r][c] == -1):
                    val = board[r][c]
                    if val == -1:
                        content = "💣"
                        cls = "mine"
                    elif val == 0:
                        content = ""
                        cls = ""
                    else:
                        content = str(val)
                        cls = f"num-{val}"

                    st.markdown(f"<div class='revealed-cell {cls}'>{content}</div>", unsafe_allow_html=True)

                # 未揭开，显示按钮
                else:
                    # 如果插旗了，显示旗帜 Overlay
                    if (r, c) in flg:
                        st.markdown("<div class='flagged-overlay'>🚩</div>", unsafe_allow_html=True)

                    # 按钮点击逻辑
                    if st.button(f"btn_{r}_{c}", key=k):
                        if st.session_state.flag:
                            if (r, c) in flg:
                                flg.remove((r, c))
                            else:
                                flg.add((r, c))
                            st.rerun()
                        elif (r, c) not in flg:
                            # 踩雷
                            if not reveal(board, vis, flg, r, c):
                                st.session_state.lost = True
                                st.session_state.last_message = "💥 BOOM! Game Over"
                                st.session_state.last_message_type = "error"
                                st.session_state.running = False
                            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # 重开按钮
    if st.button("🔄 Restart Game", type="primary", use_container_width=True):
        st.session_state.running = False
        st.rerun()
