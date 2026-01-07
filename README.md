# 🧌 Goblin Graph Dungeon

A terminal-based adventure game that turns classic **algorithm concepts** into actual **game mechanics**.

Explore a shifting dungeon, outwit goblins in ritual puzzles, manage your inventory carefully, and escape with ancient sigils — all while graph theory quietly runs the world behind the scenes.

This project started as a learning experiment and became a playable game.

---

## 🎮 Gameplay Overview

You play as an adventurer entering **the Goblin King’s Maze**.

- The dungeon is made of **rooms connected as a graph**
- Each run generates a **new dungeon layout**
- Rooms trigger events:
  - 🪙 **Loot Caches** (knapsack-style inventory challenge)
  - 🧙 **Goblin Rituals** (stone-taking games / divide-and-conquer puzzles)
  - ⚔️ **Ambushes** (combat encounters)
- The dungeon can **shift and change** after rituals
- Your goal: **collect 3 Sigils** and reach the Exit Gate

If your health reaches zero — the dungeon claims another victim.

---

## 🧠 Algorithms Used (Hidden in Plain Sight)

This game is built to *demonstrate algorithms through play*, not lectures.

| Concept | How it appears in-game |
|------|-------------------------|
| Graphs (Adjacency Lists) | Dungeon rooms and tunnels |
| BFS / Reachability | Ensuring the exit is never unreachable |
| Dynamic Graph Mutation | Tunnels opening and collapsing |
| Knapsack | Loot rooms with weight limits and penalties |
| Divide & Conquer / Game Theory | Goblin stone ritual puzzles |
| Modular Arithmetic (mod 4) | Ritual hints and optimal strategies |

You can play the game without knowing any of this — but if you *do* know it, you’ll smile.

---

## 🏘️ Game Structure (Option B Design)

- **Village (Hub)**
  - Shop
  - Inventory management
  - Save / Load
  - Enter the dungeon

- **Dungeon (Graph-Based Exploration)**
  - Move room to room
  - Events trigger once per room
  - Dungeon may shift after rituals
  - Return to village at any time

This structure keeps the game forgiving, replayable, and easy to extend.

---

## ▶️ How to Run

### Requirements
- Python **3.9+**
- Terminal / Command Prompt

No external libraries required.

### Run the game
```bash
python goblin_graph_dungeon_v1.py
````

The game will:

* ask for your name
* allow you to start a new game or load a save
* automatically create a save file (`goblin_save.json`)

---

## 💾 Saving & Loading

* The game autosaves when quitting
* Manual save is available in the village
* Save file includes:

  * player stats
  * inventory
  * dungeon state
  * current room

Delete `goblin_save.json` to reset progress.

---

## 🧩 Goblin Rituals (Stone Duels)

Ritual rooms challenge you with **two-pile stone games**:

### Game 1

* Allowed moves:

  * (1, 0)
  * (0, 1)
  * (1, 1)
* Last move wins

### Game 2

* Remove **1–3 stones total** per turn
* Stones can be split across piles
* Hint shown:

  * total stones **mod 4**

These puzzles are based on classic game-theory strategies.

---

## 🪙 Loot Caches (Knapsack Challenge)

Loot rooms present valuable items with:

* weights
* values

Your pack has limited capacity.

* Pick wisely → keep everything
* Get greedy → drop items while fleeing and take damage

Pack capacity can be upgraded in the shop.

---

## 🛠️ Project Status

**Version:** V1
**State:** Stable / Playable

Planned (future ideas):

* More room types
* Map items (distance to exit)
* Boss encounters
* Visual UI (Tkinter or MAUI version)
* GitHub issues for student extensions

---

## 🎓 Educational Use

This project is intentionally:

* readable
* hackable
* easy to extend

Feel free to:

* fork it
* add new puzzles
* replace events
* use it as a teaching example

If you’re a student:
Try adding a new room type using a different algorithm.

---

## 📜 License

This project is shared for **educational and learning purposes**.
Use it, learn from it, and build something cool.

---

## 🙌 Credits

Created as a learning project combining:

* algorithms
* game design
* terminal storytelling

Inspired by curiosity, goblins, and stubborn persistence.
