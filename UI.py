import streamlit as st
import random

# 设置页面
st.set_page_config(page_title="Minesweeper 98", layout="centered", page_icon="💣")

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

# ================= 🎨 修复版 CSS (精准定位) =================

CELL_SIZE = 30  # 格子大小

st.markdown(f"""
<style>
    /* 全局背景：Windows 经典青色 */
    .stApp {{
        background-color: #008080;
        font-family: 'Tahoma', sans-serif;
    }}

    /* ================= 1. 修复控制区按钮 (Start/Flag/Restart) ================= */
    /* 这些按钮必须是宽的，不能被压缩 */
    .control-area {{
        margin-bottom: 15px;
        text-align: center;
    }}
    
    /* 针对控制区的按钮样式 */
    .control-area button {{
        width: auto !important;     /* 关键修复：宽度自适应文字 */
        height: auto !important;    /* 高度自适应 */
        min-width: 100px !important;
        padding: 8px 15px !important;
        background: #c0c0c0 !important;
        border: 2px solid #fff !important;
        border-right-color: #404040 !important;
        border-bottom-color: #404040 !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 0 !important;
        box-shadow: none !important;
    }}
    .control-area button:active {{
        border: 1px solid #404040 !important;
        transform: translateY(1px);
    }}

    /* ================= 2. 雷区格子 (XP-GRID) ================= */
    /* 只有放在这个 div 下面的按钮才会被强制变成小方块 */
    
    .xp-grid {{
        display: inline-block;
        background: #c0c0c0;
        border: 3px solid #808080;
        border-left-color: #fff;
        border-top-color: #fff;
        padding: 5px;
    }}

    /* 强制消除列间距 */
    .xp-grid div[data-testid="column"] {{
        width: {CELL_SIZE}px !important;
        flex: 0 0 {CELL_SIZE}px !important;
        padding: 0 !important; margin: 0 !important;
    }}
    
    .xp-grid div[data-testid="stHorizontalBlock"] {{
        gap: 0 !important;
    }}

    /* 只有雷区里的按钮才强制 30x30 */
    .xp-grid div.stButton > button {{
        width: {CELL_SIZE}px !important;
        height: {CELL_SIZE}px !important;
        border-radius: 0 !important;
        background: #c0c0c0 !important;
        border-top: 2px solid #fff !important;
        border-left: 2px solid #fff !important;
        border-right: 2px solid #808080 !important;
        border-bottom: 2px solid #808080 !important;
        margin: 0 !important; padding: 0 !important;
        line-height: 1 !important;
    }}

    /* 已揭开的格子 */
    .revealed-cell {{
        width: {CELL_SIZE}px;
        height: {CELL_SIZE}px;
        line-height: {CELL_SIZE}px;
        text-align: center;
        border-left: 1px solid #808080;
        border-top: 1px solid #808080;
        font-family: 'Courier New', monospace;
        font-weight: 900;
        font-size: 18px;
        cursor: default;
    }}

    /* 颜色 */
    .c1 {{ color: blue; }} .c2 {{ color: green; }} .c3 {{ color: red; }}
    .c4 {{ color: darkblue; }} .c5 {{ color: darkred; }}
    .bomb {{ background: red; color: black; }}
    
</style>
""", unsafe_allow_html=True)

# ================= 界面构建 =================

st.title("Minesweeper 98")

# --- 控制区域 (CSS class: control-area) ---
# 使用 st.container 配合 HTML div 包裹，确保样式只作用于这里
st.markdown('<div class="control-area">', unsafe_allow_html=True)

if not st.session_state.running:
    # 未开始：显示开始菜单
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        # 这里的按钮由于在 control-area 下，会自动变宽
        st.markdown("### Game Setup")
        diff = st.selectbox("Difficulty", ["Beginner (9x9)", "Intermediate (16x16)", "Expert (16x30)"])
        
        if st.button("Start Game"):
            if "Beginner" in diff: R,C,M = 9,9,10
            elif "Intermediate" in diff: R,C,M = 16,16,40
            else: R,C,M = 16,30,99
            start(R,C,M)
            st.rerun()

else:
    # 进行中：显示顶部状态栏
    col_info, col_face, col_toggle = st.columns([2, 1, 2])
    
    with col_info:
        left = st.session_state.mines - len(st.session_state.flags)
        st.markdown(f"<div style='background:black;color:red;font-family:monospace;font-size:24px;padding:5px;border:2px inset #808080;display:inline-block;'>{max(0, left):03}</div>", unsafe_allow_html=True)
        
    with col_face:
        # 重开按钮 (表情)
        face = "😎" if st.session_state.won else ("😵" if st.session_state.lost else "🙂")
        if st.button(face, key="restart_btn"):
            st.session_state.running = False
            st.rerun()
            
    with col_toggle:
        # 模式切换按钮 (宽按钮)
        mode_text = "🚩 Flag Mode" if st.session_state.flag else "⛏️ Dig Mode"
        # 这里的按钮也会正常显示宽度
        if st.button(mode_text, key="mode_btn"):
            st.session_state.flag = not st.session_state.flag
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True) # 结束 control-area


# --- 游戏雷区 (CSS class: xp-grid) ---
# 只有这里面的按钮会被压缩成小正方形
if st.session_state.running:
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True) # 居中容器
    st.markdown('<div class="xp-grid">', unsafe_allow_html=True) # 雷区专用样式容器
    
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
                
                # 逻辑判定
                if is_rev or (st.session_state.lost and board[r][c] == -1) or st.session_state.won:
                    val = board[r][c]
                    if val == -1:
                        bg = "bomb" if is_rev else "" # 踩到的雷变红
                        st.markdown(f"<div class='revealed-cell {bg}'>💣</div>", unsafe_allow_html=True)
                    elif val == 0:
                        st.markdown("<div class='revealed-cell'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='revealed-cell c{val}'>{val}</div>", unsafe_allow_html=True)
                else:
                    # 这里的 button 会被 .xp-grid div.stButton > button 规则强制变为 30px 宽
                    label = "🚩" if is_flg else ""
                    # 游戏结束锁死按钮
                    if st.session_state.lost or st.session_state.won:
                         st.markdown(f"<div class='stButton'><button disabled style='color:red'>{label}</button></div>", unsafe_allow_html=True)
                    else:
                        if st.button(label, key=key):
                            if st.session_state.flag:
                                if is_flg: flg.remove((r,c))
                                else: flg.add((r,c))
                                st.rerun()
                            elif not is_flg:
                                if not reveal(board, vis, flg, r, c):
                                    st.session_state.lost = True
                                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True) # 结束 xp-grid
    st.markdown('</div>', unsafe_allow_html=True) # 结束居中
