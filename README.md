# Minecraft Dungeons II - Standalone Native Trainer

A high-performance, standalone native GUI trainer for **Minecraft Dungeons II** (`Dungeons-WinGDK-Shipping.exe`).

Engineered specifically for singleplayer/offline play. Operates via direct Win32 Virtual Memory APIs (`ReadProcessMemory` / `WriteProcessMemory`) without attaching debuggers or injecting DLLs, completely bypassing anti-tamper watchdog terminations.

---

## Key Highlights

- **Zero External Dependencies**: Built entirely with the Python Standard Library (`ctypes` and `tkinter`). No `pip install` required.
- **Stealth Memory Operations**: Interacts directly with the Unreal Engine 5 object graph through unhooked Win32 process handles (`PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION`). Does not open debugging ports or set hardware breakpoints.
- **GAS Dual-Write Architecture**: Automatically synchronizes both `BaseValue` and `CurrentValue` for all Gameplay Ability System (GAS) attributes, preventing the engine from reverting modifications during combat, state changes, or ability activations.
- **Dynamic GEngine Traversal**: Resolves character, player controller, camera manager, and attribute sets dynamically from the root `GEngine` pointer (`0x0B0577C8`), ensuring pointer stability across level transitions, map loads, and character respawns.
- **Multi-Tier Loot Multiplier & Uncapped Payouts**: Scales `DropDuplicationChance` and lifts the internal engine `MaximumLootingPayouts` cap, enabling 2x, 3x, 5x, 10x, and arbitrary custom loot drops.

---

## Features

### 1. Currencies & Economy
- **Emeralds (Green Gem)**: Quick +1,000, Max Cap (9,999), and custom balance input.
- **Echo Shards / SpringStone (Blue Shard)**: Quick +500, Max Cap (9,999), and custom balance input.
- **Enchantment Points (Purple Diamond)**: Quick +5 Points, Max Cap (99), and custom balance input.
- **Souls**: Quick +10,000, Max Cap (99,999), custom balance input, and a **Freeze Souls** toggle that locks souls to 99,999 every game tick.
- **Arrows (Ammo)**: Refill (999), Max Cap, and custom count input (respects lower and higher values).
- **Auto-Refill Arrows Toggle**: Continuous background loop keeping arrow ammo topped to maximum for infinite shooting.
- **Quiver Refill Speed**: Fast (5x), Instant (0s recharge delay), Reset (1x), and custom multiplier.
- **Rapid Fire**: Rapid (3x), Insane (5x), Reset (1x), and custom attack speed multiplier.

### 2. Combat & Survival
- **God Mode Toggle**: Continuous immunity locking Health to Max, Damage Resistance to 0.0 (Immune), and forcing the actor invincibility byte ON (`CanBeDamaged = False`).
- **Instant Full Heal**: Instantly restores health to maximum.
- **Energy Shield**: Maximize Shield (100) or reset to 0.
- **Instant Cooldowns**: Artifact Cooldown (0.0s) and Health Potion Cooldown (0.0s).
- **Critical Hit Chance**: 100% Guaranteed Critical Hits (1.0) or reset to vanilla (0.0).
- **Melee Attack Speed**: 3x, 5x, Reset (1x), and custom multiplier.
- **Melee Reach / Range**: Super Reach (2,500 units) and Reset (250 units).
- **MultiShot**: Guaranteed 100% chance with 5 additional projectiles.

### 3. Movement & Physics
- **GAS Movement Speed Multiplier**: 1.5x, 2.0x, 3.0x, Reset (1.0x), and custom multiplier.
- **Lock Speed Toggle**: Continuous lock preventing attack animations and combat montages from resetting the speed multiplier to 1.0.
- **Jump Height (Z Velocity)**: High Jump (2,000), Super Jump (3,000), Reset (1,440), and custom velocity.
- **Gravity Scale**: Low Gravity (0.5), Moon Gravity (0.2), Reset (1.2), and custom gravity scale.
- **Roll Cooldown**: Instant (0.0s) or Reset (2.5s).
- **Player Time Dilation (Speedhack)**: 0.5x Slow-Motion, 2.0x Fast-Forward, 5.0x Hyper Speed, Reset (1.0x).

### 4. Progression & Multi-Tier Loot
- **Master Loot Multiplier (Synchronized All-in-One)**:
  - `2x Loot (Duplicate)`: Duplication = 1.0, Max Payouts = 2.0, Loot Multiplier = 2.0, Drop Chance = 2.0
  - `3x Loot (Triple)`: Duplication = 2.0, Max Payouts = 3.0, Loot Multiplier = 3.0, Drop Chance = 3.0
  - `5x Loot (Quintuple)`: Duplication = 4.0, Max Payouts = 5.0, Loot Multiplier = 5.0, Drop Chance = 5.0
  - `10x Loot (Loot Explosion)`: Duplication = 9.0, Max Payouts = 10.0, Loot Multiplier = 10.0, Drop Chance = 10.0
  - `Custom Multiplier`: Type any value (e.g., 7, 15, 50) and click **Set**. Sets `DropDuplicationChance = N - 1`, `MaximumLootingPayouts = N`, and `LootingMultiplier = N`.
  - `Reset (1x)`: Restores vanilla drop rates (`Duplication = 0.0`, `Max Payouts = 1.0`, `Loot Multiplier = 0.0`).
