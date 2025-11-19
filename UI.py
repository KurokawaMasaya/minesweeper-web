import streamlit as st
import random

# 页面配置
st.set_page_config(page_title="Minesweeper Redesigned", layout="centered", page_icon="💣")

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

# ================= 🎨 按键专项设计 (CSS) =================

st.markdown("""
<style>
    /* 全局深色背景 */
    .stApp {
        background-color: #202124;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    h1 { color: #e8eaed; text-align: center; font-weight: 300; letter-spacing: 2px; margin-bottom: 20px; }

    /* --- 1. 游戏格子按键 (核心设计) --- */
    
    /* 容器调整，消除间隙 */
    div[data-testid="column"] {
        width: 40px !important; flex: unset !important; padding: 0px !important; margin: 1px !important;
    }
    
    /* 这里的 button 选择器非常关键，针对 Streamlit 的按钮进行 3D 化 */
    div.stButton > button {
        width: 40px !important;
        height: 40px !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        transition: all 0.1s ease !important;
        padding: 0 !important;
        line-height: 1 !important;
    }

    /* 未被按下的状态：3D 凸起效果 */
    .tile-hidden button {
        background: #a0a0a0 !important; /* 经典灰 */
        border-top: 3px solid #e0e0e0 !important; /* 亮边 */
        border-left: 3px solid #e0e0e0 !important;
        border-bottom: 3px solid #505050 !important; /* 暗边 */
        border-right: 3px solid #505050 !important;
        color: transparent !important;
    }
    
    .tile-hidden button:hover {
        background: #b0b0b0 !important;
        transform: translateY(-1px);
    }
    
    .tile-hidden button:active {
        background: #909090 !important;
        border: 1px solid #505050 !important; /* 按下时边框变细，模拟凹陷 */
        transform: translateY(1px);
    }

    /* --- 2. 功能控制区按键 --- */
    
    .control-btn-container {
        display: flex; justify-content: center; gap: 15px; margin-bottom: 20px;
        background: #2d2e31; padding: 15px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    /* 覆盖 Streamlit 原生 Primary 按钮样式 */
    button[kind="primary"] {
        background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%) !important;
        border: none !important;
        box-shadow: 0 4px 0 #2e7d32 !important; /* 底部立体阴影 */
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        transform: translateY(0);
        transition: all 0.1s !important;
    }
    
    button[kind="primary"]:active {
        transform: translateY(4px) !important; /* 按下时位移，吃掉阴影 */
        box-shadow: 0 0 0 #2e7d32 !important;
    }

    /* 覆盖 Secondary 按钮 (用于 Restart/Mode) */
    button[kind="secondary"] {
        background: #3c4043 !important;
        color: #e8eaed !important;
        border: 1px solid #5f6368 !important;
        box-shadow: 0 4px 0 #202124 !important;
    }
    button[kind="secondary"]:active {
        transform: translateY(4px) !important;
        box-shadow: none !important;
    }

    /* --- 3. 已揭开的格子样式 --- */
    .revealed {
        width: 40px; height: 40px;
        background-color: #bzbzbz;
        border: 1px solid #707070;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Courier New', monospace;
        font-weight: 900;
        font-size: 20px;
        box-shadow: inset 2px 2px 5px rgba(0,0,0,0.2); /* 内阴影，表示凹陷 */
        color: #333;
        background: #dcdcdc;
    }
    
    /* 数字颜色 */
    .val-1 { color: #1976D2; } .val-2 { color: #388E3C; } .val-3 { color: #D32F2F; }
    .val-4 { color: #7B1FA2; } .val-5 { color: #FF8F00; }
    .mine { background: #e53935 !important; color: white !important; border: 2px solid #b71c1c !important; animation: shake 0.5s; }
    
    /* 插旗标记 */
    .flag-mark { 
        font-size: 20px; position: absolute; z-index: 10; pointer-events: none;
        margin-top: -35px; margin-left: 10px; text-shadow: 1px 1px 0 #fff;
    }
    
    @keyframes shake { 0% { transform: translateX(0); } 25% { transform: translateX(5px); } 75% { transform: translateX(-5px); } 100% { transform: translateX(0); } }

    div[data-testid="stHorizontalBlock"] { justify-content: center; }

</style>
""", unsafe_allow_html=True)

# ================= 界面构建 =================

st.title("Minesweeper")

