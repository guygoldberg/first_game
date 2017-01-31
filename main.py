import sys
from time import sleep
from random import randint
from functools import partial
from Tkinter import *

from drawings import (
    init_canvas,
    create_square_rectangle,
    create_edit_canvas,
    load_assets_to_canvas,
    create_piece,
    draw_operation,
    move_element_on_canvas,
    SQUARE_SIZE,
    code_to_operation,
    )


class State(object):
    pass


current_colors = "B"
piece_code_to_data = {
        "A": "rrgg",
        "B": "grrg",
        "C": "ggrr",
        "D": "rggr",

        "E": "rggg",
        "F": "grgg",
        "G": "ggrg",
        "H": "gggr",
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


def restart_level(event, canvas, level):
    canvas.delete(ALL)
    state = draw_board(canvas, level)
    bind_arrows(canvas, state)


def bind_restart(canvas, level):
    canvas.bind("r", partial(restart_level,
                             level=level,
                             canvas=canvas))


def enter_debug(event, canvas, state):
    import pdb; pdb.set_trace()


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
    canvas.bind("d", partial(enter_debug,
                             canvas=canvas,
                             state=state))
    canvas.bind("<Button-3>", partial(right_click,
                                      canvas=canvas,
                                      state=state))
    canvas.bind("<Button-1>", partial(left_click,
                                      canvas=canvas,
                                      state=state))



def right_click(event, canvas, state):
    delete_element(canvas, state, 
                   event.x // SQUARE_SIZE, event.y // SQUARE_SIZE)


def left_click(event, canvas, state):
    x, y = event.x // SQUARE_SIZE, event.y // SQUARE_SIZE

    if current_colors == "B":
        add_block(canvas, state, x, y)
    elif current_colors[0] in "TF":
        add_operation(canvas, state, x, y, code_to_operation(current_colors))
    else:
        add_piece(canvas, state, x, y, current_colors)


def piece_data_after_operation(original_data, operation):
    mirror, number_of_rotations = operation

    if mirror:
        new_data = "".join([original_data[3], original_data[2],
                    original_data[1], original_data[0]])
    else:
        new_data = original_data[:]

    for _ in xrange(number_of_rotations):
        new_data = "".join(new_data[(i + 3) % 4] for i in xrange(4))

    return new_data


def operate_piece(canvas, x, y, piece_data, piece_tag, operation):
    new_data = piece_data_after_operation(piece_data, operation)
    canvas.delete(piece_tag)
    new_tag = create_piece(canvas, x, y, new_data)
    return new_tag, new_data


def start_game(canvas, level):
    load_assets_to_canvas(canvas)
    state = draw_board(canvas, level)
    bind_restart(canvas, level)
    bind_arrows(canvas, state)


def add_block(canvas, state, x, y):
    block = create_square_rectangle(canvas, x, y, fill="black")
    state.blocks[(x, y)] = block


def delete_element(canvas, state, x, y):
    if (x, y) in state.blocks:
        block = state.blocks.pop((x, y))
        canvas.delete(block)

    if (x, y) in state.pieces:
        tag = state.pieces.pop((x, y))[0]
        canvas.delete(tag)


    if (x, y) in state.operations:
        tag = state.operations.pop((x, y))[0]
        canvas.delete(tag)


def add_piece(canvas, state, x, y, colors):
    tag = create_piece(canvas, x, y, colors)
    state.pieces[(x, y)] = (tag, colors)


def add_operation(canvas, state, x, y, operation_type):
    operation = draw_operation(canvas, x, y, operation_type)
    state.operations[(x, y)] = (operation, operation_type)


def draw_board(canvas, level):
    state = State()
    state.operations = {}
    state.pieces = {}
    state.blocks = {}
    state.width = len(level[0])
    state.height = len(level)
    state.current_operation = None


    y = 0
    for line in level:
        x = 0
        for char in line:
            if char == "#":
                add_block(canvas, state, x, y)

            if char in piece_code_to_data:
                piece_data = piece_code_to_data[char]
                add_piece(canvas, state, x, y, piece_data)

            if char in operation_code_to_operation_type:
                operation_type = operation_code_to_operation_type[char]
                add_operation(canvas, state, x, y, operation_type)

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


def get_neighbors(state, x, y):
    neighbors = []
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        neighbor_x, neighbor_y = x + dx, y + dy

        if not is_in_board(state, neighbor_x, neighbor_y):
            continue

        if (neighbor_x, neighbor_y) not in state.pieces:
            continue

        neighbors.append((neighbor_x, neighbor_y))

    return neighbors


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
            delete_self = False
            for (other_x, other_y) in get_neighbors(state, next_x, next_y):
                other_tag, other_data = state.pieces[(other_x, other_y)]
                if other_data == new_data:
                    delete_self = True
                    canvas.update_idletasks()
                    sleep(0.3)
                    canvas.delete(other_tag)
                    state.pieces.pop((other_x, other_y))

            if delete_self:
                canvas.update_idletasks()
                sleep(0.3)
                state.pieces.pop((next_x, next_y))
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
    level = open(path, "rb").read().splitlines()
    return level


def click_edit(event, location_to_colors):
    colors = location_to_colors[(event.x // SQUARE_SIZE, event.y // SQUARE_SIZE)]
    global current_colors
    current_colors = colors


def main(argv):
    if argv:
        level_str = argv[0]
    else:
        level_str = "0"
    root = Tk()

    level = parse_level_from_path("level_{}.lvl".format(level_str))

    canvas = init_canvas(root, level)
    edit_canvas, location_to_colors = create_edit_canvas(root, level)
    edit_canvas.bind("<Button-1>", partial(click_edit,
                                           location_to_colors=location_to_colors))
    start_game(canvas, level)

    root.mainloop()


if __name__ == "__main__":
    main(sys.argv[1:])