- **Drop Duplication Chance (Direct Control)**: Presets for 2x (100%), 3x (200%), 5x (400%), 10x (900%), and Reset (0%). Automatically lifts `MaximumLootingPayouts` if needed.
- **Max Loot Payouts Cap**: Exposes the internal engine drop payout ceiling: Default (1), 5 Payouts, 10 Payouts, 50 Payouts (Uncapped), and custom input.
- **Looting Drop Multiplier**: 5x, 10x, 25x, Reset (0), and custom input.
- **Rarity Luck**: 100% Unique / Rare item roll chance.
- **Character Level & XP**: Instant Level 50, Level 100, +10,000 XP, +50,000 XP, or custom amounts.
- **Max All Vendors**: Instantly sets Village Merchant, Enchantsmith, and Old Blacksmith to Level 3 with 99 restock charges.

### 5. Developer & Camera
- **EnableDebug Flag**: Toggles developer mode on `PlayerController + 0x94D`.
- **EnableDebugUIControls**: Toggles internal debug UI controls on `PlayerController + 0x748`.
- **Camera Field of View (FOV)**: FOV 100, 110, 120, Reset (90), and custom numeric entry.

---

## Technical Architecture

```
[ Dungeons-WinGDK-Shipping.exe ]
               │
               ▼ (Base Address + 0x0B0577C8)
          [ GEngine ]
               │
               ▼ (+0x1248)
        [ GameInstance ]
               │
               ▼ (+0x0038)
       [ LocalPlayer Array ] ──> [0] LocalPlayer (+0x0000)
                                        │
                                        ▼ (+0x0030)
                              [ PlayerController ]
                                   ├── +0x02F8 ──> [ BP_AlexCharacter_C ] (Pawn)
                                   │                    │
                                   │                    ▼ (+0x0A20)
                                   │            [ AbilitySystemComponent ]
                                   │                    │
                                   │                    ▼ (+0x10A8)
                                   │            [ SpawnedAttributes Array ]
                                   │                    ├── [ 0] (+0x00) ATR_Resistance
                                   │                    ├── [ 1] (+0x08) ATR_Movement
                                   │                    ├── [ 2] (+0x10) ATR_MeleeAttack
                                   │                    ├── [ 3] (+0x18) ATR_RangedAttack
                                   │                    ├── [ 4] (+0x20) ATR_Artifact
                                   │                    ├── [ 7] (+0x38) ATR_Damage
                                   │                    ├── [ 8] (+0x40) ATR_Health
                                   │                    ├── [ 9] (+0x48) ATR_MerchantInfo
                                   │                    ├── [10] (+0x50) ATR_Jump
                                   │                    ├── [11] (+0x58) ATR_Soul
                                   │                    ├── [12] (+0x60) ATR_Currency
                                   │                    ├── [13] (+0x68) ATR_XP
                                   │                    └── [16] (+0x80) ATR_Loot
                                   │
                                   ├── +0x0360 ──> [ BP_DungeonsCameraManager_C ] (+0x2C0: FOV)
                                   ├── +0x0748 ──> EnableDebugUIControls (uint8)
                                   └── +0x094D ──> EnableDebug (uint8)
```

### Attribute Structure (`FGameplayAttributeData`)
Every Gameplay Ability System attribute is structured as:
- `+0x00`: Attribute descriptor / vtable pointer (8 bytes)
- `+0x08`: `BaseValue` (float, 4 bytes)
- `+0x0C`: `CurrentValue` (float, 4 bytes)

To ensure persistent modifications, the trainer always writes to both `BaseValue` and `CurrentValue`.

---

## Requirements

- **Operating System**: Windows 10 or Windows 11 (64-bit)
- **Python**: Python 3.10 or newer (ensure the official Python installer with Tcl/Tk support is used)
- **Target Game**: Minecraft Dungeons II (`Dungeons-WinGDK-Shipping.exe`)

---

## Installation & Usage

1. **Clone or Download the Repository**:
   ```bash
   git clone https://github.com/your-username/minecraft-dungeons-2-trainer.git
   cd minecraft-dungeons-2-trainer
   ```

2. **Launch the Game**:
   - Start Minecraft Dungeons II and load into the camp or any mission.

3. **Run the Trainer**:
   - Double-click `run_trainer.bat`, or execute via terminal:
     ```bash
     python trainer_gui.py
     ```

4. **Status Verification**:
   - The status bar at the top will automatically transition from `Searching for game process...` to `Attached: Dungeons-WinGDK-Shipping.exe (PID XXXXX)` with green status indicator once connected.
   - Live values will populate across all tabs.

---

## Troubleshooting

- **Trainer shows "Game not found"**:
  Ensure the game executable is running. The process name should be `Dungeons-WinGDK-Shipping.exe`. Click the **Reconnect** button in the top right corner.
- **Python not recognized in `run_trainer.bat`**:
  Make sure Python 3.10+ is installed and that the option **"Add Python to PATH"** was selected during installation.
- **Values display "---"**:
  In Unreal Engine, characters and attribute sets are allocated when entering a level or camp. Enter a level or camp session for all pointers to resolve.

---

## License

Distributed under the [MIT License](LICENSE).
