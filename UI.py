import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="Minesweeper Fixed", layout="centered", page_icon="💣")

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

# ================= 🎨 修复后的 CSS =================

st.markdown("""
<style>
    /* 全局背景 */
    .stApp {
        background: #2b2d42;
        font-family: sans-serif;
    }
    
    h1 { color: white; text-align: center; margin-bottom: 30px; }

    /* --- 关键修复：按钮样式分离 --- */

    /* 1. 类型为 Secondary 的按钮 -> 这是【雷区格子】 */
    /* 强制变成小方块 */
    button[kind="secondary"] {
        width: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        border-radius: 4px !important;
        border: 1px solid #4a4e69 !important;
        background-color: #8d99ae !important;
        color: transparent !important; /* 隐藏默认文字，用 emoji 或 CSS 显示 */
        transition: transform 0.1s;
    }
    button[kind="secondary"]:hover {
        background-color: #edf2f4 !important;
        transform: scale(1.05);
    }
    
    /* 2. 类型为 Primary 的按钮 -> 这是【开始/重启/功能键】 */
    /* 恢复正常宽度，自适应文字 */
    button[kind="primary"] {
        width: auto !important;
        height: auto !important;
        min-width: 120px; /* 保证按钮够宽 */
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
    
    /* 3. 已揭开的格子样式 */
    .cell-revealed {
        width: 40px; height: 40px;
        display: flex; align-items: center; justify-content: center;
        background: #edf2f4;
        border-radius: 4px;
        font-weight: 900;
        font-size: 20px;
        color: #2b2d42;
    }
    
    /* 4. 布局微调 */
    div[data-testid="column"] {
        width: 40px !important; /* 强制列宽适应格子 */
        flex: unset !important;
        padding: 2px !important;
    }
    div[data-testid="stHorizontalBlock"] {
        justify-content: center; /* 居中显示 */
    }
    
    /* 数字颜色 */
    .n1{color:#3a86ff} .n2{color:#38b000} .n3{color:#fb5607} .bomb{font-size:20px}

</style>
""", unsafe_allow_html=True)

# ================= UI 逻辑 =================

st.title("Minesweeper")

# --- 1. 游戏设置 (未开始时) ---
if not st.session_state.running:
    # 使用原生容器，不要自己写 HTML div，防止那个 Band 出现
    with st.container(border=True):
        st.subheader("🛠 Game Setup")
        
        c1, c2 = st.columns(2)
        with c1:
            diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        with c2:
            # 对应不同难度的大小
            s_map = {"Easy":(8,8,8), "Medium":(10,10,15), "Hard":(12,12,25)}
            R, C, M = s_map[diff]
            st.metric("Grid Size", f"{R} x {C}")

        st.write("")
        # Start 按钮：设置为 Primary，这样 CSS 就会让它变宽，不会竖排了
        if st.button("🚀 Start Game", type="primary", use_container_width=True):
            start(R,C,M)
            st.rerun()

# --- 2. 游戏进行中 ---
else:
    # 顶部控制栏
    c1, c2, c3 = st.columns([1.5, 2, 1.5])
    
    with c2:
        # 简单的状态文字
        left = st.session_state.mines - len(st.session_state.flags)
        status = "😊 Playing"
        if st.session_state.lost: status = "💥 Failed"
        if st.session_state.won: status = "🎉 Won"
        st.info(f"Mines: {left} | {status}")
    
    with c1:
        # 模式切换：设为 Primary 保证宽度正常
        mode = "🚩 Flag Mode" if st.session_state.flag else "⛏️ Dig Mode"
        if st.button(mode, type="primary", use_container_width=True):
            st.session_state.flag = not st.session_state.flag
            st.rerun()
            
    with c3:
        # 重开按钮：设为 Primary
        if st.button("🔄 Restart", type="primary", use_container_width=True):
            st.session_state.running = False
            st.rerun()

    st.markdown("---")
    
    # 游戏网格
    board = st.session_state.board
    vis = st.session_state.revealed
    flg = st.session_state.flags
    
    # 胜利/失败弹窗
    if st.session_state.lost: st.error("BOOM! Game Over.")
    if st.session_state.won: st.success("Congratulations!")

    # 渲染 Grid
    for r in range(st.session_state.rows):
        cols = st.columns(st.session_state.cols)
        for c in range(st.session_state.cols):
            with cols[c]:
                key = f"{r}_{c}"
                # 状态判断
                is_rev = (r,c) in vis
                is_flg = (r,c) in flg
                end = st.session_state.lost or st.session_state.won
                
                if is_rev or (end and board[r][c] == -1):
                    val = board[r][c]
                    if val == -1:
                        st.markdown("<div class='cell-revealed'>💣</div>", unsafe_allow_html=True)
                    elif val == 0:
                        st.markdown("<div class='cell-revealed'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='cell-revealed n{val}'>{val}</div>", unsafe_allow_html=True)
                else:
                    # 未揭开的按钮 (Secondary类型)
                    # 按钮文字设为空格，旗子通过 label 传递
                    # 如果游戏结束，禁用按钮
                    label = "🚩" if is_flg else " "
                    
                    if not end:
                        # 普通游戏按钮
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
                        # 结束后的占位符
                        st.markdown(f"<div class='cell-revealed' style='background:#ccc;color:#666'>{label}</div>", unsafe_allow_html=True)
