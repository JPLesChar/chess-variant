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
    "White": {"Queen": "wQ", "Rook": "wR", "Bishop": "wB", "Knight": "wN"},
    "Black": {"Queen": "bQ", "Rook": "bR", "Bishop": "bB", "Knight": "bN"},
}


def parse_square(sq_str: str) -> Tuple[int, int]:
    """Converts notation like 'A1' into 0-indexed (col, row) coordinates."""
    col = COLS.index(sq_str[0].upper())
    row = ROWS.index(sq_str[1])
    return col, row


def format_square(coords: Tuple[int, int]) -> str:
    """Converts 0-indexed (col, row) coordinates to notation like 'A1'."""
    return f"{COLS[coords[0]]}{ROWS[coords[1]]}"


class Board:
    def __init__(self, white_piece: str, black_piece: str):
        self.white_piece = white_piece
        self.black_piece = black_piece
        
        # Starting positions
        self.white_start = (0, 0)  # A1
        self.black_start = (3, 3)  # D4
        
        # Current positions
        self.positions: Dict[str, Tuple[int, int]] = {
            "White": self.white_start,
            "Black": self.black_start,
        }

    def display(self):
        """Cleanly renders the 4x4 board state."""
        print("\n      A      B      C      D  ")
        print("   +------+------+------+------+")
        for r in reversed(range(4)):
            row_str = f" {ROWS[r]} |"
            for c in range(4):
                cell_content = "  "
                for player, pos in self.positions.items():
                    if pos == (c, r):
                        piece = self.white_piece if player == "White" else self.black_piece
                        cell_content = PIECE_SYMBOLS[player][piece]

                # Highlight starting bases if unoccupied
                if cell_content == "  ":
                    if (c, r) == self.white_start:
                        cell_content = ".w"  # White base marker
                    elif (c, r) == self.black_start:
                        cell_content = ".b"  # Black base marker
                    else:
                        cell_content = " ."

                row_str += f"  {cell_content}  |"
            print(row_str)
            print("   +------+------+------+------+")
        print("      A      B      C      D  \n")
        print("Base Tiles: [.w] = White Base (A1) | [.b] = Black Base (D4)\n")


