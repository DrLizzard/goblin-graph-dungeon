# goblin_graph_dungeon_v1.py - J.Booysen
# Terminal hub + graph dungeon + knapsack loot + stone duel ritual
# This project is shared for educational and learning purposes.
# Use it, learn from it, and build something cool.
import json
import math
import random
import sys
import time
from pathlib import Path
from collections import deque

SAVEFILE = "goblin_save.json"

TITLE = r"""
   ____       _     _ _        ____                 _     
  / ___| ___ | |__ | (_)_ __  / ___|_ __ __ _ _ __ | |__  
 | |  _ / _ \| '_ \| | | '_ \| |  _| '__/ _` | '_ \| '_ \ 
 | |_| | (_) | |_) | | | | | | |_| | | | (_| | |_) | | | |
  \____|\___/|_.__/|_|_|_| |_|\____|_|  \__,_| .__/|_| |_|
                                             |_|          
"""

SHOP_ART = r"""
   ____  _                 _     
  / ___|| |_ _ __ ___  ___| |__  
  \___ \| __| '__/ _ \/ __| '_ \ 
   ___) | |_| | |  __/ (__| | | |
  |____/ \__|_|  \___|\___|_| |_|
"""

ENEMY_ART = r"""
      (    )
     ((((()))
     |o\ /o)|
     ( (  _')
      (._.  /\__
     ,\___,/ '  ')
 '.,_/   /_   /
    __.-'   __.)
"""

# ----------------------------
# UI helpers (kept vibe)
# ----------------------------
def slow_print(text: str, delay: float = 0.02, end: str = "\n"):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end)
    sys.stdout.flush()

def divider():
    print("\n" + "-" * 60 + "\n")

def pause(seconds: float = 0.6):
    time.sleep(seconds)

# ----------------------------
# Player state
# ----------------------------
player = {
    "name": "",
    "health": 100,
    "gold": 50,
    "inventory": [],     # strings
    "pack_capacity": 5,  # knapsack capacity (weight limit)
    "sigils": 0,         # collected sigils (goal is 3)
}

# ----------------------------
# Save / Load
# ----------------------------
def save_game(state, filename=SAVEFILE):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print(f"[Game saved to {filename}]")
    except Exception as e:
        print("[Failed to save game:]", e)

def load_game(filename=SAVEFILE):
    if not Path(filename).is_file():
        print("[No save file found.]")
        return None
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "player" not in data:
            print("[Save file looks corrupt.]")
            return None
        print(f"[Loaded game from {filename}]")
        return data
    except Exception as e:
        print("[Failed to load game:]", e)
        return None

# ----------------------------
# Combat (number battle vibe)
# ----------------------------
def number_battle(difficulty: int):
    divisor = {1: 30, 2: 50, 3: 100}.get(difficulty, 30)
    secret = random.randint(1, divisor)
    attempts = 0

    slow_print(f"An enemy challenges you! Guess the number between 1 and {divisor}.")
    while True:
        attempts += 1
        try:
            guess = int(input("Your guess: ").strip())
        except ValueError:
            slow_print("Please enter a valid integer.")
            attempts -= 1
            continue

        if guess < secret:
            slow_print("Too low!")
        elif guess > secret:
            slow_print("Too high!")
        else:
            slow_print("You hit the mark! The foe recoils.")
            return {"result": "win", "attempts": attempts, "secret": secret}

        damage = random.randint(5 + difficulty * 2, 12 + difficulty * 3)
        player["health"] -= damage
        slow_print(f"The enemy strikes you for {damage} damage! (HP: {player['health']})")

        if player["health"] <= 0:
            slow_print("\nYOU FALL. THE DUNGEON CLAIMS ANOTHER.\n")
            return {"result": "death", "attempts": attempts, "secret": secret}

# ----------------------------
# Knapsack loot event (based on your knapsack room)
# ----------------------------
ITEM_POOL = [
    ("Rusty Coins", 1, 5),
    ("Silver Ring", 1, 12),
    ("Small Gem", 1, 18),
    ("Gold Idol", 4, 60),
    ("Ancient Tome", 2, 25),
    ("Iron Dagger", 2, 20),
    ("Jeweled Crown", 3, 45),
    ("Bone Charm", 1, 10),
    ("Knight Helm", 3, 35),
    ("Cursed Mirror", 2, 30),
]

def generate_room_loot(count: int = 6):
    return random.sample(ITEM_POOL, k=count)

