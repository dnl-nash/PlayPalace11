"""GNUBG subprocess integration for Backgammon bot AI.

Manages a persistent gnubg-cli --tty subprocess for move evaluation.
Falls back to random moves when GNUBG is unavailable.
"""

from __future__ import annotations

import base64
import logging
import queue
import re
import shutil
import subprocess
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import BackgammonGameState

log = logging.getLogger(__name__)

_available: bool | None = None  # None = untested


def _find_gnubg() -> str | None:
    """Find gnubg-cli executable on PATH."""
    for name in ("gnubg-cli", "gnubg-cli.exe", "gnubg", "gnubg.exe"):
        path = shutil.which(name)
        if path:
            return path
    return None


def is_gnubg_available() -> bool:
    """Check if GNUBG binary is on PATH. Caches result after first check."""
    global _available
    if _available is not None:
        return _available
    _available = _find_gnubg() is not None
    if not _available:
        log.info("GNUBG not found on PATH; bot will use random fallback")
    return _available


# ---------------------------------------------------------------------------
# Position ID encoding
# ---------------------------------------------------------------------------

def encode_position_id(state: BackgammonGameState) -> str:
    """Encode the board as a GNUBG Position ID (14-char base64 string).

    GNUBG position key is 80 bits built from unary-encoded checker counts:
      First half: NOT-on-roll player's points 1-24 (from their perspective) + bar
      Second half: on-roll player's points 1-24 (from their perspective) + bar
    Each point: N ones followed by a zero separator. 80 bits total.
    Packed little-endian into 10 bytes, then base64-encoded (no padding).

    We always encode from the on-roll player's perspective, with the
    opponent (not-on-roll) encoded first per the GNUBG spec.
    """
    board = state.board

    # Build checker arrays from each player's perspective
    # Red: point 1 = index 0, point 24 = index 23 (positive values)
    # White: point 1 (their perspective) = index 23 (negative values)
    red_counts = []
    for i in range(24):
        red_counts.append(max(0, board.points[i]))
    red_bar = board.bar_red

    white_counts = []
    for i in range(23, -1, -1):  # White's point 1 = index 23
        white_counts.append(max(0, -board.points[i]))
    white_bar = board.bar_white

    # GNUBG format: opponent (not-on-roll) first, then on-roll player
    if state.current_color == "red":
        first_counts, first_bar = white_counts, white_bar    # opponent
        second_counts, second_bar = red_counts, red_bar       # on-roll
    else:
        first_counts, first_bar = red_counts, red_bar         # opponent
        second_counts, second_bar = white_counts, white_bar   # on-roll

    # Build bit string: for each player, 24 points + bar, unary encoded
    bits: list[int] = []
    for count in first_counts:
        bits.extend([1] * count)
        bits.append(0)
    bits.extend([1] * first_bar)
    bits.append(0)

    for count in second_counts:
        bits.extend([1] * count)
        bits.append(0)
    bits.extend([1] * second_bar)
    bits.append(0)

    # Pad to exactly 80 bits
    while len(bits) < 80:
        bits.append(0)

    # Pack into 10 bytes, little-endian bit order
    key_bytes = bytearray(10)
    for i, bit in enumerate(bits[:80]):
        if bit:
            key_bytes[i // 8] |= 1 << (i % 8)

    return base64.b64encode(bytes(key_bytes)).decode("ascii").rstrip("=")


# ---------------------------------------------------------------------------
# Hint parsing
# ---------------------------------------------------------------------------

# Matches lines like: "    1. Cubeful 0-ply    8/5 6/5                      Eq.: +0.201"
_HINT_RE = re.compile(
    r"^\s*(\d+)\.\s+Cubeful\s+\d+-ply\s+(.*?)\s+Eq\.",
)

# Individual sub-move patterns within the move string
# "8/5" or "24/18(2)" or "bar/22" or "3/off"
_SUBMOVE_RE = re.compile(
    r"(bar|\d+)/(off|\d+)(?:\((\d+)\))?"
)


def parse_hint_line(line: str) -> list[tuple[str, str, int]] | None:
    """Parse a single hint line into a list of (source, dest, count) tuples.

    Returns None if the line doesn't match.
    Source/dest are strings: "bar", "off", or point number strings.
    Count is how many checkers make that sub-move (default 1).
    """
    m = _HINT_RE.match(line)
    if not m:
        return None
    move_str = m.group(2).strip()
    submoves = []
    for sm in _SUBMOVE_RE.finditer(move_str):
        src = sm.group(1)
        dst = sm.group(2)
        count = int(sm.group(3)) if sm.group(3) else 1
        submoves.append((src, dst, count))
    return submoves if submoves else None


def hint_to_actions(
    hint_submoves: list[tuple[str, str, int]],
    color: str,
    dice: list[int] | None = None,
) -> list[tuple[int, int]]:
    """Convert parsed GNUBG hint sub-moves to (source_idx, dest_idx) pairs.

    GNUBG uses the on-roll player's perspective for point numbers.
    We convert to absolute board indices (0-23, -1=bar, 24=off).

    Compound moves (e.g. 24/14 using a 6 and a 4) are expanded into
    individual die-sized sub-moves so the game engine can apply them
    one at a time.

    Args:
        hint_submoves: List of (source, dest, count) from parse_hint_line.
        color: "red" or "white" — the player on roll.
        dice: The two dice values (e.g. [6, 4]) for expanding compound moves.

    Returns:
        List of (source_index, dest_index) pairs, one per sub-move
        (expanded for count > 1 and compound moves).
    """
    actions: list[tuple[int, int]] = []
    # Movement direction on the board: Red moves high→low, White moves low→high
    move_dir = -1 if color == "red" else 1

    for src_str, dst_str, count in hint_submoves:
        src = _gnubg_point_to_index(src_str, color)
        dst = _gnubg_point_to_index(dst_str, color)

        for _ in range(count):
            # Calculate pip distance to detect compound moves
            if dst == 24:  # bear off
                actions.append((src, dst))
                continue
            if src == -1:  # bar entry
                # Bar entry: Red enters at index 24-die, White at die-1
                # So pips = 24-dst for Red, dst+1 for White
                if color == "red":
                    pips = 24 - dst
                else:
                    pips = dst + 1
            else:
                pips = abs(dst - src)

            # Check if this is a compound move (uses more than one die)
            if dice and len(dice) >= 2 and not _is_single_die_move(pips, dice):
                # Expand into individual die-sized sub-moves
                expanded = _expand_compound_move(src, dst, pips, color, dice)
                actions.extend(expanded)
            else:
                actions.append((src, dst))

    return actions


def _is_single_die_move(pips: int, dice: list[int]) -> bool:
    """Check if the pip distance matches a single die value."""
    return pips in dice


def _expand_compound_move(
    src: int, dst: int, pips: int, color: str, dice: list[int],
) -> list[tuple[int, int]]:
    """Expand a compound move into individual die-sized sub-moves."""
    # Red moves high→low (subtract), White moves low→high (add)
    move_dir = -1 if color == "red" else 1
    d1, d2 = dice[0], dice[1]

    if d1 == d2:
        # Doubles: each step uses one die
        n_steps = pips // d1
        if n_steps <= 1:
            return [(src, dst)]
        moves = []
        cur = src
        for _ in range(n_steps):
            if cur == -1:  # bar
                nxt = (d1 - 1) if color == "red" else (24 - d1)
            else:
                nxt = cur + d1 * move_dir
            moves.append((cur, nxt))
            cur = nxt
        return moves
    else:
        # Non-doubles compound: d1 + d2 on one checker
        if pips == d1 + d2:
            if src == -1:  # bar
                mid = (24 - d1) if color == "red" else (d1 - 1)
            else:
                mid = src + d1 * move_dir
            return [(src, mid), (mid, dst)]
        return [(src, dst)]


def _gnubg_point_to_index(point_str: str, color: str) -> int:
    """Convert a GNUBG point string to an internal board index.

    GNUBG numbers from the on-roll player's perspective:
      their point 1 is closest to bearing off.

    For Red: GNUBG point N = index (N - 1)  [Red's 1-point = index 0]
    For White: GNUBG point N = index (24 - N) [White's 1-point = index 23]
    """
    if point_str == "bar":
        return -1
    if point_str == "off":
        return 24
    n = int(point_str)
    if color == "red":
        return n - 1
    else:
        return 24 - n


# ---------------------------------------------------------------------------
# Subprocess manager
# ---------------------------------------------------------------------------

class GnubgProcess:
    """Manages a persistent gnubg-cli subprocess for move evaluation.

    Uses a persistent reader thread to consume stdout lines into a queue,
    since select() doesn't work with subprocess pipes on Windows.
    """

    def __init__(self, ply: int = 0):
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()
        self._ply = ply
        self._started = False
        self._output_queue: queue.Queue[str | None] = queue.Queue()

    def start(self) -> bool:
        """Start the GNUBG subprocess. Returns True on success."""
        exe = _find_gnubg()
        if not exe:
            return False
        try:
            self._proc = subprocess.Popen(
                [exe, "-t", "-r", "-q"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
            )
            # Start persistent reader thread
            self._output_queue = queue.Queue()
            reader = threading.Thread(target=self._reader_loop, daemon=True)
            reader.start()

            # Read startup banner
            self._read_until_idle()
            # Set ply depth
            self._send(f"set evaluation chequerplay evaluation plies {self._ply}")
            self._read_until_idle()
            # Start a game so we can set board positions
            self._send("new game")
            self._read_until_idle()
            self._started = True
            log.info("GNUBG subprocess started (ply=%d)", self._ply)
            return True
        except (OSError, FileNotFoundError) as e:
            log.warning("Failed to start GNUBG: %s", e)
            self._proc = None
            return False

    def _reader_loop(self) -> None:
        """Persistent thread that reads stdout lines into the queue."""
        try:
            while self._proc and self._proc.stdout:
                line = self._proc.stdout.readline()
                if not line:
                    self._output_queue.put(None)
                    return
                self._output_queue.put(line.rstrip("\n\r"))
        except (ValueError, OSError):
            self._output_queue.put(None)

    def stop(self) -> None:
        """Terminate the subprocess."""
        with self._lock:
            if self._proc:
                try:
                    self._proc.stdin.write("quit\n")
                    self._proc.stdin.flush()
                    self._proc.wait(timeout=3)
                except Exception:
                    try:
                        self._proc.kill()
                    except Exception:
                        pass
                self._proc = None
                self._started = False

    def get_best_move(
        self, state: BackgammonGameState, color: str, timeout: float = 5.0
    ) -> list[tuple[int, int]] | None:
        """Get the best move from GNUBG for the current position.

        Returns a list of (source_idx, dest_idx) pairs, or None on failure.
        """
        with self._lock:
            if not self._proc or not self._started:
                return None
            try:
                return self._query_hint(state, color, timeout, pick_worst=False)
            except Exception as e:
                log.warning("GNUBG query failed: %s", e)
                self._restart()
                return None

    def get_worst_move(
        self, state: BackgammonGameState, color: str, timeout: float = 5.0
    ) -> list[tuple[int, int]] | None:
        """Get the worst move (Whackgammon). Asks for many hints, picks last."""
        with self._lock:
            if not self._proc or not self._started:
                return None
            try:
                return self._query_hint(state, color, timeout, pick_worst=True)
            except Exception as e:
                log.warning("GNUBG query failed: %s", e)
                self._restart()
                return None

    def get_cube_decision(
        self, state: BackgammonGameState, color: str, timeout: float = 5.0
    ) -> str | None:
        """Get GNUBG's cube decision for the current position.

        Returns one of:
            "double" — player should double
            "no-double" — player should not double
            "take" — player should accept the double
            "drop" — player should drop the double
            "too-good" — position too good to double (lose gammon value)
            None — on failure
        """
        with self._lock:
            if not self._proc or not self._started:
                return None
            try:
                return self._query_cube(state, color, timeout)
            except Exception as e:
                log.warning("GNUBG cube query failed: %s", e)
                self._restart()
                return None

    def _query_cube(
        self, state: BackgammonGameState, color: str, timeout: float,
    ) -> str | None:
        """Send position to GNUBG and parse the cube evaluation."""
        pos_id = encode_position_id(state)

        self._send(f"set board {pos_id}")
        self._read_until_idle()
        self._send("set turn 1")
        self._read_until_idle()

        # Set cube state
        self._send(f"set cube value {state.cube_value}")
        self._read_until_idle()
        if not state.cube_owner:
            self._send("set cube centre")
        elif state.cube_owner == color:
            self._send("set cube owner 1")  # on-roll player
        else:
            self._send("set cube owner 0")  # opponent
        self._read_until_idle()

        # hint 0 = cube analysis only (no dice set)
        self._send("hint 0")
        output = self._read_until_idle()

        # Parse "Proper cube action:" line
        for line in output:
            low = line.lower()
            if "proper cube action" not in low:
                continue
            if "no double" in low or "no redouble" in low:
                if "beaver" in low:
                    return "no-double"
                if "too good" in low:
                    return "too-good"
                return "no-double"
            if "double" in low or "redouble" in low:
                if "pass" in low or "drop" in low:
                    return "double"  # double because opponent should drop
                if "take" in low:
                    return "double"  # double, opponent will take but it's still correct
                return "double"
            if "take" in low:
                return "take"
            if "pass" in low or "drop" in low:
                return "drop"

        # Fallback: parse the cubeful equities to decide
        # Line format: "1. No double           +0.098"
        equities: dict[str, float] = {}
        for line in output:
            line_s = line.strip()
            if line_s.startswith("1.") and "No double" in line_s:
                try:
                    equities["no-double"] = float(line_s.split()[-1])
                except ValueError:
                    pass
            elif line_s.startswith("2.") and "pass" in line_s.lower():
                try:
                    equities["double-pass"] = float(line_s.split()[-2])
                except (ValueError, IndexError):
                    pass
            elif line_s.startswith("3.") and "take" in line_s.lower():
                try:
                    equities["double-take"] = float(line_s.split()[-2])
                except (ValueError, IndexError):
                    pass

        if equities:
            nd = equities.get("no-double", -999)
            dt = equities.get("double-take", -999)
            dp = equities.get("double-pass", -999)
            best = max(nd, dt, dp)
            if best == nd:
                return "no-double"
            return "double"

        return None

    def get_cube_hint_text(
        self, state: BackgammonGameState, color: str, timeout: float = 5.0
    ) -> str | None:
        """Get a human-readable cube hint string from GNUBG.

        Returns the full cube analysis text, or None on failure.
        """
        with self._lock:
            if not self._proc or not self._started:
                return None
            try:
                pos_id = encode_position_id(state)
                self._send(f"set board {pos_id}")
                self._read_until_idle()
                self._send("set turn 1")
                self._read_until_idle()

                self._send(f"set cube value {state.cube_value}")
                self._read_until_idle()
                if not state.cube_owner:
                    self._send("set cube centre")
                elif state.cube_owner == color:
                    self._send("set cube owner 1")
                else:
                    self._send("set cube owner 0")
                self._read_until_idle()

                self._send("hint 0")
                output = self._read_until_idle()

                # Extract the "Proper cube action" line
                for line in output:
                    if "Proper cube action" in line:
                        return line.strip()
                return None
            except Exception as e:
                log.warning("GNUBG cube hint failed: %s", e)
                self._restart()
                return None

    def _query_hint(
        self, state: BackgammonGameState, color: str, timeout: float,
        pick_worst: bool = False,
    ) -> list[tuple[int, int]] | None:
        """Send position to GNUBG and parse the hint response."""
        pos_id = encode_position_id(state)

        self._send(f"set board {pos_id}")
        self._read_until_idle()

        self._send("set turn 1")
        self._read_until_idle()

        unused_dice = [d for d, u in zip(state.dice, state.dice_used) if not u]
        if len(unused_dice) < 2:
            if unused_dice:
                d = unused_dice[0]
                unused_dice = [d, d]
            else:
                return None
        self._send(f"set dice {unused_dice[0]} {unused_dice[1]}")
        self._read_until_idle()

        # Request many hints for Whackgammon, just 1 for normal play
        hint_count = 20 if pick_worst else 1
        self._send(f"hint {hint_count}")
        output = self._read_until_idle()

        # Parse all hint lines
        last_submoves = None
        first_submoves = None
        for line in output:
            submoves = parse_hint_line(line)
            if submoves:
                if first_submoves is None:
                    first_submoves = submoves
                last_submoves = submoves

        chosen = last_submoves if pick_worst else first_submoves
        if chosen:
            return hint_to_actions(chosen, color, dice=unused_dice)
        return None

    def _send(self, command: str) -> None:
        """Send a command to GNUBG."""
        if self._proc and self._proc.stdin:
            self._proc.stdin.write(command + "\n")
            self._proc.stdin.flush()

    def _read_until_idle(self, timeout: float = 5.0) -> list[str]:
        """Read GNUBG output from the persistent reader queue until idle.

        We consider GNUBG idle when no new output arrives for 0.3s
        after receiving at least one line.
        """
        import time

        lines: list[str] = []
        deadline = time.monotonic() + timeout
        idle_wait = 0.3

        while time.monotonic() < deadline:
            remaining = deadline - time.monotonic()
            wait_time = min(idle_wait, remaining)
            try:
                item = self._output_queue.get(timeout=max(0.01, wait_time))
                if item is None:  # EOF
                    break
                lines.append(item)
            except queue.Empty:
                if lines:
                    break

        return lines

    def _restart(self) -> None:
        """Kill and restart the subprocess."""
        log.info("Restarting GNUBG subprocess")
        if self._proc:
            try:
                self._proc.kill()
            except Exception:
                pass
            self._proc = None
        self._started = False
        self.start()
