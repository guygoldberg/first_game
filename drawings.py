from Tkinter import *


SQUARE_SIZE = 80


def init_canvas(root, level):
    canvas = Canvas(root,
                    bg="white",
                    width=len(level[0]) * SQUARE_SIZE,
                    height=len(level) * SQUARE_SIZE)
    canvas.pack()
    canvas.focus_set()
    return canvas


def create_square_rectangle(canvas, x, y, fill="black", delta=0):
    return canvas.create_rectangle(x * SQUARE_SIZE + delta, y * SQUARE_SIZE + delta,
                                   (x + 1) * SQUARE_SIZE - delta, (y + 1) * SQUARE_SIZE - delta,
                                   fill=fill)


def load_assets_to_canvas(canvas):
    arrow_180_image = PhotoImage(file="arrow.gif")
    up_down_image = PhotoImage(file="up_down_flip.gif")
    rotate_image = PhotoImage(file="Rotate-Arrow.gif")
    right_left_image = PhotoImage(file="right_left.gif")
    canvas.arrow_180_image = arrow_180_image
    canvas.up_down_image = up_down_image
    canvas.rotate_image = rotate_image
    canvas.right_left_image = right_left_image


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


def move_element_on_canvas(canvas, tag, dx, dy):
    canvas.move(tag, dx * SQUARE_SIZE, dy * SQUARE_SIZE)
