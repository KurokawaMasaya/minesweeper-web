import streamlit as st
import random

st.set_page_config(page_title="Minesweeper", layout="centered")

# ============== Init ==============
if "running" not in st.session_state: st.session_state.running = False
if "board" not in st.session_state: st.session_state.board = None
if "revealed" not in st.session_state: st.session_state.revealed = set()
if "flags" not in st.session_state: st.session_state.flags = set()
if "lost" not in st.session_state: st.session_state.lost = False

# ============== CSS ==============
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">

<style>
html,body,.stApp{
  background: #f2f6ff;
  font-family: -apple-system, BlinkMacSystemFont,"Segoe UI",sans-serif;
  color: #0b1a33 !important;
}

/* Make all text dark and readable */
h1, h2, h3, h4, h5, h6, p, label, div, span, .stText, .stMarkdown {
  color: #0b1a33 !important;
}

/* Slider labels */
.stSlider label {
  color: #0b1a33 !important;
  font-weight: 600;
}

/* Selectbox labels */
.stSelectbox label {
  color: #0b1a33 !important;
  font-weight: 600;
}

/* Regular text */
.stText {
  color: #0b1a33 !important;
}

/* Write outputs */
.stWrite {
  color: #0b1a33 !important;
}

/* Buttons - make text white on dark background */
button, .stButton > button {
  color: #ffffff !important;
  background-color: #2563eb !important;
  border-color: #1e40af !important;
}

button:hover, .stButton > button:hover {
  background-color: #1d4ed8 !important;
  color: #ffffff !important;
}

/* Selectbox - make text dark and readable */
.stSelectbox > div > div,
.stSelectbox > div > div > div,
[data-baseweb="select"] > div,
[data-baseweb="select"] > div > div {
  background-color: #ffffff !important;
  color: #0b1a33 !important;
  border: 1px solid #b8c3d9 !important;
}

.stSelectbox label,
[data-baseweb="select"] label {
  color: #0b1a33 !important;
  font-weight: 600 !important;
}

[data-baseweb="select"] [role="option"] {
  background-color: #ffffff !important;
  color: #0b1a33 !important;
}

.board { 
  display:flex; 
  gap:4px; 
  flex-direction:column; 
  margin-top:10px; 
  padding:8px;
  border-radius:8px;
  transition: all 0.3s ease;
}
.row { display:flex; gap:4px; }

.tile{
  width:34px; height:34px;
  display:flex; align-items:center; justify-content:center;
  border:1px solid #b8c3d9;
  border-radius:6px; cursor:pointer; user-select:none;
  font-family:'VT323',monospace; font-size:22px; font-weight:700;
  background:#e7efff; color:#0b1a33;
  transition: all .15s ease;
}
.tile:hover{ transform:scale(1.1); }

.tile.revealed{
  background:white !important; 
  border-color:#a9b6d4;
  transform:scale(1) !important;
}

.bomb-hit{
  animation: boom 0.2s linear infinite, bombPulse 1s ease-out infinite !important;
  z-index: 10;
}

@keyframes boom{
  0% { background:#ff0000 !important; transform: scale(1) rotate(0deg); }
  25% { background:#ff6b6b !important; transform: scale(1.4) rotate(90deg); }
  50% { background:#ff0000 !important; transform: scale(1.5) rotate(180deg); }
  75% { background:#ffcccc !important; transform: scale(1.4) rotate(270deg); }
  100% { background:#ff0000 !important; transform: scale(1) rotate(360deg); }
}

@keyframes bombPulse{
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.9), 0 0 0 0 rgba(255, 100, 100, 0.7); }
  50% { box-shadow: 0 0 30px 15px rgba(255, 0, 0, 0.8), 0 0 50px 25px rgba(255, 100, 100, 0.6); }
}

.win-celebration{
  animation: winPulse 0.8s ease-in-out infinite, winGlow 1.5s ease-in-out infinite !important;
  position: relative;
}

@keyframes winPulse{
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.12); }
}

@keyframes winGlow{
  0%, 100% { 
    box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7), 0 0 0 0 rgba(255, 215, 0, 0.5);
    border: 3px solid rgba(46, 204, 113, 0.3);
  }
  50% { 
    box-shadow: 0 0 40px 20px rgba(46, 204, 113, 0.7), 0 0 60px 30px rgba(255, 215, 0, 0.5);
    border: 3px solid rgba(46, 204, 113, 0.8);
  }
}

.lose-shake{
  animation: shake 0.8s ease-in-out, explode 1s ease-out !important;
  border: 3px solid #ff0000;
}

