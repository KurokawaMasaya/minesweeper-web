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

    st.markdown("<div class='board'>", unsafe_allow_html=True)
    for r in range(len(board)):
        st.markdown("<div class='row'>", unsafe_allow_html=True)
        cols = st.columns(len(board[0]))
        for c in range(len(board[0])):
            if (r,c) in vis or st.session_state.lost:
                val = board[r][c]
                txt = "💣" if val==-1 else (" " if val==0 else str(val))
                color = {
                    "1":"#1a4de8","2":"#0d7b32","3":"#d62828","4":"#3b0ca3",
                    "5":"#7f0909","6":"#087e8b","7":"#111","8":"#666"
                }.get(str(val),"#000")
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
        st.error("💥 Boom! Game Over — Full board revealed.")
        if st.button("Play Again"):
            st.session_state.running=False
            st.rerun()

    elif len(vis) == R*C - sum(r.count(-1) for r in board):
        st.success("🎉 You Win! — Full board revealed.")
        if st.button("Play Again"):
            st.session_state.running=False
            st.rerun()
