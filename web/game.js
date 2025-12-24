const MAP = [
  "##############",
  "#S..G..C..H..#",
  "#..##..C..#..#",
  "#..#....#....#",
  "#..G..I..H...#",
  "#..#..C..#..G#",
  "#..H....#....#",
  "#..#..I..C...#",
  "##############",
];

const DELTAS = {
  n: [-1, 0],
  s: [1, 0],
  w: [0, -1],
  e: [0, 1],
};

const TILE = {
  EMPTY: ".",
  WALL: "#",
  SANTA: "S",
  GIFT: "G",
  HOUSE: "H",
  COCOA: "C",
  ICE: "I",
};

const SYMBOLS = {
  [TILE.EMPTY]: "",
  [TILE.WALL]: "⬛",
  [TILE.GIFT]: "🎁",
  [TILE.HOUSE]: "🏠",
  [TILE.COCOA]: "☕",
  [TILE.ICE]: "🧊",
};

class SantaWebGame {
  constructor(map) {
    this.originalMap = map.map((row) => row.split(""));
    this.width = this.originalMap[0].length;
    this.height = this.originalMap.length;
    this.maxMoves = 45;
    this.reset();
  }

  reset() {
    this.board = this.originalMap.map((row) => [...row]);
    this.santa = this.findSanta();
    this.movesLeft = this.maxMoves;
    this.bag = 0;
    this.delivered = 0;
    this.cheer = 0;
    this.totalGifts = this.countTiles(TILE.GIFT);
    this.houses = this.collectCoords(TILE.HOUSE);
    this.log = [];
    this.over = false;
    this.status = "Collect gifts and deliver them to every house.";
    this.pushLog("New run started. Deliver every gift before dawn!");
  }

  findSanta() {
    for (let r = 0; r < this.height; r++) {
      for (let c = 0; c < this.width; c++) {
        if (this.board[r][c] === TILE.SANTA) {
          return { r, c };
        }
      }
    }
    throw new Error("Map is missing Santa start (S).");
  }

  countTiles(tile) {
    let count = 0;
    this.board.forEach((row) => row.forEach((cell) => (count += cell === tile ? 1 : 0)));
    return count;
  }

  collectCoords(tile) {
    const coords = new Set();
    this.board.forEach((row, r) =>
      row.forEach((cell, c) => {
        if (cell === tile) coords.add(`${r},${c}`);
      }),
    );
    return coords;
  }

  withinBounds(r, c) {
    return r >= 0 && c >= 0 && r < this.height && c < this.width;
  }

  isWalkable(r, c) {
    if (!this.withinBounds(r, c)) return false;
    return this.board[r][c] !== TILE.WALL;
  }

  move(dir) {
    if (this.over) return;
    const delta = DELTAS[dir];
    if (!delta) return;

    this.stepSanta(delta);

    if (this.over) return;
    this.checkWinLose();
  }

  stepSanta(delta) {
    const target = { r: this.santa.r + delta[0], c: this.santa.c + delta[1] };
    if (!this.isWalkable(target.r, target.c)) {
      this.toast("A snowbank blocks the path.");
      this.pushLog("Bumped into a snowbank.");
      return;
    }

    this.santa = target;
    this.movesLeft = Math.max(this.movesLeft - 1, 0);

    const tile = this.board[target.r][target.c];
    this.handleTile(tile, delta);
    this.handleHouseDelivery();
  }

  handleTile(tile, delta) {
    if (tile === TILE.GIFT) {
      this.board[this.santa.r][this.santa.c] = TILE.EMPTY;
      this.bag += 1;
      this.pushLog("🎁 Picked up a gift.");
      this.cheer += 2;
    }

    if (tile === TILE.COCOA) {
      this.board[this.santa.r][this.santa.c] = TILE.EMPTY;
      this.movesLeft = Math.min(this.movesLeft + 4, this.maxMoves);
      this.cheer += 6;
      this.pushLog("☕ Warm cocoa! Extra energy (+4 moves, +6 cheer).");
      this.toast("Cocoa boost! +4 moves");
    }

    if (tile === TILE.ICE) {
      const slideTarget = { r: this.santa.r + delta[0], c: this.santa.c + delta[1] };
      if (this.isWalkable(slideTarget.r, slideTarget.c) && this.movesLeft > 0) {
        this.movesLeft = Math.max(this.movesLeft - 1, 0);
        this.santa = slideTarget;
        this.pushLog("🧊 You slide across the ice!");
        const slideTile = this.board[slideTarget.r][slideTarget.c];
        if (slideTile === TILE.GIFT) {
          this.board[slideTarget.r][slideTarget.c] = TILE.EMPTY;
          this.bag += 1;
          this.cheer += 2;
          this.pushLog("🎁 Slid into a gift!");
        }
        if (slideTile === TILE.COCOA) {
          this.board[slideTarget.r][slideTarget.c] = TILE.EMPTY;
          this.movesLeft = Math.min(this.movesLeft + 4, this.maxMoves);
          this.cheer += 6;
          this.pushLog("☕ Cocoa on ice! +4 moves, +6 cheer.");
        }
      }
    }
  }

