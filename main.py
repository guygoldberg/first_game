import sys
from time import sleep
from random import randint
from functools import partial
from Tkinter import *

from drawings import (
    init_canvas,
    create_square_rectangle,
    load_assets_to_canvas,
    create_piece,
    draw_operation,
    move_element_on_canvas,
    )


class State(object):
    pass


piece_code_to_data = {
        "A": ["red", "red", "green", "green"],
        "B": ["green", "red", "red", "green"],
        "C": ["green", "green", "red", "red"],
        "D": ["red", "green", "green", "red"],

        "E": ["red", "green", "green", "green"],
        "F": ["green", "red", "green", "green"],
        "G": ["green", "green", "red", "green"],
        "H": ["green", "green", "green", "red"],
        }

# Operation is a tuple (boolean, int)
# The boolean indicates if there's a mirroring, and the int
# is the number of rotations
operation_code_to_operation_type = {
        "a": (False, 2),
        "b": (True, 0),
        "c": (False, 1),
        "d": (True, 2),
        }


def restart_level(event, canvas, level, pairs_as_text):
    canvas.delete(ALL)
    state = draw_board(canvas, level, pairs_as_text)
    bind_arrows(canvas, state)


def bind_restart(canvas, level, pairs_as_text):
    canvas.bind("r", partial(restart_level,
                             level=level,
                             pairs_as_text=pairs_as_text,
                             canvas=canvas))


def bind_arrows(canvas, state):
    canvas.bind("<Up>", partial(move_player,
                                canvas=canvas,
                                state=state,
                                dx=0,
                                dy=-1))
    canvas.bind("<Down>", partial(move_player,
                                canvas=canvas,
                                state=state,
                                dx=0,
                                dy=1))
    canvas.bind("<Right>", partial(move_player,
                                canvas=canvas,
                                state=state,
                                dx=1,
                                dy=0))
    canvas.bind("<Left>", partial(move_player,
                                canvas=canvas,
                                state=state,
                                dx=-1,
                                dy=0))



def piece_data_after_operation(original_data, operation):
    mirror, number_of_rotations = operation

    if mirror:
        new_data = [original_data[3], original_data[2],
                    original_data[1], original_data[0]]
    else:
        new_data = original_data[:]

    for _ in xrange(number_of_rotations):
        before_rotation = new_data[:]
        for i in xrange(4):
            new_data[i] = before_rotation[(i + 3) % 4]

    return new_data


def operate_piece(canvas, x, y, piece_data, piece_tag, operation):
    new_data = piece_data_after_operation(piece_data, operation)
    canvas.delete(piece_tag)
    new_tag = create_piece(canvas, x, y, new_data)
    return new_tag, new_data


def start_game(canvas, level, pairs_as_text):
    load_assets_to_canvas(canvas)
    state = draw_board(canvas, level, pairs_as_text)
    bind_restart(canvas, level, pairs_as_text)
    bind_arrows(canvas, state)


def draw_board(canvas, level, pairs_as_text):
    state = State()
    state.operations = {}
    state.pieces = {}
    state.blocks = []
    state.width = len(level[0])
    state.height = len(level)
    state.current_operation = None
    state.pairs = {}

    for line in pairs_as_text:
        # TODO: Change from eval to a better way
        (x1, y1), (x2, y2) = eval(line)
        if (x1, y1) not in state.pairs:
            state.pairs[(x1, y1)] = []
        state.pairs[(x1, y1)].append((x2, y2))

        if (x2, y2) not in state.pairs:
            state.pairs[(x2, y2)] = []
        state.pairs[(x2, y2)].append((x1, y1))

    y = 0
    for line in level:
        x = 0
        for char in line:
            if char == "#":
                create_square_rectangle(canvas, x, y, fill="black")
                state.blocks.append((x, y))

            if char in piece_code_to_data:
                piece_data = piece_code_to_data[char]
                tag = create_piece(canvas, x, y, piece_data)
                state.pieces[(x, y)] = (tag, piece_data)

            if char in operation_code_to_operation_type:
                operation_type = operation_code_to_operation_type[char]
                operation = draw_operation(canvas, x, y, operation_type)
                state.operations[(x, y)] = (operation, operation_type)

            if char == "p":
                state.player_x = x
                state.player_y = y

            x += 1
        y += 1

    state.player = create_square_rectangle(canvas, state.player_x, state.player_y, fill="red", delta=5)
    return state


def is_blocked(state, x, y):
    return (x, y) in state.blocks


def is_in_board(state, x, y):
    if (x >= state.width or
        x < 0 or 
        y >= state.height or
        y < 0):
        return False
    return True


def move_player(event, canvas, state, dx, dy):
    next_x = state.player_x + dx
    next_y = state.player_y + dy

    if not is_in_board(state, next_x, next_y):
        return

    if is_blocked(state, next_x, next_y):
        return

    if (next_x, next_y) in state.pieces:
        if state.current_operation is None:
            return
        else:
            old_tag, piece_data = state.pieces[(next_x, next_y)]
            new_tag, new_data = operate_piece(canvas,
                                              next_x, next_y,
                                              piece_data, old_tag,
                                              state.current_operation)
            state.pieces[(next_x, next_y)] = (new_tag, new_data)
            state.current_operation = None
            if (next_x, next_y) in state.pairs:
                delete_self = False
                for (other_x, other_y) in state.pairs[(next_x, next_y)]:
                    other_tag, other_data = state.pieces[(other_x, other_y)]
                    if other_data == new_data:
                        delete_self = True
                        canvas.update_idletasks()
                        sleep(0.3)
                        canvas.delete(other_tag)
                        state.pieces.pop((other_x, other_y))
                        state.pairs.pop((other_x, other_y))

                if delete_self:
                    canvas.update_idletasks()
                    sleep(0.3)
                    state.pieces.pop((next_x, next_y))
                    state.pairs.pop((next_x, next_y))
                    canvas.delete(new_tag)
            return

    move_element_on_canvas(canvas, state.player, dx, dy)

    state.player_x += dx
    state.player_y += dy

    if (state.player_x, state.player_y) in state.operations:
        operation, operation_type = state.operations.pop((state.player_x, state.player_y))
        canvas.delete(operation)
        state.current_operation = operation_type


def parse_level_from_path(path):
    full_level = open(path, "rb").read().splitlines()
    split_index = full_level.index("-")
    level = full_level[:split_index]
    pairs_as_text = full_level[split_index+1:]
    return level, pairs_as_text


def main(argv):
    if argv:
        level_str = argv[0]
    else:
        level_str = "1"
    root = Tk()

    level, pairs_as_text = parse_level_from_path("level_{}.lvl".format(level_str))

    canvas = init_canvas(root, level)

    start_game(canvas, level, pairs_as_text)

    root.mainloop()


if __name__ == "__main__":
    main(sys.argv[1:])
