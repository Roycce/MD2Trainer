"""
Minecraft Dungeons II - Process Memory Manager & Win32 I/O Layer
Target: Dungeons-WinGDK-Shipping.exe (Singleplayer / Offline)
"""

import ctypes
import math
import re
import struct
import sys
from ctypes import wintypes

from trainer_offsets import (
    CHAINS,
    ENGINE_OFFSET,
    FNAMES_BLOCKS_OFFSET,
    RARITY_INDICES,
)

TARGET_PROCESS_NAMES = (
    "dungeons-wingdk-shipping.exe",
    "dungeons-win64-shipping.exe",
    "dungeons.exe",
)

if sys.platform == "win32":
    k32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi

    # Process Memory Access Constants
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    PROCESS_VM_WRITE = 0x0020
    PROCESS_VM_OPERATION = 0x0008
    PROCESS_ACCESS = (
        PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION
    )

    # Win32 API Function Signatures
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    k32.CloseHandle.restype = wintypes.BOOL

    k32.K32EnumProcesses.argtypes = [
        ctypes.POINTER(wintypes.DWORD),
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    k32.K32EnumProcesses.restype = wintypes.BOOL

    k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    k32.GetExitCodeProcess.restype = wintypes.BOOL

    for api in (k32.ReadProcessMemory, k32.WriteProcessMemory):
        api.argtypes = [
            wintypes.HANDLE,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
        ]
        api.restype = wintypes.BOOL

    psapi.EnumProcessModulesEx.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(wintypes.HMODULE),
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        wintypes.DWORD,
    ]
    psapi.EnumProcessModulesEx.restype = wintypes.BOOL

    psapi.GetModuleBaseNameA.argtypes = [
        wintypes.HANDLE,
        wintypes.HMODULE,
        ctypes.POINTER(ctypes.c_char),
        wintypes.DWORD,
    ]
    psapi.GetModuleBaseNameA.restype = wintypes.DWORD
else:
    from unittest.mock import MagicMock

    k32 = MagicMock()
    psapi = MagicMock()
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    PROCESS_VM_WRITE = 0x0020
    PROCESS_VM_OPERATION = 0x0008
    PROCESS_ACCESS = (
        PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION
    )


class MemoryAccessError(RuntimeError):
    """An operation cannot be completed against the game process."""


def finite_float(value):
    """Validate that value is a finite number representable in 32-bit float range."""
    value = float(value)
    if not math.isfinite(value) or abs(value) > 3.4028234663852886e38:
        raise ValueError("Enter a finite number within the 32-bit float range.")
    return value


def classify_session_role(role):
    if role == 3:
        return "local"
    if role in (1, 2):
        return "client"
    return "unknown"


