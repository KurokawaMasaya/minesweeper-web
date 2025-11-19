import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="Minesweeper Pro", layout="centered", page_icon="💣")

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

# ================= 🎨 界面样式 (CSS) =================

st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 50% -20%, #2e3b55 0%, #1a1d29 50%, #0f111a 100%);
        font-family: 'Segoe UI', sans-serif;
    }
    h1 { color: white; text-align: center; margin-bottom: 0px; }
    
    /* 游戏区域容器 */
    .game-board {
        display: flex; flex-direction: column; align-items: center;
        background: rgba(255,255,255,0.05);
        padding: 20px; border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-top: 10px;
        width: fit-content; margin-left: auto; margin-right: auto;
    }

    /* 按钮通用样式 */
    div.stButton > button {
        font-weight: 600;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* 游戏格子按钮 (未揭开) */
    .grid-btn button {
        width: 38px !important; height: 38px !important;
        background: #3a3f50 !important;
        margin: 0 !important; padding: 0 !important;
        border: 1px solid #4a4f60 !important;
        box-shadow: 2px 2px 0px rgba(0,0,0,0.2);
        transition: transform 0.1s;
    }
    .grid-btn button:hover {
        background: #4d5366 !important;
        border-color: #666 !important;
        z-index: 2;
    }
    .grid-btn button:active {
        transform: scale(0.95);
    }

    /* 🚩 插旗模式下的鼠标样式 */
    .flag-mode-cursor button {
        cursor: copy !important; /* 看起来像个加号/复制，表示放置 */
        border-color: #ff6b6b !important;
    }

    /* ⛏️ 挖掘模式下的鼠标样式 */
    .dig-mode-cursor button {
        cursor: crosshair !important; /* 准星样式 */
    }

    /* 已揭开格子 */
    .cell {
        width: 38px; height: 38px;
        display: flex; align-items: center; justify-content: center;
        background: #1e2129;
        border: 1px solid #2a2e3a;
        border-radius: 4px;
        font-weight: bold; font-size: 18px;
    }

    /* Streamlit列间距消除 */
    div[data-testid="column"] { 
        width: 38px !important; flex: unset !important; padding: 1px !important; 
    }
    div[data-testid="stHorizontalBlock"] { justify-content: center; }

    /* 颜色定义 */
    .n1 { color: #4285F4; } .n2 { color: #34A853; } .n3 { color: #EA4335; } 
    .n4 { color: #A142F4; } .bomb { background: #500; }

    /* 顶部控制栏背景 */
    .control-panel {
        background: rgba(0,0,0,0.3); padding: 15px; border-radius: 12px;
        margin-bottom: 20px; border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

st.title("Minesweeper")

# 1. 游戏设置界面 (未开始时显示)
if not st.session_state.running:
    st.info("👇 Please configure and start the game below / 请在下方设置并开始游戏")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1: R = st.number_input("Rows (行)", 5, 15, 10)
        with c2: C = st.number_input("Cols (列)", 5, 15, 10)
        with c3: 
            diff = st.selectbox("Difficulty (难度)", ["Easy", "Medium", "Hard"])
            M = int(R*C*{"Easy":0.12, "Medium":0.18, "Hard":0.25}[diff])
        
        st.markdown("---")
        # START 按钮：加上了 help 提示
        if st.button(f"🚀 START GAME ({R}x{C}, {M} Mines)", type="primary", use_container_width=True, help="点击开始新游戏 / Click to start"):
            start(R,C,M)
            st.rerun()

# 2. 游戏主界面 (进行中/结束)
else:
    # 顶部控制区 (Control Panel)
    with st.container():
        st.markdown('<div class="control-panel">', unsafe_allow_html=True)
        
        # 使用 3 列布局：重开 - 状态 - 插旗
        c_restart, c_status, c_flag = st.columns([1, 1.5, 1])
        
        with c_restart:
            # RESTART 按钮
            if st.button("🔄 Restart / 重开", use_container_width=True, help="放弃当前进度并重新开始 / Reset Game"):
                st.session_state.running = False
                st.rerun()
        
        with c_status:
            # 中间显示状态文字
            mines_left = st.session_state.mines - len(st.session_state.flags)
            status_color = "red" if st.session_state.lost else ("green" if st.session_state.won else "orange")
            status_text = "💥 FAILED" if st.session_state.lost else ("🎉 WON" if st.session_state.won else "Playing")
            
            st.markdown(f"""
            <div style="text-align:center; line-height:1.2;">
                <div style="font-size:12px; color:#888;">MINES LEFT</div>
                <div style="font-size:24px; font-weight:bold; color:white;">💣 {mines_left}</div>
                <div style="font-size:14px; color:{status_color}; font-weight:bold;">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)

        with c_flag:
            # FLAG 按钮 (状态切换)
            mode_color = "primary" if st.session_state.flag else "secondary"
            label = "🚩 Flag: ON" if st.session_state.flag else "⛏️ Dig: ON"
            help_text = "当前是插旗模式" if st.session_state.flag else "当前是挖掘模式"
            
            if st.button(label, type=mode_color, use_container_width=True, help=f"点击切换模式 / Click to toggle. {help_text}"):
                st.session_state.flag = not st.session_state.flag
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    # 游戏棋盘区
    # 根据模式给容器加 class，改变鼠标指针样式
    cursor_class = "flag-mode-cursor" if st.session_state.flag else "dig-mode-cursor"
    st.markdown(f'<div class="game-board {cursor_class}">', unsafe_allow_html=True)

    # 胜利/失败提示 Banner
    if st.session_state.lost:
        st.error("💥 BOOM! You clicked a mine. / 你踩到雷了！")
    elif st.session_state.won:
        st.success("🎉 SUCCESS! You found all mines. / 恭喜通关！")

    # 渲染网格
    board = st.session_state.board
    vis = st.session_state.revealed
    flg = st.session_state.flags
    
    for r in range(st.session_state.rows):
        cols = st.columns(st.session_state.cols)
        for c in range(st.session_state.cols):
            with cols[c]:
                key = f"{r}-{c}"
                # 逻辑：是否显示内容
                if (r,c) in vis or (st.session_state.lost and board[r][c] == -1) or (st.session_state.won):
                    # 已揭开
                    val = board[r][c]
                    if val == -1:
                        # 如果是踩雷导致的，背景变红
                        bg_style = "background:#8b0000;" if ((r,c) in vis and val == -1) else ""
                        st.markdown(f"<div class='cell bomb' style='{bg_style}'>💣</div>", unsafe_allow_html=True)
                    elif val == 0:
                        st.markdown("<div class='cell'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='cell n{val}'>{val}</div>", unsafe_allow_html=True)
                else:
                    # 未揭开 (按钮)
                    # 插旗标记
                    btn_label = "🚩" if (r,c) in flg else ""
                    
                    # 按钮是否可用
                    disabled = st.session_state.lost or st.session_state.won
                    
                    # 在按钮容器上加 class 用于 CSS 选择
                    st.markdown('<div class="grid-btn">', unsafe_allow_html=True)
                    
                    # 如果游戏结束，渲染不可点的假按钮或禁用按钮
                    if disabled:
                         st.markdown(f"<div class='cell' style='background:#2a2e3a;color:red;'>{btn_label}</div>", unsafe_allow_html=True)
                    else:
                        if st.button(btn_label, key=key):
                            if st.session_state.flag:
                                if (r,c) in flg: flg.remove((r,c))
                                else: flg.add((r,c))
                                st.rerun()
                            elif (r,c) not in flg:
                                if not reveal(board, vis, flg, r, c):
                                    st.session_state.lost = True
                                st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 底部操作提示
    if st.session_state.running and not st.session_state.lost and not st.session_state.won:
        help_msg = "💡 Tip: Click **Flag: ON** to mark mines." if st.session_state.flag else "💡 Tip: You are in **Dig Mode**. Click to reveal."
        st.caption(help_msg)
