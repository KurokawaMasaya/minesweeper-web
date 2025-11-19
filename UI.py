import streamlit as st
import random

# 页面配置：手绘风
st.set_page_config(page_title="Paper Minesweeper", layout="centered", page_icon="🖍️")

# ================= 核心逻辑 (完全保留原版算法) =================
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

# ================= 🖍️ 蜡笔手绘风 CSS =================

st.markdown("""
<style>
    /* 1. 引入 Google Fonts: Patrick Hand (完美的手写蜡笔字体) */
    @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

    /* 2. 全局样式：米黄色素描纸背景 */
    .stApp {
        background-color: #fdfcf0; /* 暖色调纸张 */
        font-family: 'Patrick Hand', cursive, sans-serif !important;
    }
    
    h1, h2, h3, p, div, button, span {
        font-family: 'Patrick Hand', cursive, sans-serif !important;
        color: #2c3e50;
    }
    
    h1 {
        border-bottom: 3px dashed #2c3e50; /* 虚线下划线 */
        padding-bottom: 10px;
        text-align: center;
        font-size: 3rem !important;
    }

    /* 3. 核心：井字棋 (Tic-Tac-Toe) 风格网格 */
    
    /* 强制消除 Streamlit 所有默认间距 */
    div[data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        justify-content: center;
    }
    
    div[data-testid="column"] {
        width: 42px !important;
        flex: unset !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* 通用格子样式 (基础) */
    .base-cell {
        width: 42px !important;
        height: 42px !important;
        padding: 0 !important;
        border-radius: 0 !important; /* 必须直角 */
        border: 1px solid #2c3e50 !important; /* 手绘风黑线 */
        margin: 0 !important;
        font-size: 24px !important;
        font-weight: bold !important;
    }

    /* A. 未揭开的按钮 (Secondary) */
    button[kind="secondary"] {
        width: 42px !important;
        height: 42px !important;
        border: 1px solid #2c3e50 !important;
        border-radius: 0 !important;
        background-color: transparent !important; /* 透明，显示纸张背景 */
        color: transparent !important;
        transition: background 0.2s;
    }
    
    /* 鼠标悬停：像铅笔涂了一层灰 */
    button[kind="secondary"]:hover {
        background-color: rgba(0,0,0,0.05) !important;
    }

    /* B. 已揭开的格子 */
    .cell-drawn {
        width: 42px; height: 42px;
        display: flex; align-items: center; justify-content: center;
        border: 1px solid #2c3e50;
        background-color: rgba(0,0,0,0.03); /* 稍微深一点点 */
        font-size: 26px;
        line-height: 1;
        cursor: default;
    }
    
    /* C. 功能按钮 (Start/Restart)：手绘框 */
    button[kind="primary"] {
        background: transparent !important;
        color: #2c3e50 !important;
        border: 3px solid #2c3e50 !important;
        border-radius: 255px 15px 225px 15px / 15px 225px 15px 255px !important; /* 模拟手画的不规则圆角 */
        font-size: 20px !important;
        padding: 5px 20px !important;
        box-shadow: 2px 2px 0px #2c3e50 !important;
        transition: transform 0.1s !important;
    }
    button[kind="primary"]:hover {
        transform: translate(1px, 1px);
        box-shadow: 1px 1px 0px #2c3e50 !important;
        background-color: #fff !important;
    }

    /* 蜡笔数字颜色 (稍微调低饱和度，模仿画笔) */
    .c1 { color: #2980b9; } /* 蓝蜡笔 */
    .c2 { color: #27ae60; } /* 绿蜡笔 */
    .c3 { color: #c0392b; } /* 红蜡笔 */
    .c4 { color: #8e44ad; } /* 紫蜡笔 */
    .c5 { color: #d35400; } /* 橙蜡笔 */
    
    .bomb-drawn {
        color: #000;
        font-size: 28px;
    }
    
    /* 旗帜 */
    .flag-mark {
        color: #e74c3c;
        font-weight: bold;
    }
    
    /* 容器边框 (画在最外面的大框) */
    .board-container {
        display: inline-block;
        border: 3px solid #2c3e50; /* 加粗的外边框 */
        background: #fff;
    }

</style>
""", unsafe_allow_html=True)