class MemoryManager:
    """Manages process attachment, memory reads/writes, pointer chains, and game structures."""

    def __init__(self):
        self.pid = None
        self.process_name = "Dungeons-WinGDK-Shipping.exe"
        self.base_addr = None
        self.h_proc = None
        self.blocks_addr = None
        self.engine_offset = ENGINE_OFFSET
        self.fnames_blocks_offset = FNAMES_BLOCKS_OFFSET
        self.last_error = "Game not found. Waiting for game process..."

    def close(self):
        if self.h_proc:
            k32.CloseHandle(self.h_proc)
            self.h_proc = None
        self.pid = None
        self.base_addr = None
        self.blocks_addr = None
        self.engine_offset = ENGINE_OFFSET
        self.fnames_blocks_offset = FNAMES_BLOCKS_OFFSET

    def is_alive(self):
        if not self.h_proc:
            return False
        code = wintypes.DWORD()
        if not k32.GetExitCodeProcess(self.h_proc, ctypes.byref(code)) or code.value != 259:
            self.close()
            self.last_error = "Game closed or connection lost. Waiting to reconnect..."
            return False
        return True

    def attach(self):
        self.close()
        self.last_error = "Game not found. Waiting for game process..."
        bytes_needed = wintypes.DWORD()
        capacity = 2048
        while True:
            pids = (wintypes.DWORD * capacity)()
            if not k32.K32EnumProcesses(pids, ctypes.sizeof(pids), ctypes.byref(bytes_needed)):
                self.last_error = (
                    f"Cannot list processes (Windows error {ctypes.get_last_error()})."
                )
                return False
            if bytes_needed.value < ctypes.sizeof(pids):
                break
            capacity *= 2
        process_count = bytes_needed.value // ctypes.sizeof(wintypes.DWORD)

        for i in range(process_count):
            pid = pids[i]
            if pid == 0:
                continue
            h = k32.OpenProcess(0x0410, False, pid)
            if not h:
                continue
            try:
                mods = (wintypes.HMODULE * 1)()
                cb = wintypes.DWORD()
                if psapi.EnumProcessModulesEx(h, mods, ctypes.sizeof(mods), ctypes.byref(cb), 3):
                    mod_name = (ctypes.c_char * 260)()
                    psapi.GetModuleBaseNameA(h, mods[0], mod_name, 260)
                    proc_str = mod_name.value.decode(errors="ignore")
                    if proc_str.lower() in TARGET_PROCESS_NAMES:
                        self.pid = pid
                        self.process_name = proc_str
                        self.base_addr = mods[0]
                        break
            finally:
                k32.CloseHandle(h)

        if not self.pid:
            return False

        self.h_proc = k32.OpenProcess(PROCESS_ACCESS, False, self.pid)
        if self.h_proc:
            self.engine_offset = ENGINE_OFFSET
            self.fnames_blocks_offset = FNAMES_BLOCKS_OFFSET
            self.blocks_addr = self.base_addr + self.fnames_blocks_offset
            return True
        else:
            self.last_error = (
                f"Process found ({self.process_name}), but access denied (Windows error {ctypes.get_last_error()}). "
                f"Try running as Administrator."
            )
            self.close()
            return False

    def read_memory(self, address, size):
        if not self.h_proc or not address:
            return None
        buf = ctypes.create_string_buffer(size)
        transferred = ctypes.c_size_t()
        if (
            k32.ReadProcessMemory(
                self.h_proc, ctypes.c_void_p(address), buf, size, ctypes.byref(transferred)
            )
            and transferred.value == size
        ):
            return buf.raw
        return None

    def write_memory(self, address, data):
        if not self.h_proc or not address:
            return False
        bytes_written = ctypes.c_size_t()
        return bool(
            k32.WriteProcessMemory(
                self.h_proc, ctypes.c_void_p(address), data, len(data), ctypes.byref(bytes_written)
            )
            and bytes_written.value == len(data)
        )

    def is_engine_candidate(self, cand_offset):
        """
        Verify if a given RVA offset in the main module points to a valid GEngine instance.
        Validates the 5-level pointer hierarchy:
        GEngine -> GameInstance (+0x1248) -> LocalPlayers (+0x38) -> LocalPlayer (+0x0) -> PlayerController (+0x30)
        """
        if not self.h_proc or not self.base_addr or not cand_offset:
            return False
        # 1. GEngine pointer
        gengine = self.read_ptr(self.base_addr + cand_offset)
        if not (0x10000 <= gengine <= 0x7FFFFFFFFFFF):
            return False
        # 2. GameInstance pointer (+0x1248)
        game_instance = self.read_ptr(gengine + 0x1248)
        if not (0x10000 <= game_instance <= 0x7FFFFFFFFFFF):
            return False
        # 3. LocalPlayers pointer (+0x38)
        local_players = self.read_ptr(game_instance + 0x38)
        if not (0x10000 <= local_players <= 0x7FFFFFFFFFFF):
            return False
        # 4. LocalPlayer[0] pointer (+0x0)
        local_player = self.read_ptr(local_players + 0x0)
        if not (0x10000 <= local_player <= 0x7FFFFFFFFFFF):
            return False
        # 5. PlayerController pointer (+0x30)
        player_controller = self.read_ptr(local_player + 0x30)
        if not (0x10000 <= player_controller <= 0x7FFFFFFFFFFF):
            return False
        return True

    def is_fnames_candidate(self, cand_offset):
        """Verify if a given RVA offset points to a valid FNamePool.Blocks table."""
        if not self.h_proc or not self.base_addr or not cand_offset:
            return False
        block0 = self.read_ptr(self.base_addr + cand_offset)
        if not (0x10000 <= block0 <= 0x7FFFFFFFFFFF):
            return False
        chunk_hdr = self.read_memory(block0, 32)
        if not chunk_hdr:
            return False
        if b"None" in chunk_hdr or b"ByteProperty" in chunk_hdr:
            return True
        hdr = struct.unpack("<H", chunk_hdr[:2])[0]
        length = min(hdr >> 6, 250)
        if 1 <= length <= 64:
            text = chunk_hdr[2 : 2 + length]
            if all(32 <= b < 127 for b in text):
                return True
        return False

    def get_module_sections(self):
        """Parse PE headers to locate .text, .data, and other sections."""
        sections = []
        dos_hdr = self.read_memory(self.base_addr, 0x40)
        if not dos_hdr or dos_hdr[:2] != b"MZ":
            return sections
        e_lfanew = struct.unpack("<I", dos_hdr[0x3C:0x40])[0]
        nt_hdr = self.read_memory(self.base_addr + e_lfanew, 0x108)
        if not nt_hdr or nt_hdr[:4] != b"PE\x00\x00":
            return sections
        num_sections = struct.unpack("<H", nt_hdr[6:8])[0]
        size_opt = struct.unpack("<H", nt_hdr[20:22])[0]
        sec_start = self.base_addr + e_lfanew + 24 + size_opt
        sec_raw = self.read_memory(sec_start, num_sections * 40)
        if not sec_raw:
            return sections
        for i in range(num_sections):
            chunk = sec_raw[i * 40 : (i + 1) * 40]
            name = chunk[:8].rstrip(b"\x00").decode("latin1", errors="ignore")
            vsize, vrva = struct.unpack("<II", chunk[8:16])
            sections.append({"name": name, "rva": vrva, "size": vsize})
        return sections

    def find_engine_offset(self):
        """Dynamically detect GEngine offset by testing candidate chains, AOB scanning, and data section inspection."""
        if self.is_engine_candidate(ENGINE_OFFSET):
            return ENGINE_OFFSET

        sections = self.get_module_sections()
        text_secs = [s for s in sections if s["name"].lower() in (".text", "code")]
        if not text_secs and sections:
            text_secs = [sections[0]]

        patterns = [
            # Pattern 1: Accessing GameInstance (0x1248) from GEngine
            re.compile(
                b"\x48\x8b[\x05\x0d\x15\x1d\x25\x2d\x35\x3d](.{4})\x48\x8b[\x80-\xbf]\x48\x12\x00\x00"
            ),
            # Pattern 2: GEngine check
            re.compile(b"\x48\x8b\x0d(.{4})\x48\x85\xc9\x74"),
            # Pattern 3: GEngine mov cs:GEngine, rax
            re.compile(b"\x48\x89\x05(.{4})\x48\x85"),
        ]

        chunk_size = 2 * 1024 * 1024
        for sec in text_secs:
            sec_rva = sec["rva"]
            sec_size = sec["size"]
            offset = 0
            while offset < sec_size:
                read_len = min(chunk_size, sec_size - offset)
                chunk = self.read_memory(self.base_addr + sec_rva + offset, read_len)
                if not chunk:
                    break
                for pat in patterns:
                    for match in pat.finditer(chunk):
                        rel32 = struct.unpack("<i", match.group(1))[0]
                        cand_rva = sec_rva + offset + match.start() + 7 + rel32
                        if self.is_engine_candidate(cand_rva):
                            return cand_rva
                if read_len < chunk_size:
                    break
                offset += chunk_size - 32

        # Direct search in data sections (.data / .bss)
        data_secs = [s for s in sections if s["name"].lower() in (".data", ".bss")]
        for sec in data_secs:
            sec_rva = sec["rva"]
            sec_size = sec["size"]
            offset = 0
            while offset < sec_size:
                read_len = min(chunk_size, sec_size - offset)
                chunk = self.read_memory(self.base_addr + sec_rva + offset, read_len)
                if not chunk:
                    break
                for idx in range(0, len(chunk) - 7, 8):
                    ptr = struct.unpack_from("<Q", chunk, idx)[0]
                    if 0x10000 <= ptr <= 0x7FFFFFFFFFFF:
                        cand_rva = sec_rva + offset + idx
                        if self.is_engine_candidate(cand_rva):
                            return cand_rva
                if read_len < chunk_size:
                    break
                offset += chunk_size

        return ENGINE_OFFSET

    def find_fnames_offset(self):
        """Dynamically detect FNamePool.Blocks offset."""
        if self.is_fnames_candidate(FNAMES_BLOCKS_OFFSET):
            return FNAMES_BLOCKS_OFFSET

        sections = self.get_module_sections()
        text_secs = [s for s in sections if s["name"].lower() in (".text", "code")]
        if not text_secs and sections:
            text_secs = [sections[0]]

        patterns = [
            re.compile(b"\x48\x8d\x0d(.{4})\xe8.{4}\x4c\x8b"),
            re.compile(b"\x48\x8d\x05(.{4})\xeb"),
            re.compile(b"\x48\x8d\x0d(.{4})\x49\x63"),
            re.compile(b"\x48\x8d\x0d(.{4})\xe8"),
        ]

        chunk_size = 2 * 1024 * 1024
        for sec in text_secs:
            sec_rva = sec["rva"]
            sec_size = sec["size"]
            offset = 0
            while offset < sec_size:
                read_len = min(chunk_size, sec_size - offset)
                chunk = self.read_memory(self.base_addr + sec_rva + offset, read_len)
                if not chunk:
                    break
                for pat in patterns:
                    for match in pat.finditer(chunk):
                        rel32 = struct.unpack("<i", match.group(1))[0]
                        cand_rva = sec_rva + offset + match.start() + 7 + rel32
                        if self.is_fnames_candidate(cand_rva):
                            return cand_rva
                if read_len < chunk_size:
                    break
                offset += chunk_size - 32

        # Direct search in data sections
        data_secs = [s for s in sections if s["name"].lower() in (".data", ".rdata")]
        for sec in data_secs:
            sec_rva = sec["rva"]
            sec_size = sec["size"]
            offset = 0
            while offset < sec_size:
                read_len = min(chunk_size, sec_size - offset)
                chunk = self.read_memory(self.base_addr + sec_rva + offset, read_len)
                if not chunk:
                    break
                for idx in range(0, len(chunk) - 7, 8):
                    ptr = struct.unpack_from("<Q", chunk, idx)[0]
                    if 0x10000 <= ptr <= 0x7FFFFFFFFFFF:
                        cand_rva = sec_rva + offset + idx
                        if self.is_fnames_candidate(cand_rva):
                            return cand_rva
                if read_len < chunk_size:
                    break
                offset += chunk_size

        return FNAMES_BLOCKS_OFFSET

    def resolve_chain(self, offsets_list):
        if not self.h_proc or not self.base_addr:
            return None
        curr_addr = self.base_addr + self.engine_offset
        buf8 = ctypes.create_string_buffer(8)
        transferred = ctypes.c_size_t()
        for off_str in reversed(offsets_list):
            off = int(off_str, 16)
            res = k32.ReadProcessMemory(
                self.h_proc, ctypes.c_void_p(curr_addr), buf8, 8, ctypes.byref(transferred)
            )
            if not res or transferred.value != 8:
                return None
            ptr = struct.unpack("<Q", buf8.raw)[0]
            if not ptr or ptr < 0x10000:
                return None
            curr_addr = ptr + off
        return curr_addr

    def read_float(self, key):
        addr = self.resolve_chain(CHAINS[key])
        if not addr:
            return None
        data = self.read_memory(addr, 4)
        if data is not None:
            val = struct.unpack("<f", data)[0]
            return val if math.isfinite(val) else None
        return None

    def require_float(self, key):
        val = self.read_float(key)
        if val is None:
            raise MemoryAccessError(f"Cannot read {key}.")
        return val

    def write_float(self, key, val):
        addr = self.resolve_chain(CHAINS[key])
        if not addr:
            return False
        buf4 = struct.pack("<f", finite_float(val))
        return self.write_memory(addr, buf4)

    def read_byte(self, key):
        addr = self.resolve_chain(CHAINS[key])
        if not addr:
            return None
        data = self.read_memory(addr, 1)
        if data is not None:
            return data[0]
        return None

    def write_byte(self, key, val):
        addr = self.resolve_chain(CHAINS[key])
        if not addr:
            return False
        val_int = int(val)
        if not 0 <= val_int <= 255:
            raise ValueError("Enter a whole number between 0 and 255.")
        buf1 = struct.pack("<B", val_int)
        return self.write_memory(addr, buf1)

    # Raw Memory Primitives
    def read_ptr(self, addr):
        data = self.read_memory(addr, 8)
        if data is not None:
            return struct.unpack("<Q", data)[0]
        return 0

    def write_ptr(self, addr, val):
        return self.write_memory(addr, struct.pack("<Q", int(val)))

    def read_u32(self, addr):
        data = self.read_memory(addr, 4)
        if data is not None:
            return struct.unpack("<I", data)[0]
        return 0

    def write_u32(self, addr, val):
        return self.write_memory(addr, struct.pack("<I", int(val)))

    def read_f32(self, addr):
        data = self.read_memory(addr, 4)
        if data is not None:
            val = struct.unpack("<f", data)[0]
            return val if math.isfinite(val) else 0.0
        return 0.0

    def write_f32(self, addr, val):
        return self.write_memory(addr, struct.pack("<f", finite_float(val)))

    # FName Resolver
    def get_fname(self, comp_idx):
        if not self.h_proc or not self.blocks_addr or not comp_idx:
            return ""
        block_idx = comp_idx >> 16
        offset = comp_idx & 0xFFFF
        buf8 = self.read_memory(self.blocks_addr + block_idx * 8, 8)
        if not buf8:
            return ""
        bptr = struct.unpack("<Q", buf8)[0]
        if not bptr:
            return ""
        ebuf = self.read_memory(bptr + offset * 2, 256)
        if not ebuf:
            return ""
        hdr = struct.unpack("<H", ebuf[:2])[0]
        length = min(hdr >> 6, 250)
        return ebuf[2 : 2 + length].decode("ascii", errors="ignore")

    # Inventory & Gear Operations
    def get_equipped_gear(self):
        pawn_addr = self.resolve_chain(["2F8", "30", "0", "38", "1248"])
        if not pawn_addr:
            return []
        pawn = self.read_ptr(pawn_addr)
        if not pawn:
            return []
        inv_comp = self.read_ptr(pawn + 0xDA0)
        if not inv_comp:
            return []
        slots_data = self.read_ptr(inv_comp + 0x158 + 0x108)
        slots_count = self.read_u32(inv_comp + 0x158 + 0x110)
        if not slots_data or slots_count == 0:
            return []

        equipped = []
        for s in range(slots_count):
            slot_addr = slots_data + s * 0x50
            stag = self.get_fname(self.read_u32(slot_addr + 0xC))
            if "Equipment" in stag:
                cnt = self.read_u32(slot_addr + 0x48)
                idata = self.read_ptr(slot_addr + 0x40)
                lbl = stag.replace("SW.ItemSlot.Equipment.", "")
                if cnt > 0 and idata:
                    itag = self.get_fname(self.read_u32(idata + 0x0)).replace("SW.Item.", "")
                    rtag = self.get_fname(self.read_u32(idata + 0x14)).replace("SW.Rarity.", "")
                    pwr = self.read_f32(idata + 0x60)
                    pwr_orig = self.read_f32(idata + 0x5C)
                    lvl = self.read_u32(idata + 0x68)
                    xp = self.read_f32(idata + 0x6C)
                    equipped.append(
                        {
                            "slot_idx": s,
                            "slot_tag": stag,
                            "label": lbl,
                            "item_addr": idata,
                            "name": itag,
                            "power": pwr,
                            "power_orig": pwr_orig,
                            "rarity": rtag if rtag else "None",
                            "level": lvl,
                            "xp": xp,
                            "is_talisman": "talisman" in lbl.lower(),
                        }
                    )
        return equipped

    def set_gear_power(self, item_addr, slot_tag, power_val):
        power_val = finite_float(power_val)
        self.write_f32(item_addr + 0x5C, power_val)
        self.write_f32(item_addr + 0x60, power_val)
        if "MeleeWeapon" in slot_tag:
            self.write_float("power_melee_base", power_val)
            self.write_float("power_melee_cur", power_val)
        elif "RangedWeapon" in slot_tag:
            self.write_float("power_ranged_base", power_val)
            self.write_float("power_ranged_cur", power_val)
        elif "Armor" in slot_tag:
            self.write_float("power_armor_base", power_val)
            self.write_float("power_armor_cur", power_val)
        elif "Artifact.Slot1" in slot_tag:
            self.write_float("power_artifact0_base", power_val)
            self.write_float("power_artifact0_cur", power_val)
        elif "Artifact.Slot2" in slot_tag:
            self.write_float("power_artifact1_base", power_val)
            self.write_float("power_artifact1_cur", power_val)
        elif "Artifact.Slot3" in slot_tag:
            self.write_float("power_artifact2_base", power_val)
            self.write_float("power_artifact2_cur", power_val)
        return True

    def set_gear_rarity(self, item_addr, rarity_name):
        idx = RARITY_INDICES.get(rarity_name)
        if idx:
            return self.write_u32(item_addr + 0x14, idx)
        return False

    def set_talisman_level_xp(self, item_addr, level, xp):
        self.write_u32(item_addr + 0x68, int(level))
        self.write_f32(item_addr + 0x6C, finite_float(xp))
        return True

    def max_out_talismans(self, only_equipped=True):
        items = self.get_equipped_gear()
        count = 0
        for it in items:
            if it["is_talisman"]:
                addr = it["item_addr"]
                self.write_u32(addr + 0x68, 2)
                self.write_f32(addr + 0x6C, 100000.0)
                count += 1
        if not only_equipped:
            pawn_addr = self.resolve_chain(["2F8", "30", "0", "38", "1248"])
            if pawn_addr:
                pawn = self.read_ptr(pawn_addr)
                if pawn:
                    inv_comp = self.read_ptr(pawn + 0xDA0)
                    if inv_comp:
                        slots_data = self.read_ptr(inv_comp + 0x158 + 0x108)
                        slots_count = self.read_u32(inv_comp + 0x158 + 0x110)
                        if slots_data and slots_count > 7:
                            slot7 = slots_data + 7 * 0x50
                            cnt = self.read_u32(slot7 + 0x48)
                            idata = self.read_ptr(slot7 + 0x40)
                            inv_entry_size = 0xD8
                            for i in range(cnt):
                                t_addr = idata + i * inv_entry_size
                                self.write_u32(t_addr + 0x68, 2)
                                self.write_f32(t_addr + 0x6C, 100000.0)
                                count += 1
        return count

    def session_kind(self):
        if not self.h_proc or not self.is_alive():
            return "disconnected"
        if self.read_float("health_current") is None:
            return "loading"
        role = self.read_byte("player_role")
        return classify_session_role(role)
