import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="Minesweeper Custom", layout="centered", page_icon="💣")

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
    # 确保雷数不超过格子总数-1 (至少留一个空位)
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

# ================= 🎨 CSS 样式 (保持修复版布局) =================

st.markdown("""
<style>
    .stApp {
        background: #2b2d42;
        font-family: sans-serif;
    }
    h1 { color: white; text-align: center; margin-bottom: 20px; }

    /* --- 按钮样式分离 --- */
    
    /* 1. 雷区格子 (Secondary) -> 强制正方形小格 */
    button[kind="secondary"] {
        width: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        border-radius: 4px !important;
        border: 1px solid #4a4e69 !important;
        background-color: #8d99ae !important;
        color: transparent !important;
        transition: transform 0.1s;
    }
    button[kind="secondary"]:hover {
        background-color: #edf2f4 !important;
        transform: scale(1.05);
    }
    
    /* 2. 功能按钮 (Primary) -> 宽度自适应 */
    button[kind="primary"] {
        width: auto !important;
        height: auto !important;
        min-width: 120px;
        padding: 10px 24px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        background: #ef233c !important;
        color: white !important;
        border: none !important;
    }
    button[kind="primary"]:hover {
        background: #d90429 !important;
    }
    
    /* 3. 已揭开格子 */
    .cell-revealed {
        width: 40px; height: 40px;
        display: flex; align-items: center; justify-content: center;
        background: #edf2f4;
        border-radius: 4px;
        font-weight: 900;
        font-size: 20px;
        color: #2b2d42;
    }
    
    /* 4. 布局修正 */
    div[data-testid="column"] {
        width: 40px !important;
        flex: unset !important;
        padding: 2px !important;
    }
    div[data-testid="stHorizontalBlock"] {
        justify-content: center;
    }
    
    /* 数字颜色 */
    .n1{color:#3a86ff} .n2{color:#38b000} .n3{color:#fb5607} .n4{color:#8338ec} 
    .n5{color:#ff006e} .n6{color:#00f5d4} .n7{color:#2b2d42} .n8{color:#8d99ae}

</style>
""", unsafe_allow_html=True)

# ================= UI 主程序 =================

st.title("Minesweeper")

# --- 1. 游戏设置 (恢复自定义功能) ---
if not st.session_state.running:
    with st.container(border=True):
        st.subheader("🛠 Game Setup / 游戏设置")
        
        # 第一行：设置行和列 (恢复 Slider/NumberInput)
        c_row, c_col = st.columns(2)
        with c_row:
            R = st.number_input("Rows (行)", min_value=5, max_value=20, value=10)
        with c_col:
            C = st.number_input("Columns (列)", min_value=5, max_value=20, value=10)
            
        # 第二行：设置难度 (按你要求的倍率)
        diff = st.selectbox("Difficulty (难度)", ["Easy (0.3)", "Medium (0.5)", "Hard (0.7)"])
        
        # 计算雷数
        rate = 0.3 # 默认 Easy
        if "Medium" in diff: rate = 0.5
        elif "Hard" in diff: rate = 0.7
            
        # 按照你的公式：难度系数 * 格子总数
        total_cells = R * C
        M = int(total_cells * rate)
        M = max(1, min(M, total_cells - 1)) # 基础保护，防止雷数超过格子数
        
        st.write(f"**Mines:** {M} (Density: {int(rate*100)}%)")
        
        st.write("")
        # START 按钮
        if st.button("🚀 Start Game", type="primary", use_container_width=True):
            start(R, C, M)
            st.rerun()

# --- 2. 游戏界面 ---
else:
    # 顶部信息栏
    c1, c2, c3 = st.columns([1.5, 2, 1.5])
    
    with c2:
        left = st.session_state.mines - len(st.session_state.flags)
        status = "😊 Playing"
        if st.session_state.lost: status = "💥 Failed"
        if st.session_state.won: status = "🎉 Won"
        st.info(f"Mines: {left} | {status}")
    
    with c1:
        # 模式切换
        mode = "🚩 Flag Mode" if st.session_state.flag else "⛏️ Dig Mode"
        if st.button(mode, type="primary", use_container_width=True):
            st.session_state.flag = not st.session_state.flag
            st.rerun()
            
    with c3:
        # 重开
        if st.button("🔄 Restart", type="primary", use_container_width=True):
            st.session_state.running = False
            st.rerun()

    st.markdown("---")

    # 渲染棋盘
    board = st.session_state.board
    vis = st.session_state.revealed
    flg = st.session_state.flags
    
    if st.session_state.lost: st.error("BOOM! You hit a mine!")
    if st.session_state.won: st.success("Congratulations! All cleared!")

    for r in range(st.session_state.rows):
        cols = st.columns(st.session_state.cols)
        for c in range(st.session_state.cols):
            with cols[c]:
                key = f"{r}_{c}"
                is_rev = (r,c) in vis
                is_flg = (r,c) in flg
                end = st.session_state.lost or st.session_state.won
                
                # 逻辑分支：显示内容 or 显示按钮
                if is_rev or (end and board[r][c] == -1):
                    val = board[r][c]
                    if val == -1:
                        st.markdown("<div class='cell-revealed' style='background:#ffccd5;'>💣</div>", unsafe_allow_html=True)
                    elif val == 0:
                        st.markdown("<div class='cell-revealed'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='cell-revealed n{val}'>{val}</div>", unsafe_allow_html=True)
                else:
                    # 按钮逻辑
                    label = "🚩" if is_flg else " "
                    if not end:
                        # 游戏进行中：可点击的按钮 (Secondary)
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
                        # 游戏结束：静态展示
                        st.markdown(f"<div class='cell-revealed' style='background:#b0c4b1;color:#fff'>{label}</div>", unsafe_allow_html=True)
