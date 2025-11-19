import streamlit as st
import random

# 页面设置：使用宽屏模式让布局更舒展
st.set_page_config(page_title="Crystal Minesweeper", layout="centered", page_icon="💎")

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

# ================= 💎 终极毛玻璃 UI (CSS) =================

st.markdown("""
<style>
    /* 1. 背景：高级深海渐变，衬托白字非常清晰 */
    .stApp {
        background: radial-gradient(circle at center, #2b5876 0%, #4e4376 100%);
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    /* 2. 标题 */
    h1 {
        color: rgba(255, 255, 255, 0.95) !important;
        text-shadow: 0 0 20px rgba(255,255,255,0.4);
        font-weight: 300 !important;
        letter-spacing: 2px;
        margin-bottom: 20px !important;
    }

    /* 3. 游戏容器：磨砂玻璃卡片 */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        text-align: center;
        margin-bottom: 20px;
    }

    /* 4. 按钮样式 (未揭开的格子)：半透明果冻 */
    div.stButton > button {
        width: 45px !important;
        height: 45px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        background: rgba(255, 255, 255, 0.15) !important; /* 半透明白 */
        border-radius: 8px !important;
        color: white !important;
        transition: all 0.2s ease !important;
        font-weight: bold !important;
    }

    div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.4) !important;
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.4);
        border-color: white !important;
    }

    div.stButton > button:active {
        transform: scale(0.95);
    }

    /* 5. 已揭开的格子：乳白色背景，高对比度数字 */
    .cell-revealed {
        width: 45px;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.9); /* 不透明的乳白色 */
        border-radius: 8px;
        font-family: 'Verdana', sans-serif;
        font-weight: 900;
        font-size: 22px;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* 数字颜色 - 这种配色在白色背景上最清晰 */
    .n1 { color: #2563eb; } /* 亮蓝 */
    .n2 { color: #059669; } /* 翠绿 */
    .n3 { color: #dc2626; } /* 鲜红 */
    .n4 { color: #7c3aed; } /* 紫色 */
    .n5 { color: #d97706; } /* 橙色 */
    
    .bomb { 
        background: #ef4444 !important; 
        color: white !important;
        font-size: 24px;
        animation: shake 0.5s;
    }
    
    /* 旗帜标记 */
    .flagged-mark {
        color: #ff6b6b;
        font-size: 22px;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
    }

    /* Streamlit 布局微调 */
    div[data-testid="column"] {
        width: 45px !important;
        flex: unset !important;
        padding: 3px !important; /* 保留一点间隙，好看 */
    }
    div[data-testid="stHorizontalBlock"] {
        justify-content: center;
    }
    
    /* 模式切换按钮的高亮 */
    .mode-active {
        border: 2px solid #ffdd00 !important;
        background: rgba(255, 221, 0, 0.2) !important;
        color: #ffdd00 !important;
    }
    
    @keyframes shake { 0% { transform: translate(1px, 1px); } 50% { transform: translate(-1px, -2px); } 100% { transform: translate(0, 0); } }

</style>
""", unsafe_allow_html=True)

# ================= UI 构建 =================

st.title("Crystal Minesweeper")

# --- 游戏未开始：漂亮的启动卡片 ---
if not st.session_state.running:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🎮 New Game Setup")
    
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        # 将设置放在中间
        diff = st.select_slider("Difficulty Level", options=["Easy", "Medium", "Hard"])
        
        # 根据难度预设参数
        if diff == "Easy": R, C, M = 8, 8, 8
        elif diff == "Medium": R, C, M = 10, 10, 15
        else: R, C, M = 12, 12, 25
        
        st.write("")
        if st.button("✨ Start Game", type="primary", use_container_width=True):
            start(R,C,M)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 游戏进行中 ---
else:
    # 1. 顶部控制栏 (透明悬浮)
    c_left, c_mid, c_right = st.columns([1.5, 2, 1.5])
    
    with c_mid:
        # 状态显示
        mines_left = st.session_state.mines - len(st.session_state.flags)
        state_text = "Playing..."
        if st.session_state.lost: state_text = "💀 Failed"
        if st.session_state.won: state_text = "🏆 Victory!"
        
        st.markdown(f"""
        <div style="text-align:center; background:rgba(0,0,0,0.3); border-radius:50px; padding:8px 20px; color:white; font-weight:bold; border:1px solid rgba(255,255,255,0.2);">
            💣 {mines_left} &nbsp; | &nbsp; {state_text}
        </div>
        """, unsafe_allow_html=True)

    with c_left:
        # 模式切换
        mode_icon = "🚩" if st.session_state.flag else "⛏️"
        mode_txt = "Flag Mode" if st.session_state.flag else "Dig Mode"
        btn_type = "primary" if st.session_state.flag else "secondary"
        
        if st.button(f"{mode_icon} {mode_txt}", use_container_width=True, help="Click to toggle mode"):
            st.session_state.flag = not st.session_state.flag
            st.rerun()

    with c_right:
        if st.button("🔄 Restart", use_container_width=True):
            st.session_state.running = False
            st.rerun()

    # 2. 游戏主区域 (毛玻璃卡片)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card' style='display:inline-block; padding:20px;'>", unsafe_allow_html=True)
    
    # 胜利/失败 弹窗效果
    if st.session_state.won:
        st.balloons()
        st.success("You cleared all mines! Amazing!")
    elif st.session_state.lost:
        st.error("BOOM! Game Over.")

    board = st.session_state.board
    vis = st.session_state.revealed
    flg = st.session_state.flags
    
    # 渲染网格
    for r in range(st.session_state.rows):
        cols = st.columns(st.session_state.cols)
        for c in range(st.session_state.cols):
            with cols[c]:
                key = f"{r}_{c}"
                is_rev = (r,c) in vis
                is_flag = (r,c) in flg
                game_over = st.session_state.lost or st.session_state.won
                
                # A. 已揭开 或 游戏结束看答案
                if is_rev or (game_over and board[r][c] == -1):
                    val = board[r][c]
                    if val == -1:
                        # 雷：红色背景
                        st.markdown("<div class='cell-revealed bomb'>💣</div>", unsafe_allow_html=True)
                    elif val == 0:
                        # 空：乳白色背景
                        st.markdown("<div class='cell-revealed'></div>", unsafe_allow_html=True)
                    else:
                        # 数字：乳白色背景 + 彩色数字
                        st.markdown(f"<div class='cell-revealed n{val}'>{val}</div>", unsafe_allow_html=True)
                
                # B. 未揭开 (按钮)
                else:
                    # 如果已经结束，显示不可点击的半透明块
                    if game_over:
                         flag_disp = "🚩" if is_flag else ""
                         st.markdown(f"<div class='cell-revealed' style='background:rgba(255,255,255,0.1); color:rgba(255,255,255,0.5);'>{flag_disp}</div>", unsafe_allow_html=True)
                    else:
                        # 正常按钮
                        # 利用 label 显示旗帜
                        btn_label = "🚩" if is_flag else ""
                        
                        if st.button(btn_label, key=key):
                            if st.session_state.flag:
                                if is_flag: flg.remove((r,c))
                                else: flg.add((r,c))
                                st.rerun()
                            elif not is_flag:
                                if not reveal(board, vis, flg, r, c):
                                    st.session_state.lost = True
                                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True) # End glass-card