@keyframes shake{
  0%, 100% { transform: translateX(0) rotate(0deg); }
  10% { transform: translateX(-15px) rotate(-3deg); }
  20% { transform: translateX(15px) rotate(3deg); }
  30% { transform: translateX(-12px) rotate(-2deg); }
  40% { transform: translateX(12px) rotate(2deg); }
  50% { transform: translateX(-8px) rotate(-1deg); }
  60% { transform: translateX(8px) rotate(1deg); }
  70% { transform: translateX(-5px) rotate(0deg); }
  80% { transform: translateX(5px) rotate(0deg); }
}

@keyframes explode{
  0% { filter: brightness(1); }
  50% { filter: brightness(1.5) contrast(1.2); }
  100% { filter: brightness(1); }
}

.confetti{
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 9999;
}

.confetti-piece{
  position: fixed; width: 8px; height: 8px; border-radius: 50%;
  animation: confettiFall 3s linear forwards;
  z-index: 9999;
}

@keyframes confettiFall{
  0% { transform: translateY(0) rotate(0deg); opacity: 1; }
  100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
}
</style>
""", unsafe_allow_html=True)

# ============== Core Logic ==============
def neighbors(r,c,R,C):
    for dr in (-1,0,1):
        for dc in (-1,0,1):
            if dr==0 and dc==0: continue
            rr,cc=r+dr,c+dc
            if 0<=rr<R and 0<=cc<C: yield rr,cc

def init_board(R,C,M):
    board=[[0]*C for _ in range(R)]
    mines=set(random.sample([(r,c) for r in range(R) for c in range(C)],M))
    for r,c in mines: board[r][c] = -1
    for r,c in mines:
        for nr,nc in neighbors(r,c,R,C):
            if board[nr][nc]!=-1: board[nr][nc] +=1
    return board

def flood(r,c,board,vis):
    stack=[(r,c)]
    while stack:
        x,y=stack.pop()
        if (x,y) in vis: continue
        vis.add((x,y))
        if board[x][y]==0:
            for nx,ny in neighbors(x,y,len(board),len(board[0])):
                if (nx,ny) not in vis: stack.append((nx,ny))

def reveal(r,c):
    board=st.session_state.board
    vis=st.session_state.revealed
    flags=st.session_state.flags

    if (r,c) in flags: return

    if board[r][c]==-1:
        st.session_state.lost=True
        st.session_state.running=False
        return

    if board[r][c]==0:
        flood(r,c,board,vis)
    else:
        vis.add((r,c))

# ============== UI ==============
st.title("✨ Minesweeper (Animated Edition)")

if not st.session_state.running:
    R = st.slider("Rows",5,20,10)
    C = st.slider("Cols",5,20,10)
    diff = st.selectbox("Difficulty",["Easy","Medium","Hard"])
    M = int(R*C*{"Easy":0.12,"Medium":0.18,"Hard":0.26}[diff])

    if st.button("Start Game 🎮"):
        st.session_state.board=init_board(R,C,M)
        st.session_state.revealed=set()
        st.session_state.flags=set()
        st.session_state.running=True
        st.session_state.lost=False
        st.rerun()

else:
    board = st.session_state.board
    vis   = st.session_state.revealed
    flags = st.session_state.flags

    st.write(f"Flags: {len(flags)}/{sum(r.count(-1) for r in board)}")

    # Check win condition
    won = len(vis) == len(board) * len(board[0]) - sum(r.count(-1) for r in board)

    st.markdown("<div class='board'>", unsafe_allow_html=True)
    for r in range(len(board)):
        st.markdown("<div class='row'>", unsafe_allow_html=True)
        cols = st.columns(len(board[0]))
        for c in range(len(board[0])):
            if (r,c) in vis or st.session_state.lost:
                val = board[r][c]
                txt = "💣" if val==-1 else (" " if val==0 else str(val))
                color = {
                    "1":"#0066ff","2":"#00cc44","3":"#ff3333","4":"#7b00ff",
                    "5":"#ff6600","6":"#00ffff","7":"#000000","8":"#888888"
                }.get(str(val),"#333333")
                cols[c].markdown(
                    f"<div class='tile revealed' style='color:{color}'>{txt}</div>",
                    unsafe_allow_html=True
                )
            else:
                label = "🚩" if (r,c) in flags else ""
                click = cols[c].button(label or " ", key=f"{r}-{c}")
                if click:
                    if st.session_state.flag_mode:
                        if (r,c) in flags: flags.remove((r,c))
                        else: flags.add((r,c))
                    else:
                        reveal(r,c)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.flag_mode = st.checkbox("🚩 Flag Mode (Shift+Click supported)")

    if st.session_state.lost:
        st.error("💥 BOOM! Game Over")
        if st.button("Play Again"):
            st.session_state.running=False
            st.rerun()

    elif won:
        st.success("🎉 YOU WIN!")
        if st.button("Play Again"):
            st.session_state.running=False
            st.rerun()
