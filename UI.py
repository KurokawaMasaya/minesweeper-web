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

.board { display:flex; gap:4px; flex-direction:column; margin-top:10px; }
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
  animation: boom .15s linear infinite alternate;
}

@keyframes boom{
  from{ background:#ff4f4f; }
  to{ background:#ffc8c8; }
}

.win-celebration{
  animation: winPulse 0.6s ease-in-out infinite;
  position: relative;
}

@keyframes winPulse{
  0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); }
  50% { transform: scale(1.05); box-shadow: 0 0 20px 10px rgba(46, 204, 113, 0.4); }
}

.lose-shake{
  animation: shake 0.5s ease-in-out;
}

@keyframes shake{
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px) rotate(-2deg); }
  75% { transform: translateX(10px) rotate(2deg); }
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
    board_class = ""
    if won:
        board_class = "win-celebration"
    elif st.session_state.lost:
        board_class = "lose-shake"

    st.markdown(f"<div class='board {board_class}'>", unsafe_allow_html=True)
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
                boom = "bomb-hit" if st.session_state.lost and val==-1 else ""
                cols[c].markdown(
                    f"<div class='tile revealed {boom}' style='color:{color}'>{txt}</div>",
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
        st.markdown("""
        <div style='padding:15px;background:#fee;border:2px solid #f44;border-radius:8px;text-align:center;font-size:20px;font-weight:700;color:#d00;'>
            💥 BOOM! Game Over
        </div>
        """, unsafe_allow_html=True)
        if st.button("Play Again"):
            st.session_state.running=False
            st.rerun()

    elif won:
        st.markdown("""
        <div id='win-message' style='padding:15px;background:#efe;border:2px solid #4f4;border-radius:8px;text-align:center;font-size:24px;font-weight:700;color:#060;animation:winPulse 0.6s ease-in-out infinite;'>
            🎉 YOU WIN! 🎉
        </div>
        <script>
        // Confetti celebration effect
        const colors = ['#ffd700','#ff6b6b','#4ecdc4','#45b7d1','#f7b731','#5f27cd'];
        for(let i=0; i<60; i++){
            const piece = document.createElement('div');
            piece.className = 'confetti-piece';
            const left = Math.random()*100;
            const drift = (Math.random()-0.5)*200;
            piece.style.left = left + '%';
            piece.style.background = colors[Math.floor(Math.random()*colors.length)];
            piece.style.animationDelay = Math.random()*2 + 's';
            piece.style.animationDuration = (2 + Math.random()*2) + 's';
            piece.style.setProperty('--drift', drift/100);
            piece.style.top = '-10px';
            document.body.appendChild(piece);
            setTimeout(() => piece.remove(), 5000);
        }
        </script>
        """, unsafe_allow_html=True)
        if st.button("Play Again"):
            st.session_state.running=False
            st.rerun()
