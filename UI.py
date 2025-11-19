import streamlit as st
import random
import time

# 页面配置
st.set_page_config(page_title="Minesweeper Pro", layout="centered", page_icon="💣")

# ================= 核心算法 (完全不动) =================
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
    st.session_state.last_message=None

# ================= Session State =================
if "running" not in st.session_state: st.session_state.running=False
if "flag" not in st.session_state: st.session_state.flag=False
if "lost" not in st.session_state: st.session_state.lost=False
if "won" not in st.session_state: st.session_state.won=False
if "last_message" not in st.session_state: st.session_state.last_message=None
# 用于触发 Toast 的状态
if "toast_msg" not in st.session_state: st.session_state.toast_msg = None

# ================= 🎨 CSS 样式优化版 =================

st.markdown("""
<style>
    /* 全局背景 */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #2e3b55 0%, #1a1d29 50%, #0f111a 100%);
        font-family: 'Inter', sans-serif;
    }

    h1 { color: #fff; text-align: center; margin-bottom: 5px !important; }

    /* 游戏容器：限制最大宽度，防止在宽屏上太散 */
    .game-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin: 0 auto; 
        display: flex;
        flex-direction: column;
        align-items: center;
        width: fit-content; /* 关键：容器宽度适应内容 */
    }

    /* 强制所有按钮的大小为 40px x 40px，解决"按键太大"的问题 */
    div.stButton > button {
        width: 40px !important;
        height: 40px !important;
        border-radius: 6px !important;
        border: none !important;
        background: linear-gradient(145deg, #3a3f50, #2a2e3a) !important;
        box-shadow: 3px 3px 6px rgba(0,0,0,0.3), -1px -1px 2px rgba(255,255,255,0.05) !important;
        color: transparent !important;
        margin: 0 !important;
        padding: 0 !important;
        transition: all 0.1s !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-1px);
        background: #454b5e !important;
    }
    
    div.stButton > button:active {
        transform: translateY(1px);
        box-shadow: inset 2px 2px 5px rgba(0,0,0,0.4) !important;
    }
    
    /* 🚩 旗帜模式激活时的按钮边框 */
    .flag-active div.stButton > button {
        border: 1px solid #ff6b6b !important;
    }

    /* 已揭开的格子 */
    .revealed-cell {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #1a1d24;
        border-radius: 4px;
        font-weight: 900;
        font-size: 18px;
        border: 1px solid #2a2e3a;
        box-shadow: inset 1px 1px 4px rgba(0,0,0,0.6);
    }
    
    /* 消除 Streamlit 列之间的默认间距 */
    div[data-testid="column"] {
        width: 40px !important;
        flex: 0 0 40px !important;
        min-width: 40px !important;
        padding: 1px !important; 
    }
    
    /* 强制 Grid 居中 */
    div[data-testid="stHorizontalBlock"] {
        justify-content: center;
    }

    /* 顶部状态栏 */
    .status-bar {
        display: flex; justify-content: center; gap: 20px; margin-bottom: 15px;
    }
    .pill {
        background: rgba(0,0,0,0.3); padding: 5px 15px; border-radius: 20px;
        color: #ccc; font-size: 14px; border: 1px solid #333;
    }

    /* 数字颜色 */
    .num-1 { color: #4285F4; } .num-2 { color: #34A853; } .num-3 { color: #EA4335; }
    .num-4 { color: #A142F4; } .mine { font-size: 20px; }
    
    /* 旗帜 Overlay */
    .flag-overlay { pointer-events: none; position: absolute; top: 5px; left: 8px; font-size: 18px; z-index: 2; }

</style>
""", unsafe_allow_html=True)

# ================= 处理 Toast 逻辑 =================
# 必须放在 UI 渲染前处理，保证每次 rerun 都能弹
if st.session_state.toast_msg:
    st.toast(st.session_state.toast_msg, icon="ℹ️")
    st.session_state.toast_msg = None

# ================= 主界面逻辑 =================

st.title("Minesweeper")

# 游戏未开始（配置界面）
if not st.session_state.running:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        c1, c2, c3 = st.columns([1,2,1]) # 用列布局挤压中间，让设置不要太宽
        with c2:
            st.markdown("### ⚙️ Game Setup")
            R = st.slider("Rows", 5, 15, 10) # 限制最大行数防止溢出屏幕
            C = st.slider("Columns", 5, 15, 10)
            diff = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"])
            factor = {"Easy":0.12, "Medium":0.18, "Hard":0.25}
            M = max(1, int(R*C*factor[diff]))
            
            st.write("")
            # 开始按钮：使用 type="primary" 让它更显眼
            if st.button("🚀 START GAME", type="primary", use_container_width=True):
                start(R,C,M)
                st.session_state.toast_msg = "Game Started! Good Luck!"
                st.rerun()