class Game:
    def __init__(self):
        self.white_piece = random.choice(PIECE_NAMES)
        self.black_piece = random.choice(PIECE_NAMES)
        self.board = Board(self.white_piece, self.black_piece)
        self.current_turn = "White"

    def opponent(self, player: str) -> str:
        return "Black" if player == "White" else "White"

    def is_path_clear(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """Checks if intermediate squares between start and end are unoccupied."""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

        curr_x = start[0] + step_x
        curr_y = start[1] + step_y

        occupied_positions = set(self.board.positions.values())

        while (curr_x, curr_y) != end:
            if (curr_x, curr_y) in occupied_positions:
                return False
            curr_x += step_x
            curr_y += step_y

        return True

    def validate_move(self, player: str, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[str]:
        """Validates move mechanics. Returns None if valid, or an error message."""
        if start != self.board.positions[player]:
            expected = format_square(self.board.positions[player])
            return f"Invalid source: Your piece is at {expected}, not at {format_square(start)}."

        if start == end:
            return "Destination must be different from the starting square."

        piece = self.white_piece if player == "White" else self.black_piece
        dx = abs(end[0] - start[0])
        dy = abs(end[1] - start[1])

        # Validate piece movement
        if piece == "Rook":
            if not ((dx == 0 and dy > 0) or (dx > 0 and dy == 0)):
                return "Rooks can only move horizontally or vertically."
            if not self.is_path_clear(start, end):
                return "Move blocked: Cannot leap over another piece."

        elif piece == "Bishop":
            if not (dx == dy and dx > 0):
                return "Bishops can only move diagonally."
            if not self.is_path_clear(start, end):
                return "Move blocked: Cannot leap over another piece."

        elif piece == "Queen":
            is_orthogonal = (dx == 0 and dy > 0) or (dx > 0 and dy == 0)
            is_diagonal = (dx == dy and dx > 0)
            if not (is_orthogonal or is_diagonal):
                return "Queens can only move orthogonally or diagonally."
            if not self.is_path_clear(start, end):
                return "Move blocked: Cannot leap over another piece."

        elif piece == "Knight":
            if not ((dx == 1 and dy == 2) or (dx == 2 and dy == 1)):
                return "Knights must move in an 'L' shape (2 squares in one axis, 1 in the other)."

        return None

    def prompt_move(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Prompts and parses move input in formats like 'A1 to A3', 'A1-A3', or 'A1 A3'."""
        pattern = re.compile(r"^\s*([A-Da-d][1-4])\s*(?:to|->|-)?\s*([A-Da-d][1-4])\s*$")

        while True:
            piece_name = self.white_piece if self.current_turn == "White" else self.black_piece
            curr_pos = format_square(self.board.positions[self.current_turn])
            
            user_input = input(
                f"[{self.current_turn}'s Turn ({piece_name} @ {curr_pos})]\n"
                f"Enter move (e.g. '{curr_pos} to ...' or 'quit'): "
            ).strip()

            if user_input.lower() in ["quit", "exit"]:
                print("Game aborted.")
                sys.exit(0)

            match = pattern.match(user_input)
            if not match:
                print(">> Error: Invalid format. Please enter moves like 'A1 to A3', 'A1-A3', or 'A1 A3'.\n")
                continue

            start_sq = match.group(1).upper()
            end_sq = match.group(2).upper()

            start_coords = parse_square(start_sq)
            end_coords = parse_square(end_sq)

            err = self.validate_move(self.current_turn, start_coords, end_coords)
            if err:
                print(f">> Illegal move: {err}\n")
                continue

            return start_coords, end_coords

    def play(self):
        print("=" * 55)
        print("         WELCOME TO 4x4 MICRO-CHESS VARIANT        ")
        print("=" * 55)
        print(f"Draft Results:")
        print(f"  • Player 1 (White): {self.white_piece} (Starts at A1)")
        print(f"  • Player 2 (Black): {self.black_piece} (Starts at D4)")
        print("\nWin Conditions:")
        print("  1. Capture your opponent's piece.")
        print("  2. Land your piece on the opponent's starting tile.")
        print("=" * 55)

        while True:
            self.board.display()
            _, end = self.prompt_move()

            # Execute move
            self.board.positions[self.current_turn] = end
            opp = self.opponent(self.current_turn)
            opp_start_tile = self.board.black_start if self.current_turn == "White" else self.board.white_start

            # Win condition checks
            captured = end == self.board.positions[opp]
            reached_base = end == opp_start_tile

            if captured or reached_base:
                self.board.display()
                print("*" * 55)
                if captured:
                    print(f"{self.current_turn} wins by capturing the opponent!")
                else:
                    print(f"{self.current_turn} wins by reaching the opponent's starting tile!")
                print("*" * 55)
                return

            self.current_turn = opp


def run_streamlit_app():
    import streamlit as st

    st.set_page_config(page_title="4x4 Micro-Chess", page_icon="♟")
    st.title("4x4 Micro-Chess Variant")
    st.caption("Select your piece, then select its destination. Capture your opponent or reach their starting tile to win.")

    if "game" not in st.session_state:
        st.session_state.game = Game()
        st.session_state.selected_square = None
        st.session_state.winner = None
        st.session_state.message = None

    game = st.session_state.game
    selected_square = st.session_state.selected_square
    winner = st.session_state.winner

    white_col, black_col = st.columns(2)
    white_col.write(f"White: **{game.white_piece}** (A1)")
    black_col.write(f"Black: **{game.black_piece}** (D4)")

    if winner:
        st.success(f"{winner} wins!")
    else:
        current_piece = game.white_piece if game.current_turn == "White" else game.black_piece
        current_square = format_square(game.board.positions[game.current_turn])
        st.info(f"{game.current_turn}'s turn: {current_piece} at {current_square}")

    if st.button("New game"):
        st.session_state.game = Game()
        st.session_state.selected_square = None
        st.session_state.winner = None
        st.session_state.message = None
        st.rerun()

    if st.session_state.message:
        st.warning(st.session_state.message)
        st.session_state.message = None

    for row in reversed(range(4)):
        board_columns = st.columns(4)
        for col, board_column in enumerate(board_columns):
            square = (col, row)
            square_name = format_square(square)
            occupant = next(
                (player for player, position in game.board.positions.items() if position == square),
                None,
            )
            if occupant:
                piece = game.white_piece if occupant == "White" else game.black_piece
                label = PIECE_SYMBOLS[occupant][piece]
            elif square == game.board.white_start:
                label = ".w"
            elif square == game.board.black_start:
                label = ".b"
            else:
                label = "."

            if square == selected_square:
                label = f"[{label}]"

            if board_column.button(
                f"{square_name}  {label}",
                key=f"square_{col}_{row}",
                disabled=winner is not None,
                type="primary" if square == selected_square else "secondary",
                use_container_width=True,
            ):
                if selected_square is None:
                    if square == game.board.positions[game.current_turn]:
                        st.session_state.selected_square = square
                    else:
                        st.session_state.message = "Select your piece first."
                elif square == selected_square:
                    st.session_state.selected_square = None
                else:
                    error = game.validate_move(game.current_turn, selected_square, square)
                    if error:
                        st.session_state.message = error
                    else:
                        player = game.current_turn
                        opponent = game.opponent(player)
                        opponent_start = (
                            game.board.black_start if player == "White" else game.board.white_start
                        )
                        captured = square == game.board.positions[opponent]
                        game.board.positions[player] = square
                        st.session_state.selected_square = None

                        if captured or square == opponent_start:
                            st.session_state.winner = player
                        else:
                            game.current_turn = opponent
                st.rerun()

    if st.session_state.selected_square is not None and winner is None:
        st.caption(f"Selected {format_square(st.session_state.selected_square)}. Choose a destination.")


if __name__ == "__main__":
    run_streamlit_app()
