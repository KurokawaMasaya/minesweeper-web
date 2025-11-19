import streamlit as st
import random

# 页面配置：白底黑字，简约风
st.set_page_config(page_title="Minesweeper Minimal", layout="centered", page_icon="✏️")

# ================= 核心逻辑 (原版 MS.py，完全不动) =================
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

# ================= ✏️ 数独极简风 CSS =================
st.markdown("""
<style>
    /* 1. 全局背景：护眼纯白 */
    .stApp {
        background-color: #ffffff;
        color: #333333;
        font-family: 'Courier New', Courier, monospace; /* 打印机字体 */
    }
    
    h1 {
        color: #000;
        font-weight: bold;
        border-bottom: 2px solid #000;
        padding-bottom: 10px;
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
    }

    /* 2. 游戏区域外框：像数独的粗边框 */
    .sudoku-border {
        border: 3px solid #000000;
        padding: 5px;
        display: inline-block;
        background-color: #000; /* 利用间隙做网格线 */
    }

    /* 3. 格子按钮 (未揭开)：纯白方块，极细边框 */
    button[kind="secondary"] {
        width: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        border: 1px solid #ccc !important; /* 浅灰细线 */
        border-radius: 0 !important; /* 尖角，不要圆角 */
        background-color: #ffffff !important;
        color: transparent !important;
        transition: background-color 0.2s;
    }
    
    /* 鼠标悬停：浅灰，像铅笔涂抹 */
    button[kind="secondary"]:hover {
        background-color: #f0f0f0 !important;
        border-color: #999 !important;
    }
    
    /* 4. 功能按钮 (Start/Restart)：极简黑白 */
    button[kind="primary"] {
        background-color: #333 !important;
        color: #fff !important;
        border: none !important;
        border-radius: 0 !important;
        font-family: 'Courier New', monospace !important;
        font-weight: bold !important;
        min-width: 100px !important;
    }
    button[kind="primary"]:hover {
        background-color: #000 !important;
    }

    /* 5. 已揭开的格子：纸张质感 */
    .cell-paper {
        width: 40px; height: 40px;
        display: flex; align-items: center; justify-content: center;
        background-color: #ffffff; /* 保持纯白 */
        border: 1px solid #eee; /* 极淡的内部线 */
        font-weight: bold;
        font-size: 20px;
        font-family: 'Courier New', monospace;
    }
    
    /* 布局控制：消除间隙，让格子紧贴 */
    div[data-testid="column"] {
        width: 40px !important;
        flex: unset !important;
        padding: 0 !important; /* 0间距 */
        margin: 0 !important;
    }
    div[data-testid="stHorizontalBlock"] {
        justify-content: center;
        gap: 0 !important; /* 0间距 */
    }

    /* 数字颜色：使用低饱和度的经典墨水色 */
    .ink-1 { color: #0044cc; } /* 蓝墨水 */
    .ink-2 { color: #008000; } /* 绿墨水 */
    .ink-3 { color: #cc0000; } /* 红墨水 */
    .ink-4 { color: #000080; } /* 深蓝 */
    .ink-bomb { color: #000; font-weight: 900; } /* 纯黑炸弹 */

    /* 状态栏文字 */
    .status-text {
        font-family: 'Courier New', monospace;
        font-size: 16px;
        font-weight: bold;
        color: #333;
    }
    
    /* 旗帜模式激活时的提示 */
    .flag-mode-on button[kind="primary"] {
        background-color: #cc0000 !important; /* 红色警示 */
    }
</style>
""", unsafe_allow_html=True)

# ================= UI 主程序 =================

st.title("MINESWEEPER")

# --- 1. 极简设置栏 ---
if not st.session_state.running:
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        R = st.number_input("ROWS", 5, 20, 10)
    with c2:
        C = st.number_input("COLS", 5, 20, 10)
    with c3:
        # 恢复 10%, 15%, 20% 的合理难度
        diff_label = st.selectbox("DIFFICULTY", ["EASY (10%)", "NORMAL (15%)", "HARD (20%)"])
    
    if "EASY" in diff_label: rate = 0.10
    elif "NORMAL" in diff_label: rate = 0.15
    else: rate = 0.20
    
    M = int(R * C * rate)
    M = max(1, M)
    
    st.write(f"**MINES:** {M}")
    st.write("")
    
    if st.button("START GAME", type="primary", use_container_width=True):
        start(R, C, M)
        st.rerun()

# --- 2. 游戏界面 ---
else:
    # 顶部简单的文字状态
    c_left, c_mid, c_right = st.columns([1, 2, 1])
    
    with c_mid:
        left = st.session_state.mines - len(st.session_state.flags)
        status = "PLAYING"
        if st.session_state.lost: status = "FAILED"
        if st.session_state.won: status = "CLEARED"
        st.markdown(f"<div style='text-align:center' class='status-text'>MINES: {left} | {status}</div>", unsafe_allow_html=True)
    
    with c_left:
        # 模式切换：单纯的黑白按钮
        mode_txt = "[X] FLAG MODE" if st.session_state.flag else "[ ] DIG MODE"
        # 动态加个class给容器方便变色（可选）
        if st.button(mode_txt, type="primary", use_container_width=True):
            st.session_state.flag = not st.session_state.flag
            st.rerun()

    with c_right:
        if st.button("RESTART", type="primary", use_container_width=True):
            st.session_state.running = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 游戏结果文字 (打字机风格)
    if st.session_state.lost: 
        st.markdown("<div style='text-align:center; color:red; font-weight:bold;'>GAME OVER.</div>", unsafe_allow_html=True)
    if st.session_state.won: 
        st.markdown("<div style='text-align:center; color:green; font-weight:bold;'>PUZZLE SOLVED.</div>", unsafe_allow_html=True)

    # === 渲染纸质网格 ===
    
    # 1. 居中容器
    st.markdown("<div style='display:flex; justify-content:center;'>", unsafe_allow_html=True)
    
    # 2. 黑色粗边框容器 (Sudoku Border)
    st.markdown("<div class='sudoku-border'>", unsafe_allow_html=True)
    
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
                        # 炸弹：简单的黑色符号，或者红色X
                        char = "X" if val == -1 else str(val)
                        color_cls = "ink-bomb" if val == -1 else f"ink-{val}"
                        # 如果是失败踩到的雷，背景稍微灰一点
                        bg_style = "background:#ddd;" if (is_rev and val == -1) else ""
                        st.markdown(f"<div class='cell-paper {color_cls}' style='{bg_style}'>{char}</div>", unsafe_allow_html=True)
                    elif val == 0:
                        # 空地：纯白
                        st.markdown("<div class='cell-paper'></div>", unsafe_allow_html=True)
                    else:
                        # 数字
                        st.markdown(f"<div class='cell-paper ink-{val}'>{val}</div>", unsafe_allow_html=True)
                else:
                    # 未揭开：白色按钮
                    label = "P" if is_flg else " " # P for Pin/Flag
                    
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
                        # 结束后的未揭开区域：灰色斜线感
                        char = "P" if is_flg else "."
                        st.markdown(f"<div class='cell-paper' style='color:#999; background:#f9f9f9;'>{char}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True) # End sudoku-border
    st.markdown("</div>", unsafe_allow_html=True) # End center flex