# 游戏进行中
else:
    board = st.session_state.board
    vis   = st.session_state.revealed
    flg   = st.session_state.flags
    R     = st.session_state.rows
    C     = st.session_state.cols
    M     = st.session_state.mines

    # 计算剩余雷数
    mines_left = M - len(flg)
    
    # 判定胜利
    safe = R*C-M
    opened = sum((r,c) in vis for r in range(R) for c in range(C) if board[r][c]!=-1)
    
    if opened == safe and not st.session_state.won:
        st.session_state.won = True
        st.session_state.toast_msg = "🎉 VICTORY!" 
        # 胜利后自动插满旗
        for r in range(R):
             for c in range(C):
                 if board[r][c] == -1: flg.add((r,c))
                 else: vis.add((r,c))
        st.rerun()

    # === 顶部控制栏 ===
    # 使用 columns 布局让 Mode 按钮和 Restart 按钮分开
    c_left, c_mid, c_right = st.columns([1.5, 2, 1.5])
    
    with c_mid:
        # 状态展示
        st.markdown(f"""
        <div class="status-bar">
            <span class="pill">💣 {mines_left}</span>
            <span class="pill">⏱️ {'Running' if not st.session_state.lost and not st.session_state.won else 'Ended'}</span>
        </div>
        """, unsafe_allow_html=True)

    with c_left:
        # 旗帜模式切换按钮
        mode_label = "🚩 Flag Mode: ON" if st.session_state.flag else "⛏️ Reveal Mode"
        # 根据状态改变按钮样式 (虽然 Streamlit 按钮样式有限，但文案可变)
        if st.button(mode_label, use_container_width=True):
            st.session_state.flag = not st.session_state.flag
            state_text = "Enabled" if st.session_state.flag else "Disabled"
            st.session_state.toast_msg = f"Flag Mode {state_text}"
            st.rerun()
            
    with c_right:
        # 重开按钮
        if st.button("🔄 Restart", use_container_width=True):
            st.session_state.running = False
            st.session_state.toast_msg = "Game Reset"
            st.rerun()

    # === 游戏棋盘区 ===
    # 动态给容器添加 class，如果是插旗模式，添加 css 标记
    flag_class = "flag-active" if st.session_state.flag else ""
    
    st.markdown(f"<div class='game-container {flag_class}'>", unsafe_allow_html=True)
    
    # 结果提示 Banner
    if st.session_state.lost:
        st.error("💥 BOOM! You hit a mine! Press Restart to try again.")
    elif st.session_state.won:
        st.success("🎉 Congratulations! You cleared the field!")

    # 渲染 Grid
    # 使用 gap="0" (Streamlit 1.30+ 特性) 或者靠 CSS 挤压
    # 这里完全依赖 CSS 的 div[data-testid="column"] { width: 40px } 强制控制
    for r in range(R):
        cols = st.columns(C) 
        for c in range(C):
            with cols[c]:
                k = f"{r}_{c}"
                # 逻辑：已揭开 OR (游戏结束且是雷)
                is_revealed = (r,c) in vis
                is_mine = board[r][c] == -1
                show_mine = st.session_state.lost and is_mine
                
                if is_revealed or show_mine:
                    val = board[r][c]
                    if val == -1:
                        txt, cls = "💣", "mine"
                    elif val == 0:
                        txt, cls = "", ""
                    else:
                        txt, cls = str(val), f"num-{val}"
                    st.markdown(f"<div class='revealed-cell {cls}'>{txt}</div>", unsafe_allow_html=True)
                else:
                    # 旗帜 Overlay
                    if (r,c) in flg:
                        st.markdown("<div class='flag-overlay'>🚩</div>", unsafe_allow_html=True)
                    
                    # 只有游戏没结束时按钮才有效
                    if not st.session_state.lost and not st.session_state.won:
                        if st.button(f"b{r}{c}", key=k):
                            if st.session_state.flag:
                                if (r,c) in flg: flg.remove((r,c))
                                else: flg.add((r,c))
                                st.rerun()
                            elif (r,c) not in flg:
                                if not reveal(board, vis, flg, r, c):
                                    st.session_state.lost = True
                                    st.session_state.toast_msg = "💥 BOOM! Game Over"
                                st.rerun()
                    else:
                        # 游戏结束后显示不可点击的方块占位
                        st.markdown("<div style='width:40px;height:40px;background:#2a2e3a;border-radius:6px;'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
