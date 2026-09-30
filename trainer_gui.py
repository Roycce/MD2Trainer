#!/usr/bin/env python3
"""
MINECRAFT DUNGEONS II - STANDALONE NATIVE TRAINER
Target: Dungeons-WinGDK-Shipping.exe (Singleplayer / Offline)
Direct Win32 Memory Access - Zero Debugger, Zero Watchdog Conflicts, Zero Dependencies.
"""

import sys
import time
import struct
import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
from ctypes import wintypes

k32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

# Process Memory Access Constants
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
PROCESS_ACCESS = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION

# Pointer Chain Definitions (Base Module + GEngine 0x0B0577C8)
CHAINS = {
    # Currencies & Inventory (AttrSet [12] = ATR_Currency at 0x60)
    "emeralds_current":     ['9C', '60', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "emeralds_base":        ['98', '60', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "emeralds_cap_cur":     ['AC', '60', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "emeralds_cap_base":    ['A8', '60', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],

    # Echo Shards / SpringStone (Blue Shard in Screenshot 1, AttrSet [12] at +0x100)
    "springstone_current":  ['10C', '60', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "springstone_base":     ['108', '60', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "springstone_cap_cur":  ['11C', '60', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "springstone_cap_base": ['118', '60', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],

    # Enchantment Points (Purple Diamond 51/1 in Screenshot 1, AttrSet [13] = ATR_XP at 0x68)
    "ench_points_cur":      ['DC', '68', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "ench_points_base":     ['D8', '68', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "ench_points_cap_cur":  ['FC', '68', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "ench_points_cap_base": ['F8', '68', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],

    # Souls (AttrSet [11] = ATR_Soul at 0x58)
    "souls_current":        ['9C', '58', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "souls_base":           ['98', '58', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "souls_cap_cur":        ['AC', '58', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "souls_cap_base":       ['A8', '58', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],

    # Arrows (Ammo, AttrSet [3] = ATR_RangedAttack at 0x18)
    "ammo_current":         ['BC', '18', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "ammo_base":            ['B8', '18', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "ammo_max_cur":         ['CC', '18', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "ammo_max_base":        ['C8', '18', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "rapid_fire_cur":       ['9C', '18', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "rapid_fire_base":      ['98', '18', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],

    # Currency Gain Multipliers (AttrSet [12] = ATR_Currency at 0x60, AttrSet [11] = ATR_Soul at 0x58)
    "emerald_increase_cur":    ['CC', '60', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "emerald_increase_base":   ['C8', '60', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "emerald_max_add_cur":     ['EC', '60', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "emerald_max_add_base":    ['E8', '60', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "emerald_drop_chance_cur": ['DC', '60', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "emerald_drop_chance_base":['D8', '60', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "soul_gather_cur":         ['DC', '58', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "soul_gather_base":        ['D8', '58', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],

    # Level & Progression (AttrSet [13] = ATR_XP at 0x68)
    "level":                ['BC', '68', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "xp_current":           ['9C', '68', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "xp_needed":            ['AC', '68', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],

    # Survival & Combat (AttrSet [8] = ATR_Health at 0x40, AttrSet [0] = ATR_Resistance at 0x0)
    "health_current":          ['9C', '40', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "health_max":              ['BC', '40', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "shield_current":          ['16C', '0', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "shield_max":              ['18C', '0', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "damage_resist":           ['9C', '0', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "actor_invincible":        ['5A', '2F8', '30', '0', '38', '1248'],
    "artifact_cd":             ['9C', '20', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "artifact_cd_base":        ['98', '20', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "potion_cd":               ['13C', '40', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "potion_cd_base":          ['138', '40', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "potion_base_cd_cur":      ['12C', '40', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "potion_base_cd_base":     ['128', '40', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "potion_charges_cur":      ['16C', '40', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "potion_charges_base":     ['168', '40', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "potion_max_charges_cur":  ['17C', '40', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "potion_max_charges_base": ['178', '40', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "crit_chance":             ['21C', '38', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "crit_multiplier":         ['24C', '38', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "melee_dmg_mult":          ['1BC', '38', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "ranged_dmg_mult":         ['1CC', '38', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "melee_speed":             ['9C', '10', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "melee_reach":             ['AC', '10', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "multishot_chance":        ['13C', '18', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "multishot_count":         ['14C', '18', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],

    # Movement & Physics (AttrSet [1] = ATR_Movement at 0x8)
    "move_mult_cur":           ['AC', '8', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "move_mult_base":          ['A8', '8', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "jump_velocity":           ['1A8', '330', '2F8', '30', '0', '38', '1248'],
    "gravity":                 ['1A0', '330', '2F8', '30', '0', '38', '1248'],
    "roll_cd":                 ['12C', '8', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "roll_cd_base":            ['128', '8', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "roll_charges_cur":        ['14C', '8', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "roll_charges_base":       ['148', '8', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "roll_max_charges_cur":    ['15C', '8', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "roll_max_charges_base":   ['158', '8', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "time_dilation":           ['68', '2F8', '30', '0', '38', '1248'],

    # Loot & Vendors (AttrSet [16] = ATR_Loot at 0x80, AttrSet [9] = ATR_MerchantInfo at 0x48)
    "loot_multiplier":  ['9C', '80', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "loot_mult_base":   ['98', '80', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "max_payouts_cur":  ['AC', '80', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "max_payouts_base": ['A8', '80', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "rarity_bonus":     ['BC', '80', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "rarity_bonus_base":['B8', '80', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "drop_chance":      ['CC', '80', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "drop_chance_base": ['C8', '80', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "drop_duplication": ['DC', '80', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "drop_dup_base":    ['D8', '80', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "merchant_charges": ['9C', '48', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "merchant_upg":     ['CC', '48', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "enchantsmith_upg": ['EC', '48', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],
    "blacksmith_upg":   ['10C', '48', '10A8', 'A20', '2F8', '30', '0', '38', '1248'],

    # Engine & Debug
    "debug_flag":       ['94D', '30', '0', '38', '1248'],
    "debug_ui":         ['748', '30', '0', '38', '1248'],
    "camera_fov":       ['2C0', '360', '30', '0', '38', '1248'],
}

class MemoryManager:
    def __init__(self):
        self.pid = None
        self.base_addr = None
        self.h_proc = None

    def attach(self):
        if self.h_proc:
            k32.CloseHandle(self.h_proc)
            self.h_proc = None
        self.pid = None
        self.base_addr = None

        pids = (wintypes.DWORD * 2048)()
        cbNeeded = wintypes.DWORD()
        k32.K32EnumProcesses(pids, ctypes.sizeof(pids), ctypes.byref(cbNeeded))
        num = cbNeeded.value // 4

        for i in range(num):
            pid = pids[i]
            if pid == 0: continue
            h = k32.OpenProcess(0x0410, False, pid)
            if h:
                HMODULE = ctypes.c_void_p
                hMods = (HMODULE * 1)()
                cb = wintypes.DWORD()
                psapi.EnumProcessModulesEx.argtypes = [wintypes.HANDLE, ctypes.POINTER(HMODULE), wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), wintypes.DWORD]
                if psapi.EnumProcessModulesEx(h, hMods, ctypes.sizeof(hMods), ctypes.byref(cb), 3):
                    mod_name = (ctypes.c_char * 260)()
                    psapi.GetModuleBaseNameA(h, HMODULE(hMods[0]), mod_name, 260)
                    if mod_name.value.decode(errors='ignore').lower() == 'dungeons-wingdk-shipping.exe':
                        self.pid = pid
                        self.base_addr = hMods[0]
                        k32.CloseHandle(h)
                        break
                k32.CloseHandle(h)

        if not self.pid:
            return False

        self.h_proc = k32.OpenProcess(PROCESS_ACCESS, False, self.pid)
        return self.h_proc is not None and self.h_proc != 0

    def resolve_chain(self, offsets_list):
        if not self.h_proc or not self.base_addr:
            return None
        curr_addr = self.base_addr + 0x0B0577C8
        buf8 = ctypes.create_string_buffer(8)
        for off_str in reversed(offsets_list):
            off = int(off_str, 16)
            res = k32.ReadProcessMemory(self.h_proc, ctypes.c_void_p(curr_addr), buf8, 8, None)
            if not res:
                return None
            ptr = struct.unpack('<Q', buf8.raw)[0]
            if not ptr or ptr < 0x10000:
                return None
            curr_addr = ptr + off
        return curr_addr

    def read_float(self, key):
        addr = self.resolve_chain(CHAINS[key])
        if not addr: return None
        buf4 = ctypes.create_string_buffer(4)
        if k32.ReadProcessMemory(self.h_proc, ctypes.c_void_p(addr), buf4, 4, None):
            return struct.unpack('<f', buf4.raw)[0]
        return None

    def write_float(self, key, val):
        addr = self.resolve_chain(CHAINS[key])
        if not addr: return False
        buf4 = struct.pack('<f', float(val))
        bytes_written = ctypes.c_size_t()
        return bool(k32.WriteProcessMemory(self.h_proc, ctypes.c_void_p(addr), buf4, 4, ctypes.byref(bytes_written)))

    def read_byte(self, key):
        addr = self.resolve_chain(CHAINS[key])
        if not addr: return None
        buf1 = ctypes.create_string_buffer(1)
        if k32.ReadProcessMemory(self.h_proc, ctypes.c_void_p(addr), buf1, 1, None):
            return struct.unpack('<B', buf1.raw)[0]
        return None

    def write_byte(self, key, val):
        addr = self.resolve_chain(CHAINS[key])
        if not addr: return False
        buf1 = struct.pack('<B', int(val))
        bytes_written = ctypes.c_size_t()
        return bool(k32.WriteProcessMemory(self.h_proc, ctypes.c_void_p(addr), buf1, 1, ctypes.byref(bytes_written)))


class TrainerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minecraft Dungeons II - Native Trainer v1.0.1")
        self.geometry("880x730")
        self.minsize(820, 650)
        self.configure(bg="#181825")

        self.mem = MemoryManager()
        self.god_mode_active = False
        self.freeze_souls_active = False
        self.auto_refill_ammo_active = False
        self.lock_speed_active = False
        self.locked_speed_val = 1.0
        self.infinite_potions_active = False
        self.infinite_roll_active = False

        self.setup_styles()
        self.create_widgets()

        self.try_connect()
        self.after(500, self.refresh_loop)

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TNotebook', background="#181825", borderwidth=0)
        style.configure('TNotebook.Tab', background="#1e1e2e", foreground="#cdd6f4", padding=[18, 6], font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#313244')], foreground=[('selected', '#89b4fa')])
        style.configure('TFrame', background="#181825")
        style.configure('Card.TFrame', background="#1e1e2e", relief='flat')
        style.configure('TLabel', background="#1e1e2e", foreground="#cdd6f4", font=('Segoe UI', 9))
        style.configure('Header.TLabel', background="#181825", foreground="#89b4fa", font=('Segoe UI', 12, 'bold'))
        style.configure('Status.TLabel', background="#181825", foreground="#a6e3a1", font=('Segoe UI', 9, 'bold'))
        style.configure('Value.TLabel', background="#1e1e2e", foreground="#f9e2af", font=('Consolas', 10, 'bold'))
        style.configure('TButton', background="#313244", foreground="#cdd6f4", font=('Segoe UI', 9), borderwidth=0, padding=[6, 3])
        style.map('TButton', background=[('active', '#45475a'), ('pressed', '#585b70')])

    def create_widgets(self):
        # Top Header Bar
        top_bar = tk.Frame(self, bg="#181825", padx=16, pady=10)
        top_bar.pack(fill='x')

        title_lbl = tk.Label(top_bar, text="MINECRAFT DUNGEONS II - NATIVE TRAINER v1.0.1", font=('Segoe UI', 13, 'bold'), bg="#181825", fg="#89b4fa")
        title_lbl.pack(side='left')

        self.status_lbl = tk.Label(top_bar, text="Searching for game process...", font=('Segoe UI', 9, 'bold'), bg="#181825", fg="#f38ba8")
        self.status_lbl.pack(side='right', padx=10)

        refresh_btn = ttk.Button(top_bar, text="Reconnect", command=self.try_connect)
        refresh_btn.pack(side='right')

        # Notebook (Clean concise tab names)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=14, pady=8)

        self.tab_currencies = self.create_tab("Currencies")
        self.tab_combat = self.create_tab("Combat")
        self.tab_movement = self.create_tab("Movement")
        self.tab_progression = self.create_tab("Progression")
        self.tab_developer = self.create_tab("Developer")

        self.build_currencies_tab()
        self.build_combat_tab()
        self.build_movement_tab()
        self.build_progression_tab()
        self.build_developer_tab()

    def create_tab(self, name):
        frame = tk.Frame(self.notebook, bg="#1e1e2e", padx=16, pady=16)
        self.notebook.add(frame, text=name)
        return frame

    def try_connect(self):
        if self.mem.attach():
            self.status_lbl.config(text=f"Attached: Dungeons-WinGDK-Shipping.exe (PID {self.mem.pid})", fg="#a6e3a1")
        else:
            self.status_lbl.config(text="Game not found (Waiting for Dungeons-WinGDK-Shipping.exe)", fg="#f38ba8")

    # ==========================================
    # Tab 1: Currencies
    # ==========================================
    def build_currencies_tab(self):
        f = self.tab_currencies

        # Emeralds (Green Gem in Game, Cap: 9,999)
        self.lbl_emeralds = self.add_row(f, 0, "Emeralds (Green Gem):", "emeralds_current",
                                         [("+1,000", lambda: self.adjust_emeralds(1000)),
                                          ("Max (9,999)", lambda: self.set_emeralds(9999))],
                                         custom_entry=True, setter=self.set_emeralds)

        # Echo Shards / SpringStone (Blue Shard in Screenshot 1)
        self.lbl_springstone = self.add_row(f, 1, "Echo Shards (Blue Shard):", "springstone_current",
                                            [("+500", lambda: self.adjust_springstone(500)),
                                             ("Max (9,999)", lambda: self.set_springstone(9999))],
                                            custom_entry=True, setter=self.set_springstone)

        # Enchantment Points (Purple Diamond 51/1 in Screenshot 1)
        self.lbl_ench = self.add_row(f, 2, "Enchantment Points (Purple):", "ench_points_cur",
                                     [("+5 Points", lambda: self.adjust_ench_points(5)),
                                      ("Set 99 Points", lambda: self.set_ench_points(99))],
                                     custom_entry=True, setter=self.set_ench_points)

        # Currency Gain Multiplier (Emeralds & Soul Gathering Scale)
        self.lbl_curr_mult = self.add_row(f, 3, "Currency Gain Multiplier:", "emerald_increase_cur",
                                          [("2x Gain", lambda: self.set_currency_gain(2.0)),
                                           ("3x Gain", lambda: self.set_currency_gain(3.0)),
                                           ("5x Gain", lambda: self.set_currency_gain(5.0)),
                                           ("10x Gain", lambda: self.set_currency_gain(10.0)),
                                           ("Reset (1x)", lambda: self.set_currency_gain(1.0))],
                                          custom_entry=True, setter=self.set_currency_gain)

        # Souls (with dedicated Freeze Souls toggle)
        self.lbl_souls = self.add_row(f, 4, "Souls (Soul Energy):", "souls_current",
                                      [("+500", lambda: self.adjust_souls(500)),
                                       ("Max (99,999)", lambda: self.set_souls(99999))],
                                      custom_entry=True, setter=self.set_souls)

        # Freeze Souls Toggle Row
        freeze_frame = tk.Frame(f, bg="#1e1e2e", pady=2)
        freeze_frame.grid(row=5, column=0, columnspan=5, sticky='w')
        self.btn_freeze_souls = tk.Button(freeze_frame, text="FREEZE SOULS (OFF)", font=('Segoe UI', 9, 'bold'),
                                          bg="#313244", fg="#f38ba8", padx=12, pady=4, relief='flat',
                                          command=self.toggle_freeze_souls)
        self.btn_freeze_souls.pack(side='left')
        lbl_souls_hint = tk.Label(freeze_frame, text="Locks Souls to Max capacity continuously (Unlimited Artifact activations)",
                                  bg="#1e1e2e", fg="#a6adc8", font=('Segoe UI', 8))
        lbl_souls_hint.pack(side='left', padx=10)

        # Arrows (Ammo) - Custom amount, respects lower values, auto-refill toggle
        self.lbl_ammo = self.add_row(f, 6, "Arrows (Ammo Count):", "ammo_current",
                                     [("Refill (999)", lambda: self.set_ammo(999)),
                                      ("Max Cap (999)", self.max_ammo_cap)],
                                     custom_entry=True, setter=self.set_ammo)

        # Auto-Refill (Infinite Ammo) Toggle Row
        refill_frame = tk.Frame(f, bg="#1e1e2e", pady=2)
        refill_frame.grid(row=7, column=0, columnspan=5, sticky='w')
        self.btn_auto_refill = tk.Button(refill_frame, text="AUTO-REFILL ARROWS (OFF)", font=('Segoe UI', 9, 'bold'),
                                         bg="#313244", fg="#f38ba8", padx=12, pady=4, relief='flat',
                                         command=self.toggle_auto_refill)
        self.btn_auto_refill.pack(side='left')
        lbl_refill_hint = tk.Label(refill_frame, text="Infinite Arrows: Keeps ammo topped to max every game tick",
                                   bg="#1e1e2e", fg="#a6adc8", font=('Segoe UI', 8))
        lbl_refill_hint.pack(side='left', padx=10)

        # Rapid Fire (Bow Attack Speed)
        self.lbl_rapid = self.add_row(f, 8, "Rapid Fire (Bow Speed):", "rapid_fire_cur",
                                      [("Rapid (3x)", lambda: self.set_rapid_fire(3.0)),
                                       ("Insane (5x)", lambda: self.set_rapid_fire(5.0)),
                                       ("Reset (1x)", lambda: self.set_rapid_fire(1.0))],
                                      custom_entry=True, setter=self.set_rapid_fire)

    def set_emeralds(self, val):
        val = float(val)
        self.mem.write_float("emeralds_cap_base", max(9999.0, val))
        self.mem.write_float("emeralds_cap_cur", max(9999.0, val))
        self.mem.write_float("emeralds_base", val)
        self.mem.write_float("emeralds_current", val)

    def adjust_emeralds(self, delta):
        cur = self.mem.read_float("emeralds_current") or 0.0
        self.set_emeralds(cur + delta)

    def set_currency_gain(self, mult):
        mult = float(mult)
        if mult <= 1.0:
            self.mem.write_float("emerald_increase_base", 0.0)
            self.mem.write_float("emerald_increase_cur", 0.0)
            self.mem.write_float("emerald_max_add_base", 1.0)
            self.mem.write_float("emerald_max_add_cur", 1.0)
            self.mem.write_float("emerald_drop_chance_base", 0.0)
            self.mem.write_float("emerald_drop_chance_cur", 0.0)
            self.mem.write_float("soul_gather_base", 1.0)
            self.mem.write_float("soul_gather_cur", 1.0)
        else:
            pct = mult - 1.0
            max_add = max(1.0, mult * 5.0)
            self.mem.write_float("emerald_increase_base", pct)
            self.mem.write_float("emerald_increase_cur", pct)
            self.mem.write_float("emerald_max_add_base", max_add)
            self.mem.write_float("emerald_max_add_cur", max_add)
            self.mem.write_float("emerald_drop_chance_base", mult)
            self.mem.write_float("emerald_drop_chance_cur", mult)
            self.mem.write_float("soul_gather_base", mult)
            self.mem.write_float("soul_gather_cur", mult)

    def set_springstone(self, val):
        val = float(val)
        self.mem.write_float("springstone_cap_base", max(9999.0, val))
        self.mem.write_float("springstone_cap_cur", max(9999.0, val))
        self.mem.write_float("springstone_base", val)
        self.mem.write_float("springstone_current", val)

    def adjust_springstone(self, delta):
        cur = self.mem.read_float("springstone_current") or 0.0
        self.set_springstone(cur + delta)

    def set_ench_points(self, val):
        val = float(val)
        self.mem.write_float("ench_points_cap_base", max(99.0, val))
        self.mem.write_float("ench_points_cap_cur", max(99.0, val))
        self.mem.write_float("ench_points_base", val)
        self.mem.write_float("ench_points_cur", val)

    def adjust_ench_points(self, delta):
        cur = self.mem.read_float("ench_points_cur") or 0.0
        self.set_ench_points(cur + delta)

    def set_souls(self, val):
        val = float(val)
        self.mem.write_float("souls_cap_base", max(100.0, val))
        self.mem.write_float("souls_cap_cur", max(100.0, val))
        self.mem.write_float("souls_base", val)
        self.mem.write_float("souls_current", val)

    def adjust_souls(self, delta):
        cur = self.mem.read_float("souls_current") or 0.0
        self.set_souls(cur + delta)

    def toggle_freeze_souls(self):
        self.freeze_souls_active = not self.freeze_souls_active
        if self.freeze_souls_active:
            self.btn_freeze_souls.config(text="SOULS: FROZEN (INFINITE)", bg="#a6e3a1", fg="#11111b")
            self.apply_freeze_souls()
        else:
            self.btn_freeze_souls.config(text="FREEZE SOULS (OFF)", bg="#313244", fg="#f38ba8")

    def apply_freeze_souls(self):
        s_cap = self.mem.read_float("souls_cap_cur") or 100.0
        s_val = max(s_cap, 99999.0)
        self.mem.write_float("souls_cap_base", s_val)
        self.mem.write_float("souls_cap_cur", s_val)
        self.mem.write_float("souls_base", s_val)
        self.mem.write_float("souls_current", s_val)

    def set_ammo(self, val):
        val = float(val)
        cur_max = self.mem.read_float("ammo_max_cur") or 15.0
        if val > cur_max:
            self.mem.write_float("ammo_max_base", val)
            self.mem.write_float("ammo_max_cur", val)
        # CRITICAL FIX: Write BOTH ammo_base and ammo_current so lower values are strictly respected
        self.mem.write_float("ammo_base", val)
        self.mem.write_float("ammo_current", val)

    def max_ammo_cap(self):
        self.mem.write_float("ammo_max_base", 999.0)
        self.mem.write_float("ammo_max_cur", 999.0)
        self.mem.write_float("ammo_base", 999.0)
        self.mem.write_float("ammo_current", 999.0)

    def toggle_auto_refill(self):
        self.auto_refill_ammo_active = not self.auto_refill_ammo_active
        if self.auto_refill_ammo_active:
            self.btn_auto_refill.config(text="AUTO-REFILL: ON (INFINITE)", bg="#a6e3a1", fg="#11111b")
            self.apply_auto_refill()
        else:
            self.btn_auto_refill.config(text="AUTO-REFILL ARROWS (OFF)", bg="#313244", fg="#f38ba8")

    def apply_auto_refill(self):
        m = self.mem.read_float("ammo_max_cur") or 999.0
        m = max(m, 999.0)
        self.mem.write_float("ammo_max_base", m)
        self.mem.write_float("ammo_max_cur", m)
        self.mem.write_float("ammo_base", m)
        self.mem.write_float("ammo_current", m)

    def set_rapid_fire(self, spd):
        spd = float(spd)
        self.mem.write_float("rapid_fire_base", spd)
        self.mem.write_float("rapid_fire_cur", spd)

    # ==========================================
    # Tab 2: Combat
    # ==========================================
    def build_combat_tab(self):
        f = self.tab_combat

        # God Mode Toggle Button
        god_frame = tk.Frame(f, bg="#1e1e2e", pady=6)
        god_frame.grid(row=0, column=0, columnspan=5, sticky='w')
        self.btn_god = tk.Button(god_frame, text="TOGGLE GOD MODE (OFF)", font=('Segoe UI', 10, 'bold'),
                                 bg="#313244", fg="#f38ba8", padx=16, pady=6, relief='flat',
                                 command=self.toggle_god_mode)
        self.btn_god.pack(side='left')

        god_hint = tk.Label(god_frame, text="Locks Health to Max, Damage Resistance to 0 (Immune), Invincible Byte ON",
                            bg="#1e1e2e", fg="#a6adc8", font=('Segoe UI', 8))
        god_hint.pack(side='left', padx=12)

        self.lbl_health = self.add_row(f, 1, "Health (Current / Max):", "health_current",
                                       [("Full Heal", self.full_heal),
                                        ("Set 10,000 HP", lambda: self.set_health(10000))],
                                       custom_entry=True, setter=self.set_health)

        self.lbl_shield = self.add_row(f, 2, "Shield:", "shield_current",
                                       [("Set 1,000 Shield", lambda: self.mem.write_float("shield_current", 1000))],
                                       custom_entry=True, setter=lambda v: self.mem.write_float("shield_current", v))

        self.lbl_art_cd = self.add_row(f, 3, "Artifact Cooldown:", "artifact_cd",
                                       [("Fast (0.05x)", self.set_instant_artifact),
                                        ("Reset (1.0x)", self.reset_artifact_cd)])

        self.lbl_pot_cd = self.add_row(f, 4, "Potion Cooldown:", "potion_base_cd_cur",
                                       [("Instant (0.1s)", self.set_instant_potion),
                                        ("Reset (30s)", self.reset_potion)],
                                       custom_entry=True, setter=self.set_potion_cd)

        # Infinite Potions Toggle Row
        pot_frame = tk.Frame(f, bg="#1e1e2e", pady=2)
        pot_frame.grid(row=5, column=0, columnspan=5, sticky='w')
        self.btn_infinite_potions = tk.Button(pot_frame, text="INFINITE POTIONS (OFF)", font=('Segoe UI', 9, 'bold'),
                                              bg="#313244", fg="#f38ba8", padx=12, pady=4, relief='flat',
                                              command=self.toggle_infinite_potions)
        self.btn_infinite_potions.pack(side='left')
        lbl_pot_hint = tk.Label(pot_frame, text="Infinite Potions: Locks potion charges to 5 and auto-recharges instantly",
                                bg="#1e1e2e", fg="#a6adc8", font=('Segoe UI', 8))
        lbl_pot_hint.pack(side='left', padx=10)

        self.lbl_crit = self.add_row(f, 6, "Critical Hit Chance (1.0=100%):", "crit_chance",
                                     [("100% Crit", lambda: self.mem.write_float("crit_chance", 1.0)),
                                      ("500% Crit Dmg", lambda: self.mem.write_float("crit_multiplier", 5.0))],
                                     custom_entry=True, setter=lambda v: self.mem.write_float("crit_chance", v))

        self.lbl_melee_spd = self.add_row(f, 7, "Melee Attack Speed:", "melee_speed",
                                          [("2x Speed", lambda: self.mem.write_float("melee_speed", 2.0)),
                                           ("5x Speed", lambda: self.mem.write_float("melee_speed", 5.0)),
                                           ("Reset", lambda: self.mem.write_float("melee_speed", 1.0))],
                                          custom_entry=True, setter=lambda v: self.mem.write_float("melee_speed", v))

        self.lbl_reach = self.add_row(f, 8, "Melee Reach / Range:", "melee_reach",
                                      [("Super (2500)", lambda: self.mem.write_float("melee_reach", 2500.0)),
                                       ("Reset (250)", lambda: self.mem.write_float("melee_reach", 250.0))],
                                      custom_entry=True, setter=lambda v: self.mem.write_float("melee_reach", v))

        self.lbl_multi = self.add_row(f, 9, "MultiShot (Chance & Arrows):", "multishot_chance",
                                      [("100% + 5 Arrows", self.enable_multishot)])

    def set_instant_artifact(self):
        self.mem.write_float("artifact_cd_base", 0.05)
        self.mem.write_float("artifact_cd", 0.05)

    def reset_artifact_cd(self):
        self.mem.write_float("artifact_cd_base", 1.0)
        self.mem.write_float("artifact_cd", 1.0)

    def set_potion_cd(self, val):
        val = float(val)
        val = max(0.05, val)
        self.mem.write_float("potion_base_cd_base", val)
        self.mem.write_float("potion_base_cd_cur", val)
        self.mem.write_float("potion_cd_base", 1.0)
        self.mem.write_float("potion_cd", 1.0)
        self.mem.write_float("potion_max_charges_base", 5.0)
        self.mem.write_float("potion_max_charges_cur", 5.0)
        self.mem.write_float("potion_charges_base", 5.0)
        self.mem.write_float("potion_charges_cur", 5.0)

    def set_instant_potion(self):
        # 0.1s base cd and 0.05 multiplier = 5ms duration, safely triggering UE4 timer delegate
        self.mem.write_float("potion_base_cd_base", 0.1)
        self.mem.write_float("potion_base_cd_cur", 0.1)
        self.mem.write_float("potion_cd_base", 0.05)
        self.mem.write_float("potion_cd", 0.05)
        self.mem.write_float("potion_max_charges_base", 5.0)
        self.mem.write_float("potion_max_charges_cur", 5.0)
        self.mem.write_float("potion_charges_base", 5.0)
        self.mem.write_float("potion_charges_cur", 5.0)

    def reset_potion(self):
        self.mem.write_float("potion_base_cd_base", 30.0)
        self.mem.write_float("potion_base_cd_cur", 30.0)
        self.mem.write_float("potion_cd_base", 1.0)
        self.mem.write_float("potion_cd", 1.0)
        self.mem.write_float("potion_max_charges_base", 1.0)
        self.mem.write_float("potion_max_charges_cur", 1.0)
        self.mem.write_float("potion_charges_base", 1.0)
        self.mem.write_float("potion_charges_cur", 1.0)

    def toggle_infinite_potions(self):
        self.infinite_potions_active = not self.infinite_potions_active
        if self.infinite_potions_active:
            self.btn_infinite_potions.config(text="INFINITE POTIONS: ON", bg="#a6e3a1", fg="#11111b")
            self.set_instant_potion()
            self.apply_infinite_potions()
        else:
            self.btn_infinite_potions.config(text="INFINITE POTIONS (OFF)", bg="#313244", fg="#f38ba8")

    def apply_infinite_potions(self):
        self.mem.write_float("potion_max_charges_base", 5.0)
        self.mem.write_float("potion_max_charges_cur", 5.0)
        self.mem.write_float("potion_charges_base", 5.0)
        self.mem.write_float("potion_charges_cur", 5.0)

    def toggle_god_mode(self):
        self.god_mode_active = not self.god_mode_active
        if self.god_mode_active:
            self.btn_god.config(text="GOD MODE: ACTIVE (IMMUNE)", bg="#a6e3a1", fg="#11111b")
            self.apply_god_mode()
        else:
            self.btn_god.config(text="TOGGLE GOD MODE (OFF)", bg="#313244", fg="#f38ba8")
            self.mem.write_float("damage_resist", 1.0)
            self.mem.write_byte("actor_invincible", 116)

    def apply_god_mode(self):
        h_max = self.mem.read_float("health_max") or 100.0
        self.mem.write_float("health_current", h_max)
        self.mem.write_float("shield_current", 100.0)
        self.mem.write_float("damage_resist", 0.0)
        self.mem.write_byte("actor_invincible", 112)

    def full_heal(self):
        h_max = self.mem.read_float("health_max") or 100.0
        self.mem.write_float("health_current", h_max)

    def set_health(self, val):
        self.mem.write_float("health_max", val)
        self.mem.write_float("health_current", val)

    def enable_multishot(self):
        self.mem.write_float("multishot_chance", 1.0)
        self.mem.write_float("multishot_count", 5.0)

    # ==========================================
    # Tab 3: Movement
    # ==========================================
    def build_movement_tab(self):
        f = self.tab_movement

        # Movement Speed Multiplier (Writes both Base and Cur + Lock option)
        self.lbl_move_mult = self.add_row(f, 0, "Speed Multiplier (GAS):", "move_mult_cur",
                                          [("1.5x", lambda: self.set_speed(1.5)),
                                           ("2.0x", lambda: self.set_speed(2.0)),
                                           ("3.0x", lambda: self.set_speed(3.0)),
                                           ("Reset (1.0)", lambda: self.set_speed(1.0))],
                                          custom_entry=True, setter=self.set_speed)

        # Lock Speed Multiplier Toggle Row (prevents combat reset)
        speed_lock_frame = tk.Frame(f, bg="#1e1e2e", pady=2)
        speed_lock_frame.grid(row=1, column=0, columnspan=5, sticky='w')
        self.btn_lock_speed = tk.Button(speed_lock_frame, text="LOCK SPEED (OFF)", font=('Segoe UI', 9, 'bold'),
                                        bg="#313244", fg="#f38ba8", padx=12, pady=4, relief='flat',
                                        command=self.toggle_lock_speed)
        self.btn_lock_speed.pack(side='left')
        lbl_speed_hint = tk.Label(speed_lock_frame, text="Locks speed multiplier so attacks / montages cannot reset speed to 1.0",
                                  bg="#1e1e2e", fg="#a6adc8", font=('Segoe UI', 8))
        lbl_speed_hint.pack(side='left', padx=10)

        # Jump Height (Jump Z Velocity)
        self.lbl_jump = self.add_row(f, 2, "Jump Height (Default: 1440):", "jump_velocity",
                                     [("High (2200)", lambda: self.mem.write_float("jump_velocity", 2200.0)),
                                      ("Super (3000)", lambda: self.mem.write_float("jump_velocity", 3000.0)),
                                      ("Reset (1440)", lambda: self.mem.write_float("jump_velocity", 1440.0))],
                                     custom_entry=True, setter=lambda v: self.mem.write_float("jump_velocity", v))

        # Gravity Scale
        self.lbl_grav = self.add_row(f, 3, "Gravity Scale (Default: 1.2):", "gravity",
                                     [("Moon (0.4)", lambda: self.mem.write_float("gravity", 0.4)),
                                      ("Low (0.7)", lambda: self.mem.write_float("gravity", 0.7)),
                                      ("Reset (1.2)", lambda: self.mem.write_float("gravity", 1.2))],
                                     custom_entry=True, setter=lambda v: self.mem.write_float("gravity", v))

        # Roll Cooldown
        self.lbl_roll = self.add_row(f, 4, "Roll Cooldown:", "roll_cd",
                                     [("Instant Roll (0.1s)", self.set_instant_roll),
                                      ("Reset (2.5s)", self.reset_roll)],
                                     custom_entry=True, setter=self.set_roll_cd)

        # Infinite Roll Toggle Row
        roll_frame = tk.Frame(f, bg="#1e1e2e", pady=2)
        roll_frame.grid(row=5, column=0, columnspan=5, sticky='w')
        self.btn_infinite_roll = tk.Button(roll_frame, text="INFINITE ROLL (OFF)", font=('Segoe UI', 9, 'bold'),
                                           bg="#313244", fg="#f38ba8", padx=12, pady=4, relief='flat',
                                           command=self.toggle_infinite_roll)
        self.btn_infinite_roll.pack(side='left')
        lbl_roll_hint = tk.Label(roll_frame, text="Infinite Roll: Continually keeps roll charges at 5 for nonstop tumbling",
                                 bg="#1e1e2e", fg="#a6adc8", font=('Segoe UI', 8))
        lbl_roll_hint.pack(side='left', padx=10)

        # Time Dilation (Player Speedhack)
        self.lbl_time = self.add_row(f, 6, "Time Dilation (Game Speed):", "time_dilation",
                                     [("1.25x", lambda: self.mem.write_float("time_dilation", 1.25)),
                                      ("1.5x", lambda: self.mem.write_float("time_dilation", 1.5)),
                                      ("Reset (1.0)", lambda: self.mem.write_float("time_dilation", 1.0))],
                                     custom_entry=True, setter=lambda v: self.mem.write_float("time_dilation", v))

    def set_roll_cd(self, val):
        val = float(val)
        val = max(0.05, val)
        self.mem.write_float("roll_cd_base", val)
        self.mem.write_float("roll_cd", val)
        self.mem.write_float("roll_max_charges_base", 5.0)
        self.mem.write_float("roll_max_charges_cur", 5.0)
        self.mem.write_float("roll_charges_base", 5.0)
        self.mem.write_float("roll_charges_cur", 5.0)

    def set_instant_roll(self):
        # 0.1s cooldown completes in 1-2 frames without getting stuck, and provides 5 charges
        self.mem.write_float("roll_cd_base", 0.1)
        self.mem.write_float("roll_cd", 0.1)
        self.mem.write_float("roll_max_charges_base", 5.0)
        self.mem.write_float("roll_max_charges_cur", 5.0)
        self.mem.write_float("roll_charges_base", 5.0)
        self.mem.write_float("roll_charges_cur", 5.0)

    def reset_roll(self):
        self.mem.write_float("roll_cd_base", 2.5)
        self.mem.write_float("roll_cd", 2.5)
        self.mem.write_float("roll_max_charges_base", 1.0)
        self.mem.write_float("roll_max_charges_cur", 1.0)
        self.mem.write_float("roll_charges_base", 1.0)
        self.mem.write_float("roll_charges_cur", 1.0)

    def toggle_infinite_roll(self):
        self.infinite_roll_active = not self.infinite_roll_active
        if self.infinite_roll_active:
            self.btn_infinite_roll.config(text="INFINITE ROLL: ON", bg="#a6e3a1", fg="#11111b")
            self.set_instant_roll()
            self.apply_infinite_roll()
        else:
            self.btn_infinite_roll.config(text="INFINITE ROLL (OFF)", bg="#313244", fg="#f38ba8")

    def apply_infinite_roll(self):
        self.mem.write_float("roll_max_charges_base", 5.0)
        self.mem.write_float("roll_max_charges_cur", 5.0)
        self.mem.write_float("roll_charges_base", 5.0)
        self.mem.write_float("roll_charges_cur", 5.0)

    def set_speed(self, val):
        val = float(val)
        self.locked_speed_val = val
        self.mem.write_float("move_mult_base", val)
        self.mem.write_float("move_mult_cur", val)

    def toggle_lock_speed(self):
        self.lock_speed_active = not self.lock_speed_active
        if self.lock_speed_active:
            cur = self.mem.read_float("move_mult_cur") or 1.0
            if cur > 1.0:
                self.locked_speed_val = cur
            self.btn_lock_speed.config(text=f"SPEED LOCKED ({self.locked_speed_val:.1f}x)", bg="#a6e3a1", fg="#11111b")
            self.apply_lock_speed()
        else:
            self.btn_lock_speed.config(text="LOCK SPEED (OFF)", bg="#313244", fg="#f38ba8")

    def apply_lock_speed(self):
        self.mem.write_float("move_mult_base", self.locked_speed_val)
        self.mem.write_float("move_mult_cur", self.locked_speed_val)

    # ==========================================
    # Tab 4: Progression
    # ==========================================
    def build_progression_tab(self):
        f = self.tab_progression

        # Master Loot Multiplier (Synchronizes Drops + Duplication + Engine Payouts Cap)
        self.lbl_master_loot = self.add_row(f, 0, "Master Loot Multiplier:", "loot_multiplier",
                                            [("2x Loot", lambda: self.set_master_loot(2.0)),
                                             ("3x Loot", lambda: self.set_master_loot(3.0)),
                                             ("5x Loot", lambda: self.set_master_loot(5.0)),
                                             ("10x Loot", lambda: self.set_master_loot(10.0)),
                                             ("Reset (1x)", lambda: self.set_master_loot(1.0))],
                                            custom_entry=True, setter=self.set_master_loot)

        # Drop Duplication Chance
        self.lbl_dup = self.add_row(f, 1, "Drop Duplication Chance:", "drop_duplication",
                                    [("2x (100%)", lambda: self.set_drop_duplication(1.0)),
                                     ("3x (200%)", lambda: self.set_drop_duplication(2.0)),
                                     ("5x (400%)", lambda: self.set_drop_duplication(4.0)),
                                     ("10x (900%)", lambda: self.set_drop_duplication(9.0)),
                                     ("Reset (0%)", lambda: self.set_drop_duplication(0.0))],
                                    custom_entry=True, setter=self.set_drop_duplication)

        # Max Loot Payouts Cap (Internal Engine Drop Iteration Limit)
        self.lbl_max_payouts = self.add_row(f, 2, "Max Loot Payouts Cap:", "max_payouts_cur",
                                            [("Default (1)", lambda: self.set_max_payouts(1.0)),
                                             ("5 Payouts", lambda: self.set_max_payouts(5.0)),
                                             ("10 Payouts", lambda: self.set_max_payouts(10.0)),
                                             ("50 Payouts", lambda: self.set_max_payouts(50.0))],
                                            custom_entry=True, setter=self.set_max_payouts)

        # Looting Drop Multiplier
        self.lbl_loot = self.add_row(f, 3, "Looting Drop Multiplier:", "loot_multiplier",
                                     [("5x Drops", lambda: self.set_looting_multiplier(5.0)),
                                      ("10x Drops", lambda: self.set_looting_multiplier(10.0)),
                                      ("25x Drops", lambda: self.set_looting_multiplier(25.0)),
                                      ("Reset (0)", lambda: self.set_looting_multiplier(0.0))],
                                     custom_entry=True, setter=self.set_looting_multiplier)

        # Rarity Bonus Chance
        self.lbl_rarity = self.add_row(f, 4, "Rarity Bonus Chance:", "rarity_bonus",
                                       [("100% Unique/Rare", lambda: self.set_rarity_bonus(1.0)),
                                        ("Reset (0)", lambda: self.set_rarity_bonus(0.0))],
                                       custom_entry=True, setter=self.set_rarity_bonus)

        # Character Level
        self.lbl_level = self.add_row(f, 5, "Character Level:", "level",
                                      [("Level 50", lambda: self.mem.write_float("level", 50.0)),
                                       ("Level 100", lambda: self.mem.write_float("level", 100.0))],
                                      custom_entry=True, setter=lambda v: self.mem.write_float("level", v))

        # Current XP
        self.lbl_xp = self.add_row(f, 6, "Current XP:", "xp_current",
                                   [("+10,000 XP", lambda: self.adjust_xp(10000.0)),
                                    ("+50,000 XP", lambda: self.adjust_xp(50000.0))],
                                   custom_entry=True, setter=lambda v: self.mem.write_float("xp_current", v))

        # Vendors
        self.lbl_vendor = self.add_row(f, 7, "Vendor Upgrades & Restock:", "merchant_charges",
                                       [("Max All Vendors", self.max_all_vendors)])

    def set_master_loot(self, mult):
        mult = float(mult)
        if mult <= 1.0:
            self.mem.write_float("drop_dup_base", 0.0)
            self.mem.write_float("drop_duplication", 0.0)
            self.mem.write_float("max_payouts_base", 1.0)
            self.mem.write_float("max_payouts_cur", 1.0)
            self.mem.write_float("loot_mult_base", 0.0)
            self.mem.write_float("loot_multiplier", 0.0)
            self.mem.write_float("drop_chance_base", 0.0)
            self.mem.write_float("drop_chance", 0.0)
        else:
            dup_val = mult - 1.0
            payout_val = mult
            self.mem.write_float("drop_dup_base", dup_val)
            self.mem.write_float("drop_duplication", dup_val)
            self.mem.write_float("max_payouts_base", payout_val)
            self.mem.write_float("max_payouts_cur", payout_val)
            self.mem.write_float("loot_mult_base", mult)
            self.mem.write_float("loot_multiplier", mult)
            self.mem.write_float("drop_chance_base", mult)
            self.mem.write_float("drop_chance", mult)

    def set_drop_duplication(self, val):
        val = float(val)
        self.mem.write_float("drop_dup_base", val)
        self.mem.write_float("drop_duplication", val)
        # Ensure engine MaximumLootingPayouts is at least val + 1 so duplication isn't capped
        cur_payouts = self.mem.read_float("max_payouts_cur") or 1.0
        needed = max(1.0, val + 1.0)
        if cur_payouts < needed:
            self.mem.write_float("max_payouts_base", needed)
            self.mem.write_float("max_payouts_cur", needed)

    def set_max_payouts(self, val):
        val = float(val)
        self.mem.write_float("max_payouts_base", val)
        self.mem.write_float("max_payouts_cur", val)

    def set_looting_multiplier(self, val):
        val = float(val)
        self.mem.write_float("loot_mult_base", val)
        self.mem.write_float("loot_multiplier", val)

    def set_rarity_bonus(self, val):
        val = float(val)
        self.mem.write_float("rarity_bonus_base", val)
        self.mem.write_float("rarity_bonus", val)

    def adjust_xp(self, delta):
        cur = self.mem.read_float("xp_current") or 0.0
        self.mem.write_float("xp_current", cur + delta)

    def max_all_vendors(self):
        self.mem.write_float("merchant_charges", 99.0)
        self.mem.write_float("merchant_upg", 3.0)
        self.mem.write_float("enchantsmith_upg", 3.0)
        self.mem.write_float("blacksmith_upg", 3.0)

    # ==========================================
    # Tab 5: Developer
    # ==========================================
    def build_developer_tab(self):
        f = self.tab_developer

        self.lbl_debug = self.add_row(f, 0, "EnableDebug Flag (PC+0x94D):", "debug_flag",
                                      [("Enable (1)", lambda: self.mem.write_byte("debug_flag", 1)),
                                       ("Disable (0)", lambda: self.mem.write_byte("debug_flag", 0))], is_byte=True)

        self.lbl_debug_ui = self.add_row(f, 1, "DebugUIControls (PC+0x748):", "debug_ui",
                                         [("Enable (1)", lambda: self.mem.write_byte("debug_ui", 1)),
                                          ("Disable (0)", lambda: self.mem.write_byte("debug_ui", 0))], is_byte=True)

        self.lbl_fov = self.add_row(f, 2, "Camera FOV (Default: 90):", "camera_fov",
                                    [("FOV 100", lambda: self.mem.write_float("camera_fov", 100.0)),
                                     ("FOV 110", lambda: self.mem.write_float("camera_fov", 110.0)),
                                     ("FOV 120", lambda: self.mem.write_float("camera_fov", 120.0)),
                                     ("Reset (90)", lambda: self.mem.write_float("camera_fov", 90.0))],
                                    custom_entry=True, setter=lambda v: self.mem.write_float("camera_fov", v))

    # ==========================================
    # GUI Helpers
    # ==========================================
    def add_row(self, parent, row_idx, label_text, key, buttons, custom_entry=False, is_byte=False, setter=None):
        lbl_title = tk.Label(parent, text=label_text, bg="#1e1e2e", fg="#cdd6f4", font=('Segoe UI', 9, 'bold'))
        lbl_title.grid(row=row_idx, column=0, sticky='w', pady=6, padx=(0, 10))

        lbl_val = tk.Label(parent, text="---", bg="#1e1e2e", fg="#f9e2af", font=('Consolas', 10, 'bold'), width=11, anchor='w')
        lbl_val.grid(row=row_idx, column=1, sticky='w', pady=6, padx=(0, 8))

        btn_frame = tk.Frame(parent, bg="#1e1e2e")
        btn_frame.grid(row=row_idx, column=2, sticky='w', pady=6)

        if custom_entry:
            entry_var = tk.StringVar()
            entry = tk.Entry(btn_frame, textvariable=entry_var, width=7, bg="#313244", fg="#cdd6f4",
                             insertbackground="#cdd6f4", relief='flat', font=('Consolas', 9))
            entry.pack(side='left', padx=(0, 4))

            def on_set():
                val = entry_var.get().strip()
                if val:
                    try:
                        num = float(val) if not is_byte else int(val)
                        if setter:
                            setter(num)
                        elif is_byte:
                            self.mem.write_byte(key, num)
                        else:
                            self.mem.write_float(key, num)
                    except ValueError:
                        pass

            btn_set = ttk.Button(btn_frame, text="Set", command=on_set, width=4)
            btn_set.pack(side='left', padx=(0, 8))

        for text, cmd in buttons:
            b = ttk.Button(btn_frame, text=text, command=cmd)
            b.pack(side='left', padx=3)

        return (lbl_val, key, is_byte)

    def refresh_loop(self):
        if not self.mem.h_proc:
            self.try_connect()

        if self.mem.h_proc:
            # God Mode continuous lock
            if self.god_mode_active:
                self.apply_god_mode()

            # Freeze Souls continuous lock
            if self.freeze_souls_active:
                self.apply_freeze_souls()

            # Auto-Refill Ammo continuous lock
            if self.auto_refill_ammo_active:
                self.apply_auto_refill()

            # Lock Speed Multiplier continuous lock (prevents attack montage reset)
            if self.lock_speed_active:
                self.apply_lock_speed()

            # Infinite Potions continuous lock
            if self.infinite_potions_active:
                self.apply_infinite_potions()

            # Infinite Roll continuous lock
            if self.infinite_roll_active:
                self.apply_infinite_roll()

            for tab_rows in [
                [self.lbl_emeralds, self.lbl_springstone, self.lbl_ench, self.lbl_curr_mult, self.lbl_souls, self.lbl_ammo, self.lbl_rapid],
                [self.lbl_health, self.lbl_shield, self.lbl_art_cd, self.lbl_pot_cd, self.lbl_crit, self.lbl_melee_spd, self.lbl_reach, self.lbl_multi],
                [self.lbl_move_mult, self.lbl_jump, self.lbl_grav, self.lbl_roll, self.lbl_time],
                [self.lbl_master_loot, self.lbl_dup, self.lbl_max_payouts, self.lbl_loot, self.lbl_rarity, self.lbl_level, self.lbl_xp, self.lbl_vendor],
                [self.lbl_debug, self.lbl_debug_ui, self.lbl_fov]
            ]:
                for row_data in tab_rows:
                    lbl, key, is_byte = row_data
                    if is_byte:
                        v = self.mem.read_byte(key)
                        lbl.config(text=str(v) if v is not None else "---")
                    else:
                        v = self.mem.read_float(key)
                        if v is not None:
                            if key == "emerald_increase_cur":
                                mult_disp = v + 1.0
                                lbl.config(text=f"{mult_disp:.1f}x")
                            elif abs(v) >= 10:
                                lbl.config(text=f"{v:,.1f}")
                            else:
                                lbl.config(text=f"{v:.2f}")
                        else:
                            lbl.config(text="---")

        self.after(250, self.refresh_loop)

if __name__ == "__main__":
    app = TrainerApp()
    app.mainloop()
