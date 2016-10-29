from Tkinter import *
from time import sleep
from random import randint
from functools import partial

class State(object):
    pass


def start(canvas):
    rec = canvas.create_rectangle(10, 10, 20, 20, fill="red")
    for _ in xrange(100):
        sleep(0.01)
        canvas.move(rec, 0, 1)
        canvas.update_idletasks()


SQUARE_SIZE = 80
WIDTH_CELLS = 10
HIGHT_CELLS = 10

FULL_CELLS = [(i, 9) for i in range(0, 2) + range(7, 10)] + \
             [(i, 8) for i in range(0, 2) + range(7, 10)] + \
             [(i, 7) for i in range(0, 10) if i != 4] + \
             [(i, 6) for i in range(0, 10) if i != 4] + \
             [(i, 4) for i in range(0, 10) if i != 4] + \
             [(i, 3) for i in range(0, 10) if i != 4] + \
             [(i, 2) for i in range(0, 10) if i != 4] + \
             [(i, 1) for i in range(0, 10) if i != 4] + \
             [(i, 0) for i in range(0, 10) if i != 4]

ARROW_CELLS = [(6, 8, "180"),
               (4, 6, "up_down")]
PIECES = [(4, 7, ["red", "red", "green", "green"]),
          (4, 6, ["green", "green", "red", "red"])]


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


def create_arrow(canvas, x, y, arrow_type):
    if arrow_type == "180":
        image = canvas.arrow_180_image
    else:
        image = canvas.up_down_image

    arrow = canvas.create_image(x * SQUARE_SIZE, y * SQUARE_SIZE,
                        anchor="nw", image=image)
    return arrow

def piece_data_after_operation(original_data, operation):
    if operation == "180":
        return [original_data[3], original_data[2],
                original_data[1], original_data[0]]
    else:
        return [original_data[2], original_data[3],
                original_data[0], original_data[1]]
      

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
    tag = str(piece_id)
    canvas.itemconfig(piece_id, tags=tag)
    canvas.create_rectangle(start_x + slice_size, start_y,
                            start_x + slice_size * 2, start_y + slice_size,
                            width=0,
                            fill=piece_data[1],
                            tags=tag)
    canvas.create_rectangle(start_x, start_y + slice_size,
                            start_x + slice_size, start_y + slice_size * 2,
                            width=0,
                            fill=piece_data[2],
                            tags=tag)
    canvas.create_rectangle(start_x + slice_size, start_y + slice_size,
                            start_x + slice_size * 2, start_y + slice_size * 2,
                            width=0,
                            fill=piece_data[2],
                            tags=tag)
    return tag


def draw_board(canvas):
    state = State()
    state.player_x = 3
    state.player_y = 9
    state.arrows = {}
    state.pieces = {}
    state.current_arrow = None

    state.player = create_square_rectangle(canvas, state.player_x, state.player_y, fill="red", delta=5)

    for x, y in FULL_CELLS:
        create_square_rectangle(canvas, x, y, fill="black")

    arrow_180_image = PhotoImage(file="arrow.gif")
    up_down_image = PhotoImage(file="up_down_flip.gif")
    canvas.arrow_180_image = arrow_180_image
    canvas.up_down_image = up_down_image

    for x, y, arrow_type in ARROW_CELLS:
        arrow = create_arrow(canvas, x, y, arrow_type)
        state.arrows[(x, y)] = (arrow, arrow_type)

    for x,y, piece_data in PIECES:
        tag = create_piece(canvas, x, y, piece_data)
        state.pieces[(x, y)] = (tag, piece_data)

    canvas.create_line(4.5 * SQUARE_SIZE, 7.5 * SQUARE_SIZE,
                       4.5 * SQUARE_SIZE, 6.5 * SQUARE_SIZE,
                       fill="blue",
                       width=3)
    bind_keys(canvas, state)


def is_blocked(x, y):
    return (x, y) in FULL_CELLS


def is_in_board(x, y):
    if (x >= WIDTH_CELLS or 
        x < 0 or 
        y >= HIGHT_CELLS or
        y < 0):
        return False
    return True


def move_player(event, canvas, state, dx, dy):
    next_x = state.player_x + dx
    next_y = state.player_y + dy

    if not is_in_board(next_x, next_y):
        return

    if is_blocked(next_x, next_y):
        return

    if (next_x, next_y) in state.pieces:
        if state.current_arrow is None:
            return
        else:
            old_tag, piece_data = state.pieces[(next_x, next_y)]
            new_tag, new_data = operate_piece(canvas,
                                              next_x, next_y,
                                              piece_data, old_tag,
                                              state.current_arrow)
            state.pieces[(next_x, next_y)] = (new_tag, new_data)
            return

    canvas.move(state.player, dx * SQUARE_SIZE, dy * SQUARE_SIZE)

    state.player_x += dx
    state.player_y += dy
    print state.player_x, state.player_y

    if (state.player_x, state.player_y) in state.arrows:
        arrow, arrow_type = state.arrows.pop((state.player_x, state.player_y))
        canvas.delete(arrow)
        print "On arrow"
        state.current_arrow = arrow_type


def main():
    root = Tk()
    canvas = Canvas(root,
                    bg="white",
                    width=WIDTH_CELLS * SQUARE_SIZE,
                    height=HIGHT_CELLS * SQUARE_SIZE)
    canvas.pack()
    canvas.focus_set()

    draw_board(canvas)

    start_button = Button(root, text="Start", command=partial(start, canvas))
    start_button.pack()
    
    root.mainloop()


if __name__ == "__main__":
    main()