def show_loot(loot):
    slow_print("\nTorchlight flickers over broken stone. You spot loot:")
    for i, (name, w, v) in enumerate(loot, start=1):
        slow_print(f"  {i}. {name:<14}  weight={w}  value={v}")
    slow_print("")

def parse_choices(inp: str, max_index: int):
    picks = []
    for part in inp.replace(",", " ").split():
        if part.isdigit():
            idx = int(part)
            if 1 <= idx <= max_index:
                picks.append(idx)
    # unique preserve order
    seen = set()
    out = []
    for x in picks:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def event_loot_cache():
    divider()
    loot = generate_room_loot()
    show_loot(loot)

    cap = player["pack_capacity"]
    slow_print(f"Your pack can carry up to {cap} weight.")
    slow_print("Pick items by number (e.g. 1 3 5). Press Enter to take nothing.")
    choice = input("> ").strip()

    picks = parse_choices(choice, len(loot))
    taken = [loot[i-1] for i in picks]

    total_w = sum(w for _, w, _ in taken)
    total_v = sum(v for _, _, v in taken)

    slow_print("\nYou tighten the straps...")
    pause()

    if total_w <= cap:
        slow_print(f"You move like a shadow. Pack weight {total_w}/{cap}.")
        slow_print(f"You pocket loot worth {total_v} gold.")
        player["gold"] += total_v
        return

    slow_print(f"Uh oh. Pack weight {total_w}/{cap}. Too heavy.")
    slow_print("Stone groans overhead. Something is coming.")
    pause()

    dropped = []
    while taken and sum(w for _, w, _ in taken) > cap:
        item = random.choice(taken)
        taken.remove(item)
        dropped.append(item)

    kept_w = sum(w for _, w, _ in taken)
    kept_v = sum(v for _, _, v in taken)

    slow_print("You start dumping gear while running...")
    for name, w, v in dropped:
        slow_print(f"  Dropped: {name} (w={w}, v={v})", delay=0.01)

    slow_print(f"\nBreathing hard, you stumble on. Pack weight {kept_w}/{cap}.")
    slow_print(f"You only manage to keep {kept_v} gold worth.")
    player["gold"] += kept_v

    # small penalty for greed
    dmg = random.randint(3, 10)
    player["health"] -= dmg
    slow_print(f"The dungeon bites you for {dmg} damage in the chaos. (HP: {player['health']})")

# ----------------------------
# Stone Duel ritual (terminal port of your rules + goblin strategy)
# ----------------------------
def goblin_move_game1(left, right):
    # Parity strategy:
    # If possible, make the resulting position (even, even) for the player.

    # If one pile is empty, only one legal move exists.
    if left == 0 and right == 0:
        return (0, 0)  # shouldn't be called here, but safe
    if left == 0:
        return (0, 1)
    if right == 0:
        return (1, 0)

    # If exactly one pile is odd, take from that pile to make it even.
    if left % 2 == 1 and right % 2 == 0:
        return (1, 0)
    if left % 2 == 0 and right % 2 == 1:
        return (0, 1)

    # If both are odd, take from both to make both even.
    if left % 2 == 1 and right % 2 == 1:
        return (1, 1)

    # Otherwise both are even already (goblin is in a losing position),
    # so any move is "bad" – pick randomly.
    return random.choice([(1, 0), (0, 1), (1, 1)])

def goblin_move_game2(left, right):
    # mod-4 strategy: remove total stones == (left+right) % 4 when possible, else random legal
    moves = []
    for l in range(0, min(3, left) + 1):
        for r in range(0, min(3 - l, right) + 1):
            if l + r >= 1:
                moves.append((l, r))

    total = left + right
    if total == 0:
        return (0, 0)

    target = total % 4
    if target != 0:
        for l, r in moves:
            if l + r == target:
                return (l, r)
    return random.choice(moves)

def make_even_in_range(x, lo=7, hi=13):
    if x % 2 == 0:
        return x
    # x is odd: try +1 if it stays in range, else -1
    if x < hi:
        return x + 1
    return x - 1

