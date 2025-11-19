import streamlit as st
import random
import time

# 页面配置
st.set_page_config(page_title="Minesweeper Final", layout="centered", page_icon="🖍️")

# ================= 核心逻辑 (保持不变) =================
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
    b = init_board(R,C)
    place(b,M)
    st.session_state.board = b
    st.session_state.revealed = set()
    st.session_state.flags = set()
    st.session_state.rows = R
    st.session_state.cols = C
    st.session_state.mines = M
    st.session_state.running = True
    st.session_state.lost = False
    st.session_state.won = False
    # 记住当前配置，用于快速 Restart
    st.session_state.config = {"R": R, "C": C, "M": M}

if "running" not in st.session_state: st.session_state.running = False
if "flag" not in st.session_state: st.session_state.flag = False
if "animating" not in st.session_state: st.session_state.animating = False

# ================= 🎨 CSS (完全回归白底黑字版 + 动画) =================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    /* 1. 全局重置 */
    .stApp {
        background-color: #fdfcf0;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    
    h1, h2, h3, p, label, span, div, button {
        color: #2c3e50 !important;
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    h1 { text-align: center; color: #000 !important; }

    /* 2. 输入框修复 (白底黑字 + 隐藏 +/-) */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    div[data-testid="stNumberInput"] > div {
        background-color: #ffffff !important;
        border: 2px solid #2c3e50 !important;
        color: #000000 !important;
        border-radius: 6px !important;
    }
    
    /* 文字强制纯黑 */
    input[type="number"], div[data-baseweb="select"] span {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
        font-weight: bold !important;
        font-size: 18px !important;
        text-align: center;
    }

    /* 隐藏 +/- 按钮 */
    div[data-testid="stNumberInput"] button { display: none !important; }

    /* 下拉菜单 */
    ul[data-baseweb="menu"] { background-color: #ffffff !important; border: 2px solid #2c3e50 !important; }
    li[data-baseweb="option"] { color: #000000 !important; background-color: #ffffff !important; }
    li[data-baseweb="option"]:hover { background-color: #e0e0e0 !important; }

    /* 3. 棋盘样式 */
    div[data-testid="stHorizontalBlock"] { gap: 0.5rem !important; justify-content: center !important; }
    div[data-testid="column"] { width: 44px !important; flex: 0 0 44px !important; min-width: 44px !important; padding: 2px !important; }

    .tile-box {
        width: 40px !important; height: 40px !important;
        border-radius: 4px !important; border: 2px solid #2c3e50 !important;
        display: flex; align-items: center; justify-content: center;
        box-sizing: border-box !important;
    }

    /* 未揭开 */
    button[kind="secondary"] {
        @extend .tile-box;
        width: 40px !important; height: 40px !important;
        background-color: #ffffff !important; color: transparent !important;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.15) !important;
        border: 2px solid #2c3e50 !important;
    }
    button[kind="secondary"]:hover { transform: translate(-1px, -1px); background-color: #f9f9f9 !important; }

    /* 已揭开 */
    .cell-revealed {
        width: 40px !important; height: 40px !important;
        border: 2px solid #2c3e50 !important; border-radius: 4px !important;
        box-sizing: border-box !important;
        background-color: #dfe6e9 !important; color: #2c3e50 !important;
        font-size: 20px; font-weight: bold; cursor: default;
        display: flex; align-items: center; justify-content: center;
        box-shadow: none !important;
    }

    .cell-bomb { color: #d63031 !important; font-size: 28px !important; line-height: 1; }
    
    /* 按钮 */
    button[kind="primary"] { background-color: #2c3e50 !important; border: 2px solid #000 !important; width: 100%; }
    button[kind="primary"] p { color: #fff !important; font-size: 20px !important; }
    button[kind="primary"]:hover { background-color: #000 !important; }
    
    /* Home 按钮特殊处理 (用 secondaryform 样式区分) */
    button[kind="secondaryform"] { background-color: #fff !important; border: 2px solid #2c3e50 !important; }
    button[kind="secondaryform"] p { color: #2c3e50 !important; }

    .c1 { color: #0984e3 !important; } .c2 { color: #00b894 !important; }
    .c3 { color: #d63031 !important; } .c4 { color: #6c5ce7 !important; }
    
    /* 4. 动画特效 */
    @keyframes crumpleOut {
        0% { transform: scale(1) rotate(0deg); opacity: 1; }
        30% { transform: scale(0.8) rotate(-5deg) skew(5deg); }
        100% { transform: scale(0) rotate(720deg); opacity: 0; }
    }
    @keyframes paperIn {
        0% { transform: translateY(30px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    .anim-crumple { animation: crumpleOut 0.6s ease-in forwards; transform-origin: center; }
    .anim-enter { animation: paperIn 0.5s ease-out forwards; }
    
    .board-container { display: inline-block; }

</style>
""", unsafe_allow_html=True)

# ================= 渲染函数 (用于动画复用) =================

def render_board_grid(board, vis, flg, rows, cols, css_class=""):
    """渲染棋盘的函数，支持传入动画 CSS Class"""
    st.markdown(f"<div class='board-container {css_class}' style='display:flex; justify-content:center; flex-direction:column; align-items:center;'>", unsafe_allow_html=True)
    
    for r in range(rows):
        cols_ui = st.columns(cols)
        for c in range(cols):
            with cols_ui[c]:
                key = f"{r}_{c}"
                is_rev = (r,c) in vis
                is_flg = (r,c) in flg
                end = st.session_state.lost or st.session_state.won
                
                # 如果正在播放揉纸动画，直接显示静态快照，避免按钮重新渲染闪烁
                if "crumple" in css_class:
                    if is_rev:
                         st.markdown("<div class='cell-revealed' style='opacity:0.8'></div>", unsafe_allow_html=True)
                    else:
                         st.markdown("<div class='cell-revealed' style='background:#fff'></div>", unsafe_allow_html=True)
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

# ================= 主流程 =================

st.title("Minesweeper")

# 1. 动画阶段：正在揉纸
if st.session_state.animating:
    # 渲染旧棋盘，加上动画 class
    render_board_grid(st.session_state.board, st.session_state.revealed, st.session_state.flags, 
                      st.session_state.rows, st.session_state.cols, "anim-crumple")
    time.sleep(0.6) # 等待动画
    
    # 动画结束，真正重置数据
    cfg = st.session_state.config
    start_game(cfg["R"], cfg["C"], cfg["M"])
    st.session_state.animating = False
    st.rerun()

# 2. 设置阶段
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

# 3. 游戏阶段
else:
    # 顶部控制栏：Home | 状态 | Restart
    c_home, c_mid, c_restart = st.columns([1, 2, 1])
    
    with c_home:
        # Home 键：返回设置
        if st.button("🏠 Home", type="secondary", use_container_width=True):
            st.session_state.running = False
            st.rerun()
            
    with c_mid:
        left = st.session_state.mines - len(st.session_state.flags)
        mode_icon = "🚩" if st.session_state.flag else "⛏️"
        
        # 状态显示
        st.markdown(
            f"<div style='text-align:center; font-size:22px; padding-top:5px;'>"
            f"<b>{left}</b> 💣 | Mode: {mode_icon}"
            f"</div>", unsafe_allow_html=True
        )
        
        # 模式切换 (隐形按钮覆盖在文字下，或者直接放在下面)
        if st.button("Switch Mode", key="mode_sw", use_container_width=True):
             st.session_state.flag = not st.session_state.flag
             st.rerun()

    with c_restart:
        # Restart 键：触发动画
        if st.button("🔄 Restart", type="primary", use_container_width=True):
            st.session_state.animating = True
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.lost: st.markdown("<h2 style='color:#d63031;text-align:center'>Oops! Boom!</h2>", unsafe_allow_html=True)
    if st.session_state.won: st.markdown("<h2 style='color:#00b894;text-align:center'>You Win!</h2>", unsafe_allow_html=True)

    # 渲染棋盘 (带入场动画)
    render_board_grid(st.session_state.board, st.session_state.revealed, st.session_state.flags, 
                      st.session_state.rows, st.session_state.cols, "anim-enter")
