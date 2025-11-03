const root = document.getElementById("root");

function send(action) {
  Streamlit.setComponentValue({ action });
}

function renderTile(props) {
  root.innerHTML = "";

  const tile = document.createElement("div");
  tile.className = "tile";

  if (props.flagged) {
    tile.textContent = "🚩";
    tile.classList.add("flag");
  } else {
    tile.textContent = "■";
  }

  tile.oncontextmenu = (e) => {
    e.preventDefault();
    if (props.flagged) send("unflag");
    else send("flag");
  };

  tile.onclick = () => {
    send("reveal");
  };

  root.appendChild(tile);
}

Streamlit.events.addEventListener("render", (event) => {
  const { r, c, flagged } = event.detail.args;
  renderTile({ r, c, flagged });
});

Streamlit.setComponentReady();
Streamlit.setFrameHeight(40);