  handleHouseDelivery() {
    const coord = `${this.santa.r},${this.santa.c}`;
    if (this.houses.has(coord) && this.bag > 0) {
      const deliveredNow = this.bag;
      this.delivered += deliveredNow;
      this.cheer += deliveredNow * 8;
      this.bag = 0;
      this.pushLog(`🏠 Delivered ${deliveredNow} gift(s)! Holiday cheer rising.`);
      this.toast("Delivery complete!");
    }
  }

  checkWinLose() {
    if (this.delivered >= this.totalGifts) {
      this.over = true;
      this.status = "Victory! Every house has its presents. 🎄";
      this.pushLog(this.status);
      this.toast("Victory!");
      return;
    }
    if (this.movesLeft <= 0) {
      this.over = true;
      this.status = "Time's up! Dawn arrived before the deliveries were done.";
      this.pushLog(this.status);
      this.toast("Dawn breaks!");
    }
  }

  pushLog(message) {
    const timestamp = new Date().toLocaleTimeString();
    this.log.unshift({ timestamp, message });
    if (this.log.length > 40) this.log.pop();
  }

  toast(text) {
    const el = document.getElementById("toast");
    if (!el) return;
    el.textContent = text;
    el.classList.add("show");
    setTimeout(() => el.classList.remove("show"), 1800);
  }
}

class SantaUI {
  constructor() {
    this.game = new SantaWebGame(MAP);
    this.boardEl = document.getElementById("board");
    this.logEl = document.getElementById("log");
    this.bindControls();
    this.render();
  }

  bindControls() {
    document.querySelectorAll("[data-dir]").forEach((btn) => {
      btn.addEventListener("click", () => {
        this.game.move(btn.dataset.dir);
        this.render();
      });
    });

    document.getElementById("restart").addEventListener("click", () => {
      this.game.reset();
      this.render();
    });

    document.getElementById("clear-log").addEventListener("click", () => {
      this.game.log = [];
      this.renderLog();
    });

    window.addEventListener("keydown", (e) => {
      const key = e.key.toLowerCase();
      const map = { arrowup: "n", w: "n", arrowdown: "s", s: "s", arrowleft: "w", a: "w", arrowright: "e", d: "e" };
      if (map[key]) {
        e.preventDefault();
        this.game.move(map[key]);
        this.render();
      }
    });
  }

  render() {
    this.renderBoard();
    this.renderStatus();
    this.renderLog();
  }

  renderBoard() {
    const { board, santa } = this.game;
    this.boardEl.style.gridTemplateColumns = `repeat(${this.game.width}, minmax(26px, 1fr))`;
    this.boardEl.innerHTML = "";

    for (let r = 0; r < this.game.height; r++) {
      for (let c = 0; c < this.game.width; c++) {
        const tile = board[r][c];
        const cell = document.createElement("div");
        cell.classList.add("cell");
        cell.setAttribute("role", "gridcell");
        cell.setAttribute("aria-label", `Row ${r + 1} column ${c + 1}`);

        if (r === santa.r && c === santa.c) {
          cell.textContent = "🎅";
          cell.classList.add("santa");
        } else {
          cell.textContent = SYMBOLS[tile] || "";
          if (tile === TILE.WALL) cell.classList.add("wall");
          if (tile === TILE.GIFT) cell.classList.add("gift");
          if (tile === TILE.HOUSE) cell.classList.add("house");
          if (tile === TILE.COCOA) cell.classList.add("cocoa");
          if (tile === TILE.ICE) cell.classList.add("ice");
        }
        this.boardEl.appendChild(cell);
      }
    }
  }

  renderStatus() {
    document.getElementById("moves-left").textContent = this.game.movesLeft;
    document.getElementById("bag-count").textContent = this.game.bag;
    document.getElementById("delivered-count").textContent = `${this.game.delivered}/${this.game.totalGifts}`;
    document.getElementById("cheer-score").textContent = this.game.cheer;
  }

  renderLog() {
    this.logEl.innerHTML = "";
    this.game.log.forEach((entry) => {
      const li = document.createElement("li");
      const time = document.createElement("time");
      time.textContent = entry.timestamp;
      const text = document.createElement("span");
      text.textContent = entry.message;
      li.appendChild(time);
      li.appendChild(text);
      this.logEl.appendChild(li);
    });
  }
}

document.addEventListener("DOMContentLoaded", () => new SantaUI());