# ================= UI 主程序 =================

st.title("Minesweeper") # 字体会自动应用 Patrick Hand

# --- 1. 设置区域 (手绘风) ---
if not st.session_state.running:
    st.markdown("### 📝 Game Setup")
    
    c1, c2 = st.columns(2)
    with c1:
        # 手绘风里，Number Input 也会变字体
        R = st.number_input("Rows", 5, 20, 10)
    with c2:
        C = st.number_input("Cols", 5, 20, 10)
        
    # 难度选择 (Easy=10%, Med=15%, Hard=20%)
    diff = st.selectbox("Difficulty", ["Easy (10%)", "Medium (15%)", "Hard (20%)"])
    
    if "Easy" in diff: rate = 0.10
    elif "Medium" in diff: rate = 0.15
    else: rate = 0.20
    
    M = max(1, int(R * C * rate))
    
    st.write(f"Mines to find: **{M}**")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 开始按钮
    if st.button("Play Game", type="primary", use_container_width=True):
        start(R, C, M)
        st.rerun()

# --- 2. 游戏区域 ---
else:
    # 顶部手写状态栏
    c1, c2, c3 = st.columns([1.5, 2, 1.5])
    
    with c2:
        left = st.session_state.mines - len(st.session_state.flags)
        # 状态文字
        status = "Playing..."
        if st.session_state.lost: status = "Oops! Boom!"
        if st.session_state.won: status = "You Did It!"
        
        st.markdown(f"<div style='text-align:center; font-size:24px; border-bottom:2px solid #ccc;'>{left} 💣 | {status}</div>", unsafe_allow_html=True)
    
    with c1:
        # 模式切换
        mode_text = "🚩 Flagging" if st.session_state.flag else "⛏️ Digging"
        if st.button(mode_text, type="primary", use_container_width=True):
            st.session_state.flag = not st.session_state.flag
            st.rerun()
            
    with c3:
        if st.button("Restart", type="primary", use_container_width=True):
            st.session_state.running = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 结果提示
    if st.session_state.lost: 
        st.markdown("<h2 style='color:#c0392b; text-align:center;'>Game Over!</h2>", unsafe_allow_html=True)
    if st.session_state.won: 
        st.markdown("<h2 style='color:#27ae60; text-align:center;'>Victory!</h2>", unsafe_allow_html=True)

    # === 渲染井字棋盘 ===
    
    # 居中外框
    st.markdown("<div style='display:flex; justify-content:center;'>", unsafe_allow_html=True)
    # 加粗外边框容器
    st.markdown("<div class='board-container'>", unsafe_allow_html=True)
    
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
                
                # 显示逻辑
                if is_rev or (end and board[r][c] == -1):
                    val = board[r][c]
                    if val == -1:
                        # 炸弹：用手写的 X 或 * 表示
                        st.markdown("<div class='cell-drawn bomb-drawn'>*</div>", unsafe_allow_html=True)
                    elif val == 0:
                        # 空地
                        st.markdown("<div class='cell-drawn'></div>", unsafe_allow_html=True)
                    else:
                        # 数字
                        st.markdown(f"<div class='cell-drawn c{val}'>{val}</div>", unsafe_allow_html=True)
                else:
                    # 按钮
                    # 这里插旗用简单的 F 或 P
                    label = "P" if is_flg else " "
                    
                    if not end:
                        # 关键：type="secondary" 会应用我们的透明边框样式
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
                        # 结束后的未揭开格子：画斜线或阴影
                        bg = "background: repeating-linear-gradient(45deg, #eee, #eee 5px, #fff 5px, #fff 10px);"
                        st.markdown(f"<div class='cell-drawn' style='color:#999; {bg}'>{label}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True) # end board-container
    st.markdown("</div>", unsafe_allow_html=True) # end center flex