def event_goblin_ritual():
    divider()
    slow_print("A Goblin Shaman draws a circle in ash.")
    slow_print("Two piles of magic stones shimmer on the floor.")
    slow_print("Win the ritual and the dungeon coughs up a Sigil.\n")

    mode = random.choice(["game1", "game2"])  # surprise ritual
    left = random.randint(7, 13)
    right = random.randint(7, 13)

    # OPTION 0: make Game 1 fair sometimes by forcing (even, even)
    if mode == "game1" and random.random() < 0.6: # If you want it even more fair, change 0.5 to 0.7 (70% fair starts)
        left = make_even_in_range(left, 7, 13)
        right = make_even_in_range(right, 7, 13)

    # OPTION 1: make Game 2 fair sometimes by starting on a multiple of 4
    if mode == "game2" and random.random() < 0.5: # If you want it even more fair, change 0.5 to 0.7 (70% fair starts)
        total = left + right
        mod = total % 4
        if mod != 0:
            add = 4 - mod  # 1..3
            # add to a random pile so it doesn't feel patterned
            if random.random() < 0.5:
                left += add
            else:
                right += add

    slow_print(f"Ritual mode: {'Game 1' if mode=='game1' else 'Game 2'}")
    if mode == "game1":
        slow_print("Rules: take (1,0) or (0,1) or (1,1). Last move wins.")
    else:
        slow_print("Rules: take 1–3 stones TOTAL each turn (split across piles). Last move wins.")
        slow_print("Hint: Total stones mod 4 matters...")

    turn = "goblin"  # like your Tkinter version, goblin starts

    while left + right > 0:
        slow_print(f"\nPiles: Left={left}  Right={right}")
        if mode == "game1":
            slow_print(f"Status: Left is {'even' if left%2==0 else 'odd'}, Right is {'even' if right%2==0 else 'odd'}")
        else:
            slow_print(f"Status: Total={left+right} (mod 4 = {(left+right)%4})")

        # Subtle hint for mathematically lost positions (no spoilers) game1
        if mode == "game1" and turn == "you" and left % 2 == 0 and right % 2 == 0:
            slow_print("The stones lock into a stubborn rhythm... the goblin seems confident.")

        # Subtle hint for mathematically lost positions (no spoilers) game2
        elif mode == "game2" and turn == "you" and (left + right) % 4 == 0:
            slow_print("The stones vibrate softly, settling into an uneasy stillness...")
            # alternate hints:
            # More mystical
            # slow_print("A low hum echoes through the circle, as if the ritual has already decided...")
            # More goblin-flavored
            # slow_print("The goblin’s grin widens. The stones no longer feel obedient.")
            # More mathematical
            # slow_print("The pattern of stones feels rigid, resistant to change.")

        if turn == "goblin":
            pause(0.4)
            if mode == "game1":
                l_take, r_take = goblin_move_game1(left, right)
            else:
                l_take, r_take = goblin_move_game2(left, right)

            left -= l_take
            right -= r_take
            slow_print(f"Goblin takes: {l_take} from left, {r_take} from right")

            if left + right == 0:
                slow_print("\n😈 The Goblin wins the ritual and does a tiny victory dance.")
                dmg = random.randint(8, 18)
                player["health"] -= dmg
                slow_print(f"The ritual backlash hits you for {dmg} damage. (HP: {player['health']})")
                return "ritual_done"

            turn = "you"
            continue

        # player turn
        while True:
            slow_print("Your move. Enter two numbers: L R  (example: 1 0)")
            raw = input("> ").strip().replace(",", " ")
            parts = raw.split()
            if len(parts) != 2 or not all(p.lstrip("-").isdigit() for p in parts):
                slow_print("Enter exactly two integers like: 1 0")
                continue
            l_take, r_take = map(int, parts)
            if l_take < 0 or r_take < 0:
                slow_print("No negative numbers, gremlin 😄")
                continue
            if l_take > left or r_take > right:
                slow_print("Illegal: you can't take more stones than exist.")
                continue
            if mode == "game1":
                if (l_take, r_take) not in [(1, 0), (0, 1), (1, 1)]:
                    slow_print("Illegal in Game 1. Only (1,0) (0,1) (1,1).")
                    continue
            else:
                if (l_take + r_take) == 0 or (l_take + r_take) > 3:
                    slow_print("Illegal in Game 2. Must take 1–3 stones total.")
                    continue
            break

        left -= l_take
        right -= r_take

        if left + right == 0:
            slow_print("\nYou win the ritual. The ash circle cracks like ice.")
            player["sigils"] += 1
            slow_print(f"You gained a Sigil! (Sigils: {player['sigils']}/3)")
            return "ritual_done"

        turn = "goblin"


