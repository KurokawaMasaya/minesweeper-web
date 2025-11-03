<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <script src="https://unpkg.com/streamlit-component-lib@1.4.0/dist/index.js"></script>
    <style>
      body { margin: 0; }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script>
      const root = document.getElementById('root');

      function render(args) {
        const r = args.r, c = args.c, flagged = !!args.flagged;
        root.innerHTML = `
          <div id="tile" style="
            width:36px;height:36px;display:flex;align-items:center;justify-content:center;
            user-select:none;cursor:pointer;border:1px solid #e5e7eb;border-radius:6px;
            background:#f8fafc;color:#111827;font-weight:700;font-size:16px;">
            ${flagged ? '🚩' : ''}
          </div>`;
        const tile = root.firstChild;
        tile.addEventListener('click', () => {
          Streamlit.setComponentValue({ action: 'reveal', r, c });
        });
        tile.addEventListener('contextmenu', (e) => {
          e.preventDefault();
          Streamlit.setComponentValue({ action: flagged ? 'unflag' : 'flag', r, c });
        });
        Streamlit.setFrameHeight(40);
      }

      Streamlit.events.addEventListener('render', (event) => {
        render(event.detail.args);
      });

      Streamlit.setComponentReady();
    </script>
  </body>
  </html>

