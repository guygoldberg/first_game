from Tkinter import *
from time import sleep
from random import randint
from functools import partial

class State(object):
    pass

SQUARE_SIZE = 80

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


def bind_keys(canvas, state):
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


def create_square_rectangle(canvas, x, y, fill="black", delta=0):
    return canvas.create_rectangle(x * SQUARE_SIZE + delta, y * SQUARE_SIZE + delta,
                                   (x + 1) * SQUARE_SIZE - delta, (y + 1) * SQUARE_SIZE - delta,
                                   fill=fill)


def draw_operation(canvas, x, y, operation_type):
    operation_type_to_image = {(False, 2): canvas.arrow_180_image,
                               (True, 0): canvas.up_down_image,
                               (False, 1): canvas.rotate_image,
                               (True, 2): canvas.right_left_image,
                               }
    image = operation_type_to_image[operation_type]
    operation = canvas.create_image(x * SQUARE_SIZE, y * SQUARE_SIZE,
                                    anchor="nw", image=image)
    return operation


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


def create_piece(canvas, x, y, piece_data):
    delta = 5
    start_x = x * SQUARE_SIZE + delta
    start_y = y * SQUARE_SIZE + delta
    slice_size = (SQUARE_SIZE - 2 * delta) / 2
    piece_id = canvas.create_rectangle(start_x, start_y, 
                            start_x + slice_size, start_y + slice_size,
                            width=0,
                            fill=piece_data[0])
    tag = "P" + str(piece_id)
    canvas.itemconfig(piece_id, tags=tag)
    canvas.create_rectangle(start_x + slice_size, start_y,
                            start_x + slice_size * 2, start_y + slice_size,
                            width=0,
                            fill=piece_data[1],
                            tags=tag)
    canvas.create_rectangle(start_x + slice_size, start_y + slice_size,
                            start_x + slice_size * 2, start_y + slice_size * 2,
                            width=0,
                            fill=piece_data[2],
                            tags=tag)
    canvas.create_rectangle(start_x, start_y + slice_size,
                            start_x + slice_size, start_y + slice_size * 2,
                            width=0,
                            fill=piece_data[3],
                            tags=tag)
    return tag


def draw_board(canvas, level, pairs_as_text):
    state = State()
    state.operations = {}
    state.pieces = {}
    state.blocks = []
    state.width = len(level[0])
    state.height = len(level)
    state.current_operation = None
    state.pairs = {}

    arrow_180_image = PhotoImage(file="arrow.gif")
    up_down_image = PhotoImage(file="up_down_flip.gif")
    rotate_image = PhotoImage(file="Rotate-Arrow.gif")
    right_left_image = PhotoImage(file="right_left.gif")
    canvas.arrow_180_image = arrow_180_image
    canvas.up_down_image = up_down_image
    canvas.rotate_image = rotate_image
    canvas.right_left_image = right_left_image


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
    bind_keys(canvas, state)


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

    canvas.move(state.player, dx * SQUARE_SIZE, dy * SQUARE_SIZE)

    state.player_x += dx
    state.player_y += dy

    if (state.player_x, state.player_y) in state.operations:
        operation, operation_type = state.operations.pop((state.player_x, state.player_y))
        canvas.delete(operation)
        state.current_operation = operation_type


def main():
    root = Tk()

    full_level = open("level_1.lvl", "rb").read().splitlines()
    split_index = full_level.index("-")
    level = full_level[:split_index]
    pairs_as_text = full_level[split_index+1:]
    canvas = Canvas(root,
                    bg="white",
                    width=len(level[0]) * SQUARE_SIZE,
                    height=len(level) * SQUARE_SIZE)
    canvas.pack()
    canvas.focus_set()

    draw_board(canvas, level, pairs_as_text)

    root.mainloop()


if __name__ == "__main__":
    main()
