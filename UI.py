import streamlit as st
import random
import time

# 页面配置
st.set_page_config(page_title="Paper Minesweeper Ultimate", layout="centered", page_icon="🖍️")

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

def start_game(R, C, M):
    b = init_board(R, C)
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
    # 保存当前设置以便快速重开
    st.session_state.current_settings = {"R": R, "C": C, "M": M}

# 初始化 State
if "running" not in st.session_state: st.session_state.running = False
if "flag" not in st.session_state: st.session_state.flag = False
if "animating" not in st.session_state: st.session_state.animating = False

# ================= 🎨 CSS (含动画 + 修复样式) =================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    /* 全局样式 */
    .stApp {
        background-color: #fdfcf0;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    h1, h2, h3, p, span, div, button {
        color: #2c3e50 !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    h1 { text-align: center; color: #000 !important; }

    /* ================= 动画关键帧 ================= */
    
    /* 1. 揉纸团 (离开) */
    @keyframes crumpleOut {
        0% { transform: scale(1) rotate(0deg); opacity: 1; }
        20% { transform: scale(0.9) rotate(-5deg); }
        50% { transform: scale(0.6) rotate(10deg) skew(20deg); opacity: 0.8; }
        100% { transform: scale(0) rotate(720deg); opacity: 0; }
    }

    /* 2. 铺纸 (进入) */
    @keyframes paperIn {
        0% { transform: translateY(50px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }

    /* 动画 Class */
    .anim-crumple {
        animation: crumpleOut 0.5s ease-in forwards;
        transform-origin: center center;
    }
    .anim-enter {
        animation: paperIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }

    /* ================= 控件样式修复 ================= */

    /* 输入框：白底黑字 + 隐藏 +/- */
    div[data-testid="stNumberInput"] input {
        background-color: #fff !important;
        color: #000 !important;
        -webkit-text-fill-color: #000 !important;
        font-weight: bold;
        text-align: center;
        border: 2px solid #2c3e50 !important;
        border-radius: 4px;
    }
    div[data-testid="stNumberInput"] button { display: none !important; } /* 隐藏加减号 */
    div[data-testid="stNumberInput"] > div { border: none !important; } /* 去掉外层默认边框 */

    /* 下拉菜单 */
    div[data-baseweb="select"] > div {
        background-color: #fff !important;
        border: 2px solid #2c3e50 !important;
        color: #000 !important;
    }
    div[data-baseweb="select"] span { color: #000 !important; -webkit-text-fill-color: #000 !important; }
    div[data-baseweb="select"] svg { fill: #000 !important; }
    
    ul[data-baseweb="menu"] { background-color: #fff !important; border: 2px solid #2c3e50 !important; }
    li[data-baseweb="option"] { color: #000 !important; }

    /* ================= 棋盘样式 ================= */
    
    div[data-testid="stHorizontalBlock"] { gap: 0.5rem !important; justify-content: center !important; }
    div[data-testid="column"] { width: 44px !important; flex: 0 0 44px !important; min-width: 44px !important; padding: 2px !important; }

    .tile-box {
        width: 40px !important; height: 40px !important;
        border: 2px solid #2c3e50 !important; border-radius: 4px !important;
        display: flex; align-items: center; justify-content: center;
        box-sizing: border-box !important;
    }

    /* 未揭开 */
    button[kind="secondary"] {
        @extend .tile-box;
        background-color: #ffffff !important; color: transparent !important;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.15) !important;
    }
    button[kind="secondary"]:hover { transform: translate(-1px, -1px); background-color: #f9f9f9 !important; }

    /* 已揭开 */
    .cell-revealed {
        width: 40px !important; height: 40px !important;
        border: 2px solid #2c3e50 !important; border-radius: 4px !important;
        background-color: #dfe6e9 !important; color: #2c3e50 !important;
        font-size: 20px; font-weight: bold; cursor: default;
        display: flex; align-items: center; justify-content: center;
    }

    .cell-bomb { color: #d63031 !important; font-size: 28px !important; }
    
    /* 按钮 */
    button[kind="primary"] { background-color: #2c3e50 !important; border: 2px solid #000 !important; width: 100%; }
    button[kind="primary"] p { color: #fff !important; font-size: 18px !important; }
    button[kind="primary"]:hover { background-color: #000 !important; }
    
    /* Home 按钮特殊样式 (次要按钮) */
    button[kind="secondaryform"] { 
        background-color: #fff !important; 
        border: 2px solid #2c3e50 !important; 
        color: #2c3e50 !important;
    }

    .c1 { color: #0984e3 !important; } .c2 { color: #00b894 !important; }
    .c3 { color: #d63031 !important; } .c4 { color: #6c5ce7 !important; }
    
    /* 动画容器 */
    .anim-wrap { display: inline-block; }

</style>
""", unsafe_allow_html=True)

# ================= 辅助渲染函数 =================

def render_board(board, vis, flg, rows, cols, anim_class=""):
    """渲染棋盘的函数，支持传入动画Class"""
    st.markdown(f"<div class='anim-wrap {anim_class}' style='display:flex; justify-content:center; flex-direction:column; align-items:center;'>", unsafe_allow_html=True)
    
    for r in range(rows):
        cols_ui = st.columns(cols)
        for c in range(cols):
            with cols_ui[c]:
                key = f"{r}_{c}"
                is_rev = (r,c) in vis
                is_flg = (r,c) in flg
                end = st.session_state.lost or st.session_state.won
                
                # 如果正在动画中，全部显示为静态样式，防止按钮闪烁
                if st.session_state.animating:
                    if is_rev:
                         # 简单渲染已揭开
                         st.markdown("<div class='cell-revealed' style='opacity:0.7'></div>", unsafe_allow_html=True)
                    else:
                         # 简单渲染未揭开
                         st.markdown("<div class='cell-revealed' style='background:#fff; border:2px solid #2c3e50;'></div>", unsafe_allow_html=True)
                    continue

                # 正常游戏逻辑
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

# ================= 主程序逻辑 =================

st.title("Minesweeper")

# --- 场景 1: 动画播放中 (显示旧棋盘 -> 揉成团) ---
if st.session_state.animating:
    # 1. 渲染旧的棋盘，加上揉纸动画 Class
    render_board(st.session_state.board, st.session_state.revealed, st.session_state.flags, 
                 st.session_state.rows, st.session_state.cols, 
                 anim_class="anim-crumple")
    
    # 2. 强制暂停 0.5s 等待动画播完
    time.sleep(0.5)
    
    # 3. 动画结束，重置数据，开始新游戏
    cfg = st.session_state.current_settings
    start_game(cfg["R"], cfg["C"], cfg["M"])
    st.session_state.animating = False
    st.rerun()

# --- 场景 2: 游戏设置 ---
elif not st.session_state.running:
    st.markdown("### ✏️ Setup")
    c1, sp1, c2, sp2, c3 = st.columns([1, 0.5, 1, 0.5, 2])
    
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
        start_game(R, C, M)
        st.rerun()

# --- 场景 3: 游戏进行中 (正常显示) ---
else:
    # 顶部控制栏 (Home | 状态 | Restart)
    c_home, c_mid, c_restart = st.columns([1.2, 2, 1.2])
    
    with c_home:
        # Home 按钮：回到设置页
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.running = False
            st.rerun()

    with c_mid:
        left = st.session_state.mines - len(st.session_state.flags)
        mode_txt = "Flagging" if st.session_state.flag else "Digging"
        icon = "🚩" if st.session_state.flag else "⛏️"
        
        # 居中显示状态
        st.markdown(
            f"<div style='text-align:center; font-size:20px; border-bottom:2px dashed #ccc; padding-bottom:5px;'>"
            f"<b>{left}</b> Mines | Mode: <b>{mode_txt}</b>"
            f"</div>", 
            unsafe_allow_html=True
        )
        
        # 模式切换小按钮
        if st.button(f"Switch to {icon}", use_container_width=True):
            st.session_state.flag = not st.session_state.flag
            st.rerun()

    with c_restart:
        # Restart 按钮：触发动画 -> 快速重开
        if st.button("🔄 Restart", type="primary", use_container_width=True):
            st.session_state.animating = True # 开启揉纸状态
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.lost: st.markdown("<h2 style='color:#d63031;text-align:center'>Oops! Boom!</h2>", unsafe_allow_html=True)
    if st.session_state.won: st.markdown("<h2 style='color:#00b894;text-align:center'>You Win!</h2>", unsafe_allow_html=True)

    # 渲染正常棋盘 (带有进入动画 anim-enter)
    render_board(st.session_state.board, st.session_state.revealed, st.session_state.flags, 
                 st.session_state.rows, st.session_state.cols, 
                 anim_class="anim-enter")
