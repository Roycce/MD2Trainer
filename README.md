# Minecraft Dungeons II - Standalone Native Trainer v1.0.1

A lightweight, standalone native GUI trainer for Minecraft Dungeons II (`Dungeons-WinGDK-Shipping.exe`), designed for offline singleplayer use. It accesses game memory directly via Win32 Virtual Memory APIs without attaching debuggers, injecting DLLs, or triggering anti-tamper termination.

---

## Features

- **Currencies**: Adjust Emeralds, Echo Shards, and Enchantment Points with custom balances or maximum caps; freeze Souls value; Currency Gain Multipliers (2x, 3x, 5x, 10x, and custom Nx for Emeralds and Souls).
- **Combat**: God Mode toggle (continuous health, shield, and invincibility lock), Infinite Potions toggle & instant potion cooldown (safe non-blocking recharge with full charges), fast artifact cooldown, guaranteed critical hits, and multishot.
- **Movement**: Movement speed multiplier with combat-lock (prevents attack animation resets), custom jump height, gravity scale, Infinite Roll toggle & instant roll cooldown (recharges charges cleanly), and time dilation.
- **Ammo**: Custom arrow ammo count, auto-refill toggle for infinite arrows, and rapid fire.
- **Progression & Loot**: Master loot multipliers (2x, 3x, 5x, 10x, and custom Nx), drop duplication, uncapped loot payout ceiling, 100% rare/unique drop rate, character level adjustments, and one-click vendor upgrades.

---

## Requirements

- Windows 10 or 11 (64-bit)
- Python 3.10+ (standard library only; zero external packages or pip dependencies required)
- Minecraft Dungeons II (`Dungeons-WinGDK-Shipping.exe`)

---

## How to Run

1. Launch Minecraft Dungeons II and load into camp or a mission.
2. Run `run_trainer.bat` (or execute `python trainer_gui.py` in terminal).
3. The trainer will automatically detect and attach to the game process.

---

## Disclaimer

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability arising from the use of or inability to use this software. Intended strictly for singleplayer offline use.
