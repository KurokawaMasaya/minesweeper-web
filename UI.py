import streamlit as st
import random

# 设置为宽屏，防止自动挤压，但我们会通过 CSS 强制内容居中
st.set_page_config(page_title="Classic Minesweeper", layout="wide", page_icon="💣")

# ================= 核心逻辑 (不动) =================
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

# ================= 🎨 经典 XP 风格 CSS (暴力消除间距) =================

# 定义格子的大小 (像素)
CELL_SIZE = 35 

st.markdown(f"""
<style>
    /* 1. 全局背景：经典的Windows青灰色 */
    .stApp {{
        background-color: #008080; /* 经典桌面的颜色 */
        font-family: 'Tahoma', sans-serif;
    }}
    
    /* 2. 游戏主容器：模仿 Windows 窗口 */
    .window-frame {{
        background: #c0c0c0;
        border: 2px solid #dfdfdf;
        border-right-color: #808080;
        border-bottom-color: #808080;
        padding: 6px;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.5);
        display: inline-block; /* 让容器大小自适应内容 */
        margin-top: 20px;
    }}
    
    /* 3. 顶部信息栏 (凹陷效果) */
    .status-panel {{
        border: 2px solid #808080;
        border-right-color: #fff;
        border-bottom-color: #fff;
        padding: 5px;
        margin-bottom: 8px;
        background: #c0c0c0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    /* 数字显示屏风格 (红字黑底) */
    .digital-display {{
        background: #000;
        color: #ff0000;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        font-size: 22px;
        padding: 2px 6px;
        border-right: 1px solid #fff;
        border-bottom: 1px solid #fff;
        border-top: 1px solid #808080;
        border-left: 1px solid #808080;
        min-width: 60px;
        text-align: center;
        line-height: 1;
    }}

    /* 4. 核心：网格消除间距的黑魔法 */
    
    /* 强制清除 Streamlit 列之间的 gap */
    div[data-testid="stHorizontalBlock"] {{
        gap: 0 !important; 
    }}
    
    /* 强制每一列宽度固定，并且没有内边距 */
    div[data-testid="column"] {{
        width: {CELL_SIZE}px !important;
        flex: 0 0 {CELL_SIZE}px !important;
        padding: 0 !important;
        margin: 0 !important;
    }}

    /* 按钮样式：经典 Windows 3D 凸起 */
    div.stButton > button {{
        width: {CELL_SIZE}px !important;
        height: {CELL_SIZE}px !important;
        border-radius: 0 !important; /* 直角 */
        background: #c0c0c0 !important;
        
        /* 经典 3D 边框 */
        border-top: 2px solid #fff !important;
        border-left: 2px solid #fff !important;
        border-right: 2px solid #808080 !important;
        border-bottom: 2px solid #808080 !important;
        
        margin: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
        transition: none !important; /* 去掉现代动画 */
    }}
    
    div.stButton > button:active {{
        border: none !important;
        border-top: 1px solid #808080 !important; /* 简单的凹陷模拟 */
        border-left: 1px solid #808080 !important;
    }}

    /* 5. 已揭开的格子：凹陷效果 */
    .cell-revealed {{
        width: {CELL_SIZE}px;
        height: {CELL_SIZE}px;
        background: #c0c0c0;
        border-left: 1px solid #808080;
        border-top: 1px solid #808080;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 18px;
        font-family: 'Verdana', sans-serif;
        line-height: 1;
        cursor: default;
    }}

    /* 数字颜色 (经典 RGB) */
    .c1 {{ color: #0000ff; }} 
    .c2 {{ color: #008000; }} 
    .c3 {{ color: #ff0000; }} 
    .c4 {{ color: #000080; }} 
    .c5 {{ color: #800000; }}
    .c6 {{ color: #008080; }}
    .c7 {{ color: #000000; }}
    .c8 {{ color: #808080; }}
    
    .mine-hit {{
        background: #ff0000 !important;
        border: none;
    }}

    /* 6. 中间那个笑脸按钮 */
    .face-btn button {{
        width: 40px !important;
        height: 40px !important;
        font-size: 24px !important;
        padding-top: 0px !important;
    }}
    
    /* 控制按钮 (Start/Mode) 的微调 */
    .control-area {{ margin-top: 10px; text-align: center; }}

</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

# 使用 columns 将整个游戏区域居中
empty_left, main_game, empty_right = st.columns([1, 2, 1])

with main_game:
    # 外层灰色窗口框架
    st.markdown("<div style='display:flex; justify-content:center;'>", unsafe_allow_html=True)
    st.markdown("<div class='window-frame'>", unsafe_allow_html=True)

    # 1. 状态栏 (顶部)
    if st.session_state.running:
        mines_left = st.session_state.mines - len(st.session_state.flags)
        # 决定笑脸表情
        face = "😎" if st.session_state.won else ("😵" if st.session_state.lost else "🙂")
        
        # 使用 columns 布局状态栏内部
        c_bomb, c_face, c_mode = st.columns([2, 1.5, 2])
        
        with c_bomb:
            st.markdown(f"<div class='digital-display'>{max(0, mines_left):03}</div>", unsafe_allow_html=True)
            
        with c_face:
            # 重开按钮 (笑脸)
            st.markdown('<div class="face-btn">', unsafe_allow_html=True)
            if st.button(face, key="restart_face", help="Restart Game"):
                st.session_state.running = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c_mode:
            # 模式切换 (做一个复古的按钮)
            mode_txt = "🚩 FLAG" if st.session_state.flag else "⛏️ DIG"
            if st.button(mode_txt, key="mode_toggle"):
                st.session_state.flag = not st.session_state.flag
                st.rerun()
    else:
        # 标题
        st.markdown("<h3 style='color:black;margin:0;text-align:center;margin-bottom:10px;'>Minesweeper 98</h3>", unsafe_allow_html=True)

    # 2. 游戏设置 (如果未开始)
    if not st.session_state.running:
        st.markdown("<div style='background:#c0c0c0; padding:10px;'>", unsafe_allow_html=True)
        col_set1, col_set2 = st.columns(2)
        with col_set1:
            # 经典难度预设
            difficulty = st.selectbox("Level", ["Beginner (9x9)", "Intermediate (16x16)", "Custom"])
        
        if difficulty == "Beginner (9x9)":
            R, C, M = 9, 9, 10
        elif difficulty == "Intermediate (16x16)":
            R, C, M = 16, 16, 40
        else:
            with col_set2:
                st.caption("Custom Settings")
            R = st.number_input("Rows", 5, 20, 10)
            C = st.number_input("Cols", 5, 20, 10)
            M = st.number_input("Mines", 1, R*C-1, int(R*C*0.15))

        st.write("")
        if st.button("Start Game", use_container_width=True):
            start(R, C, M)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. 扫雷网格区域 (游戏进行中)
    else:
        # 这是一个凹陷的边框容器，用来包裹所有格子
        st.markdown("<div style='border:3px solid #808080; border-right-color:#fff; border-bottom-color:#fff; border-style:inset; display:inline-block;'>", unsafe_allow_html=True)
        
        board = st.session_state.board
        vis = st.session_state.revealed
        flg = st.session_state.flags
        
        for r in range(st.session_state.rows):
            # 这里的 columns 已经被 CSS 强制去掉了间距
            cols = st.columns(st.session_state.cols)
            for c in range(st.session_state.cols):
                with cols[c]:
                    key = f"{r}-{c}"
                    
                    # 逻辑判定
                    is_rev = (r,c) in vis
                    is_flg = (r,c) in flg
                    is_mine = board[r][c] == -1
                    game_over = st.session_state.lost or st.session_state.won
                    
                    # 显示内容
                    if is_rev or (game_over and is_mine):
                        val = board[r][c]
                        if val == -1:
                            # 踩雷是红底，其他雷是透视
                            bg_cls = "mine-hit" if is_rev else "" 
                            st.markdown(f"<div class='cell-revealed {bg_cls}'>💣</div>", unsafe_allow_html=True)
                        elif val == 0:
                            st.markdown("<div class='cell-revealed'></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='cell-revealed c{val}'>{val}</div>", unsafe_allow_html=True)
                    else:
                        # 按钮 (未揭开)
                        # 如果游戏结束，显示静态方块；否则显示按钮
                        if game_over:
                            flag_content = "🚩" if is_flg else ""
                            # 猜错的旗子打个叉 (可选优化，这里简单处理)
                            st.markdown(f"<div class='stButton'><button style='pointer-events:none;'>{flag_content}</button></div>", unsafe_allow_html=True)
                        else:
                            # 按钮上显示旗子
                            label = "🚩" if is_flg else "" 
                            if st.button(label, key=key):
                                if st.session_state.flag:
                                    if is_flg: flg.remove((r,c))
                                    else: flg.add((r,c))
                                    st.rerun()
                                elif not is_flg:
                                    if not reveal(board, vis, flg, r, c):
                                        st.session_state.lost = True
                                    st.rerun()
                                    
        st.markdown("</div>", unsafe_allow_html=True) # 结束网格边框
    
    st.markdown("</div>", unsafe_allow_html=True) # 结束 window-frame
    st.markdown("</div>", unsafe_allow_html=True) # 结束居中容器

    # 底部简单的操作说明
    if st.session_state.running:
         info_text = "LEFT CLICK to Dig" if not st.session_state.flag else "LEFT CLICK to Flag"
         st.markdown(f"<div style='text-align:center; color:white; margin-top:10px; font-weight:bold;'>Current Mode: {info_text}</div>", unsafe_allow_html=True)