# --- 顶部控制面板 (始终显示) ---
if st.session_state.running:
    col_score, col_mode, col_reset = st.columns([1.5, 1.5, 1])
    
    with col_score:
        # 显示剩余雷数
        left = st.session_state.mines - len(st.session_state.flags)
        st.metric("Mines Left", f"{left}", delta_color="inverse")
        
    with col_mode:
        # 模式切换按钮：设计成明显的开关
        mode_text = "🚩 FLAGGING" if st.session_state.flag else "⛏️ DIGGING"
        btn_type = "primary" if st.session_state.flag else "secondary"
        # 使用 help 参数增加提示
        if st.button(mode_text, key="mode_switch", type=btn_type, use_container_width=True, help="Click to toggle between Flag and Dig modes"):
            st.session_state.flag = not st.session_state.flag
            st.rerun()
            
    with col_reset:
        # 重置按钮
        if st.button("🔄 Reset", key="reset_game", type="secondary", use_container_width=True):
            st.session_state.running = False
            st.rerun()
    
    st.write("---")

# --- 游戏主逻辑 ---

if not st.session_state.running:
    # 开始菜单
    st.markdown("<div style='text-align:center; padding: 20px; background:#2d2e31; border-radius:10px;'>", unsafe_allow_html=True)
    st.markdown("### New Game")
    
    c1, c2 = st.columns(2)
    with c1:
        diff = st.select_slider("Difficulty", options=["Easy", "Medium", "Hard"])
    with c2:
        size_map = {"Small": (8,8), "Medium": (10,10), "Large": (12,12)}
        size_label = st.selectbox("Grid Size", list(size_map.keys()), index=1)
    
    R, C = size_map[size_label]
    factor = {"Easy":0.1, "Medium":0.15, "Hard":0.2}[diff]
    M = max(1, int(R*C*factor))
    
    st.write("")
    # 大号开始按钮
    if st.button(f"▶ START ({R}x{C})", type="primary", use_container_width=True):
        start(R,C,M)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # 游戏进行中
    # 状态提示
    if st.session_state.lost:
        st.error("💥 GAME OVER! You hit a mine.")
    elif st.session_state.won:
        st.balloons()
        st.success("🏆 YOU WON! Amazing job!")

    # 网格渲染区
    # 外层容器居中
    st.markdown('<div style="display:flex; justify-content:center;"><div>', unsafe_allow_html=True)
    
    board = st.session_state.board
    vis = st.session_state.revealed
    flg = st.session_state.flags
    
    for r in range(st.session_state.rows):
        # 每一行是一个 columns 容器
        cols = st.columns(st.session_state.cols)
        for c in range(st.session_state.cols):
            with cols[c]:
                key = f"btn_{r}_{c}"
                
                # 判定状态
                is_revealed = (r,c) in vis
                is_flagged = (r,c) in flg
                is_mine = board[r][c] == -1
                game_over = st.session_state.lost or st.session_state.won
                
                # 渲染逻辑
                if is_revealed or (game_over and is_mine):
                    # === 状态 A: 已揭开 (显示数字或雷) ===
                    val = board[r][c]
                    if val == -1:
                        # 爆炸的雷
                        st.markdown(f"<div class='revealed mine'>💣</div>", unsafe_allow_html=True)
                    else:
                        # 数字或空
                        txt = str(val) if val > 0 else ""
                        cls = f"val-{val}" if val > 0 else ""
                        st.markdown(f"<div class='revealed {cls}'>{txt}</div>", unsafe_allow_html=True)
                
                else:
                    # === 状态 B: 未揭开 (显示按钮) ===
                    # 利用 CSS class "tile-hidden" 给按钮加 3D 样式
                    st.markdown('<div class="tile-hidden">', unsafe_allow_html=True)
                    
                    # 只有游戏未结束才显示可交互按钮
                    if not game_over:
                        # 注意：Streamlit 的按钮文字不能动态改得太花，所以用 Emoji 辅助
                        # 这里的 button 实际上是透明文字，视觉由 CSS 控制，但插旗时我们可以显示个标记
                        if st.button(key, label="🚩" if is_flagged else " "): 
                            if st.session_state.flag:
                                if is_flagged: flg.remove((r,c))
                                else: flg.add((r,c))
                                st.rerun()
                            elif not is_flagged: # 没插旗才能挖
                                if not reveal(board, vis, flg, r, c):
                                    st.session_state.lost = True
                                st.rerun()
                    else:
                        # 游戏结束，未揭开的格子显示为静止方块
                        st.markdown(f"<div class='revealed' style='background:#ccc;'></div>", unsafe_allow_html=True)
                        
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 如果插了旗，在按钮上方叠加显示一个旗子图标 (增强视觉)
                    if is_flagged and not game_over:
                         # 这里利用 CSS hack 调整位置，确保旗子显示在按钮上
                         pass # 实际上上面的 label="🚩" 已经解决了大部分问题

    st.markdown('</div></div>', unsafe_allow_html=True)
