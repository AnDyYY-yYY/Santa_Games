const boardEl = document.getElementById("board");
const statusEl = document.getElementById("status");
const messageEl = document.getElementById("message");
const historyEl = document.getElementById("history");
const movesLeftEl = document.getElementById("moves-left");
const bagCountEl = document.getElementById("bag-count");
const deliveredCountEl = document.getElementById("delivered-count");
const celebrateBtn = document.getElementById("celebrate");

const directionButtons = document.querySelectorAll("[data-direction]");
directionButtons.forEach((btn) =>
  btn.addEventListener("click", () => handleMove(btn.dataset.direction))
);

document.getElementById("look").addEventListener("click", fetchState);
document.getElementById("new-game").addEventListener("click", () => startNewGame());
celebrateBtn.addEventListener("click", () => celebrateBtn.classList.toggle("wiggle"));

document.addEventListener("keydown", (event) => {
  const mapping = {
    ArrowUp: "n",
    ArrowDown: "s",
    ArrowLeft: "w",
    ArrowRight: "e",
    w: "n",
    s: "s",
    a: "w",
    d: "e",
  };
  const dir = mapping[event.key];
  if (dir) {
    event.preventDefault();
    handleMove(dir);
  }
});

async function fetchState() {
  const res = await fetch("/api/state");
  const payload = await res.json();
  render(payload);
}

async function startNewGame() {
  const res = await fetch("/api/new", { method: "POST" });
  const payload = await res.json();
  render(payload, true);
}

async function handleMove(direction) {
  const res = await fetch("/api/move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ direction }),
  });
  const payload = await res.json();
  render(payload, true);
}

function render(payload, addHistory = false) {
  const {
    board,
    status,
    message,
    history,
    bag,
    delivered,
    winsAt,
    remainingMoves,
    isWon,
    availableMoves = [],
  } = payload;

  // Grid
  boardEl.style.gridTemplateColumns = `repeat(${board[0].length}, 1fr)`;
  boardEl.innerHTML = "";
  board.flat().forEach((cellType) => {
    const cell = document.createElement("div");
    cell.className = `cell ${cellType}`;
    boardEl.appendChild(cell);
  });

  // Stats
  movesLeftEl.textContent = remainingMoves;
  bagCountEl.textContent = bag;
  deliveredCountEl.textContent = `${delivered}/${winsAt}`;

  // Messages
  statusEl.textContent = status;
  messageEl.textContent = message;

  if (addHistory && message) {
    historyEl.insertAdjacentHTML("afterbegin", `<li>${message}</li>`);
  } else if (!historyEl.children.length) {
    history.slice().reverse().forEach((entry) => {
      historyEl.insertAdjacentHTML("afterbegin", `<li>${entry}</li>`);
    });
  }

  // Celebrate
  celebrateBtn.setAttribute("aria-disabled", isWon ? "false" : "true");
  celebrateBtn.textContent = isWon ? "🎉 You won! Play again?" : "🎉 Victory dance";

  // Disable impossible moves
  directionButtons.forEach((btn) => {
    const dir = btn.dataset.direction;
    btn.disabled = !availableMoves.includes(dir);
  });
}

fetchState().catch((err) => {
  console.error("Failed to load state", err);
  messageEl.textContent = "Unable to load the board. Please refresh.";
});
