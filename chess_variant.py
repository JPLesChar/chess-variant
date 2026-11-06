#!/usr/bin/env python3
"""
4x4 Micro-Chess Variant

Rules:
- 4x4 Board: Columns A-D, Rows 1-4.
- White starts at A1; Black starts at D4.
- Each player is randomly drafted one piece: Queen, Rook, Bishop, or Knight.
- First player to capture the opponent OR reach the opponent's starting tile wins.
"""

import random
import re
import sys
from typing import Tuple, Optional, Dict

COLS = ["A", "B", "C", "D"]
ROWS = ["1", "2", "3", "4"]

PIECE_NAMES = ["Queen", "Rook", "Bishop", "Knight"]

PIECE_SYMBOLS = {
    "White": {
        "Queen": "wQ",
        "Rook": "wR",
        "Bishop": "wB",
        "Knight": "wN",
    },
    "Black": {
        "Queen": "bQ",
        "Rook": "bR",
        "Bishop": "bB",
        "Knight": "bN",
    },
}


def parse_square(sq_str: str) -> Tuple[int, int]:
    """Converts notation like 'A1' into 0-indexed coordinates."""
    col = COLS.index(sq_str[0].upper())
    row = ROWS.index(sq_str[1])
    return col, row


def format_square(coords: Tuple[int, int]) -> str:
    """Converts coordinates to notation like 'A1'."""
    return f"{COLS[coords[0]]}{ROWS[coords[1]]}"