# ----------------------------
# Dungeon shift event
# ----------------------------
def dungeon_shift(d):
    adj = d["adj"]
    n = len(adj)
    cur = d["current"]
    exit_room = d["exit"]

    action = random.choice(["open", "collapse"])

    # ---------- OPEN A SHORTCUT ----------
    if action == "open":
        for _ in range(20):  # try a few times
            a, b = random.sample(range(n), 2)
            if b not in adj[a]:
                adj[a].append(b)
                adj[b].append(a)
                return f"A hidden tunnel opens between {a} and {b}."
        return "You hear stone shift, but nothing new is revealed."

    # ---------- COLLAPSE A TUNNEL (SAFE) ----------
    candidates = [(u, v) for u in range(n) for v in adj[u] if u < v]
    random.shuffle(candidates)

    for u, v in candidates:
        # temporarily remove edge
        adj[u].remove(v)
        adj[v].remove(u)

        # check reachability
        if is_reachable(adj, cur, exit_room):
            return f"The ground collapses! A passage between {u} and {v} is gone."

        # rollback if unfair
        adj[u].append(v)
        adj[v].append(u)

    return "The dungeon groans, as if it wanted to change… but hesitates."



# ----------------------------
# Dungeon graph
# ----------------------------
def bfs_farthest(adj, start):
    dist = [-1] * len(adj)
    dist[start] = 0
    q = deque([start])
    while q:
        v = q.popleft()
        for u in adj[v]:
            if dist[u] == -1:
                dist[u] = dist[v] + 1
                q.append(u)
    far = max(range(len(adj)), key=lambda i: dist[i])
    return far, dist

def generate_dungeon(num_rooms=14, extra_edges=5):
    # Start with a random spanning tree to ensure connected
    adj = [[] for _ in range(num_rooms)]
    nodes = list(range(num_rooms))
    random.shuffle(nodes)
    for i in range(1, num_rooms):
        a = nodes[i]
        b = nodes[random.randrange(0, i)]
        adj[a].append(b)
        adj[b].append(a)

    # add extra random edges
    attempts = 0
    while extra_edges > 0 and attempts < 200:
        attempts += 1
        a = random.randrange(num_rooms)
        b = random.randrange(num_rooms)
        if a == b or b in adj[a]:
            continue
        adj[a].append(b)
        adj[b].append(a)
        extra_edges -= 1

    start = 0
    exit_room, dist = bfs_farthest(adj, start)

    # room types
    rooms = {}
    for i in range(num_rooms):
        rooms[i] = {
            "name": f"Room {i}",
            "desc": "Cold stone. A draft whispers through cracks.",
            "type": "empty",
            "cleared": False,
        }

    # spice names
    rooms[start]["name"] = "Cracked Archway"
    rooms[start]["desc"] = "You descend into the Goblin King’s maze. The air tastes like old coins."
    rooms[exit_room]["name"] = "Exit Gate"
    rooms[exit_room]["desc"] = "A gate of bone and iron. Three sockets wait for Sigils."
    rooms[exit_room]["type"] = "exit"

    # assign events (avoid start/exit)
    candidates = [i for i in range(num_rooms) if i not in (start, exit_room)]
    random.shuffle(candidates)

    # 4 loot rooms, 4 ritual rooms, 3 fights
    for idx, rid in enumerate(candidates):
        if idx < 4:
            rooms[rid]["type"] = "loot"
            rooms[rid]["name"] = "Loot Cache"
            rooms[rid]["desc"] = "Broken crates and glittering scraps."
        elif idx < 8:
            rooms[rid]["type"] = "ritual"
            rooms[rid]["name"] = "Goblin Ritual"
            rooms[rid]["desc"] = "Ash, bones, and a smug little laugh."
        elif idx < 11:
            rooms[rid]["type"] = "fight"
            rooms[rid]["name"] = "Ambush"
            rooms[rid]["desc"] = "Something moves in the dark."
        else:
            rooms[rid]["type"] = "empty"

    return {
        "adj": adj,
        "rooms": rooms,
        "start": start,
        "exit": exit_room,
        "current": start,
    }

def is_reachable(adj, start, target):
    visited = [False] * len(adj)
    q = deque([start])
    visited[start] = True

    while q:
        v = q.popleft()
        if v == target:
            return True
        for u in adj[v]:
            if not visited[u]:
                visited[u] = True
                q.append(u)

    return False

def enter_dungeon(state):
    # generate dungeon if none
    if "dungeon" not in state or not state["dungeon"]:
        state["dungeon"] = generate_dungeon()
        slow_print("The dungeon shifts into place beneath the village...\n")

    d = state["dungeon"]

    while True:
        if player["health"] <= 0:
            slow_print("\nYou collapse. The dungeon wins.\n")
            state["dungeon"] = None
            return

        room_id = d["current"]
        room = d["rooms"][str(room_id)] if isinstance(next(iter(d["rooms"].keys())), str) else d["rooms"][room_id]

        divider()
        slow_print(f"You are in: {room['name']}")
        slow_print(room["desc"])

        # run event once per room unless exit
        if room["type"] != "exit" and not room.get("cleared", False):
            if room["type"] == "loot":
                event_loot_cache()

            elif room["type"] == "ritual":
                result = event_goblin_ritual()
                if result == "ritual_done":
                    slow_print("\nThe dungeon shudders...")
                    msg = dungeon_shift(state["dungeon"])
                    slow_print(msg)

            elif room["type"] == "fight":
                print(ENEMY_ART)
                slow_print("A shadow lunges!")
                result = number_battle(difficulty=1 + (player["sigils"] // 1))
                if result["result"] == "win":
                    reward = 15 + random.randint(0, 25)
                    player["gold"] += reward
                    slow_print(f"You loot {reward} gold.")
                else:
                    # death handled by HP check next loop
                    pass
            else:
                slow_print("Nothing here but echoes.")

            room["cleared"] = True

        # exit room logic
        if room["type"] == "exit":
            slow_print(f"\nSigils: {player['sigils']}/3")
            if player["sigils"] >= 3:
                slow_print("The sockets flare. The gate unlocks.")
                slow_print("You step into moonlight. You escaped the Goblin King’s Graph.")
                slow_print("\n=== YOU WIN ===\n")
                # reset dungeon for next run
                state["dungeon"] = None
                return
            else:
                slow_print("The gate won’t budge. You need 3 Sigils.")

        # navigation
        adj = d["adj"]
        neighbors = adj[room_id]
        slow_print("\nExits:")
        for i, nb in enumerate(neighbors, 1):
            nb_room = d["rooms"][str(nb)] if isinstance(next(iter(d["rooms"].keys())), str) else d["rooms"][nb]
            tag = nb_room["type"]
            cleared = "✓" if nb_room.get("cleared") else " "
            print(f"{i}. [{cleared}] {nb_room['name']} ({tag})")

        print("\nA) Return to Village")
        print("S) Save")
        choice = input("> ").strip().lower()

        if choice == "a":
            slow_print("You retreat to the surface... for now.")
            return
        if choice == "s":
            state["player"] = player
            state["dungeon"] = d
            save_game(state)
            continue

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(neighbors):
                d["current"] = neighbors[idx]
            else:
                slow_print("Nope.")
        else:
            slow_print("Choose a door number, A, or S.")

# ----------------------------
# Village / Hub
# ----------------------------
def show_stats():
    divider()
    slow_print(f"Name: {player['name']}")
    slow_print(f"Health: {player['health']}")
    slow_print(f"Gold: {player['gold']}")
    slow_print(f"Pack capacity: {player['pack_capacity']}")
    slow_print(f"Sigils: {player['sigils']}/3")
    slow_print(f"Inventory: {player['inventory']}")
    slow_print("")

def use_item():
    divider()
    if not player["inventory"]:
        slow_print("You have no items.")
        return

    slow_print("Items in your pack:")
    for i, it in enumerate(player["inventory"], 1):
        print(f"{i}. {it}")
    print(f"{len(player['inventory'])+1}. Cancel")

    choice = input("> ").strip()
    try:
        idx = int(choice) - 1
    except ValueError:
        slow_print("Canceled.")
        return
    if idx < 0 or idx >= len(player["inventory"]):
        slow_print("Canceled.")
        return

    item = player["inventory"].pop(idx)
    if item == "Healing Potion":
        healed = min(100 - player["health"], 30)
        player["health"] += healed
        slow_print(f"You drink a Healing Potion and restore {healed} HP. (HP: {player['health']})")
    elif item == "Minor Elixir":
        healed = min(100 - player["health"], 70)
        player["health"] += healed
        slow_print(f"You drink a Minor Elixir and restore {healed} HP. (HP: {player['health']})")
    elif item == "Rare Sigil":
        # keep unless used at exit gate (we count sigils separately here)
        player["inventory"].append("Rare Sigil")
        slow_print("The Sigil hums but nothing happens... maybe the gate below wants these.")
    else:
        slow_print(f"You examine {item} but nothing happens.")

def shop():
    divider()
    print(SHOP_ART)
    slow_print("You enter the shop. The owner eyes your coin purse.")
    items = [
        {"name": "Healing Potion", "price": 30, "desc": "Restores 30 HP when used."},
        {"name": "Minor Elixir", "price": 60, "desc": "Restores 70 HP when used."},
        {"name": "Pack Reinforcement", "price": 40, "desc": "+1 pack capacity (permanent)."},
        {"name": "Rare Sigil", "price": 200, "desc": "A mysterious item rumored to affect destiny."}
    ]

    print("Your gold:", player["gold"])
    for i, it in enumerate(items, 1):
        print(f"{i}. {it['name']} - {it['price']} gold - {it['desc']}")
    print("5. Leave shop")

    choice = input("> ").strip()
    if choice in ("1", "2", "3", "4"):
        it = items[int(choice) - 1]
        if player["gold"] < it["price"]:
            slow_print("You can't afford that.")
            return

        player["gold"] -= it["price"]
        if it["name"] == "Pack Reinforcement":
            player["pack_capacity"] += 1
            slow_print("Leather straps tightened. Capacity increased.")
        else:
            player["inventory"].append(it["name"])
            slow_print(f"You bought: {it['name']}")
    else:
        slow_print("You leave the shop.")

def noticeboard():
    divider()
    slow_print("The noticeboard shows one warning in big letters:")
    slow_print("'THE GOBLIN KING'S MAZE SHIFTED AGAIN. SIGILS REQUIRED: THREE.'")
    slow_print("A smaller note: 'In the ritual rooms, the total stones whisper in mod 4…'")

def village(state):
    while True:
        divider()
        slow_print("You stroll through the small village. Traders call out from stalls.")
        print(SHOP_ART)
        print("1) Visit the Shop")
        print("2) Visit the Noticeboard")
        print("3) Enter the Dungeon")
        print("4) Use an item")
        print("5) Show stats")
        print("6) Save Game")
        print("7) Load Game")
        print("8) Quit (autosave)")

        choice = input("> ").strip()
        if choice == "1":
            shop()
        elif choice == "2":
            noticeboard()
        elif choice == "3":
            enter_dungeon(state)
        elif choice == "4":
            use_item()
        elif choice == "5":
            show_stats()
        elif choice == "6":
            state["player"] = player
            save_game(state)
        elif choice == "7":
            loaded = load_game()
            if loaded:
                state.clear()
                state.update(loaded)
                player.update(state.get("player", {}))
                slow_print("Loaded.")
        elif choice == "8":
            slow_print("Autosaving and exiting...")
            state["player"] = player
            save_game(state)
            slow_print("Goodbye.")
            raise SystemExit
        else:
            slow_print("Choose a valid option.")

# ----------------------------
# Start
# ----------------------------
def new_game_setup():
    divider()
    slow_print("What is your name, adventurer?")
    player["name"] = input("> ").strip() or "Nameless"
    player["health"] = 100
    player["gold"] = 50
    player["inventory"] = []
    player["pack_capacity"] = 5
    player["sigils"] = 0
    slow_print(f"Welcome, {player['name']} — your fate awaits!\n")

def intro(state):
    print(TITLE)
    slow_print("Do you want to (L)oad a previous game or (N)ew game?")
    choice = input("> ").strip().lower()
    if choice == "l":
        loaded = load_game()
        if loaded:
            state.update(loaded)
            player.update(state.get("player", {}))
            slow_print(f"Welcome back, {player['name']}!")
            return
        slow_print("Starting a new journey...")
    new_game_setup()
    state["player"] = player
    state["dungeon"] = None
    save_game(state)

def _jsonify_dungeon(state):
    # Make dungeon JSON-friendly (room keys as strings)
    if not state.get("dungeon"):
        return
    d = state["dungeon"]
    if isinstance(next(iter(d["rooms"].keys())), int):
        d["rooms"] = {str(k): v for k, v in d["rooms"].items()}
    state["dungeon"] = d

if __name__ == "__main__":
    random.seed()
    state = {}
    intro(state)

    # ensure dungeon keys are serializable
    _jsonify_dungeon(state)
    village(state)
