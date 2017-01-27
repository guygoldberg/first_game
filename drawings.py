from Tkinter import *


SQUARE_SIZE = 80

color_code_to_color = {"r": "red", "g": "green"}

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

def code_to_operation(code):
    mirror = (code[0] == "T")
    rotations = int(code[1])
    return (mirror, rotations)

def create_edit_canvas(root, level):
    edit_mode_canvas = Canvas(root,
                              bg="white",
                              width=4 * SQUARE_SIZE,
                              height=6 * SQUARE_SIZE)
    load_assets_to_canvas(edit_mode_canvas)
    edit_mode_canvas.pack()

    location_to_colors = {
            (0, 0): "rrgg",
            (1, 0): "ggrr",
            (2, 0): "rggr",
            (3, 0): "grrg",
            (0, 1): "rggg",
            (1, 1): "grgg",
            (2, 1): "ggrg",
            (3, 1): "gggr",
            (0, 2): "grrr",
            (1, 2): "rgrr",
            (2, 2): "rrgr",
            (3, 2): "rrrg",
            (0, 3): "rrrr",
            (1, 3): "gggg",
            (2, 3): "rgrg",
            (3, 3): "grgr",
            (0, 4): "B",
            (0, 5): "F2",
            (1, 5): "T0",
            (2, 5): "F1",
            (3, 5): "T2",
            }
    for (x, y), colors in location_to_colors.items():
        if colors == "B":
            create_square_rectangle(edit_mode_canvas, x, y)
        elif colors[0] in "FT":
            draw_operation(edit_mode_canvas, x, y, code_to_operation(colors))
        else:
            create_piece(edit_mode_canvas, x, y, colors)

    return edit_mode_canvas, location_to_colors



def create_piece(canvas, x, y, piece_data):
    colors = [color_code_to_color[code] for code in piece_data]
    delta = 5
    start_x = x * SQUARE_SIZE + delta
    start_y = y * SQUARE_SIZE + delta
    slice_size = (SQUARE_SIZE - 2 * delta) / 2
    piece_id = canvas.create_rectangle(start_x, start_y, 
                            start_x + slice_size, start_y + slice_size,
                            width=0,
                            fill=colors[0])
    tag = "P" + str(piece_id)
    canvas.itemconfig(piece_id, tags=tag)
    canvas.create_rectangle(start_x + slice_size, start_y,
                            start_x + slice_size * 2, start_y + slice_size,
                            width=0,
                            fill=colors[1],
                            tags=tag)
    canvas.create_rectangle(start_x + slice_size, start_y + slice_size,
                            start_x + slice_size * 2, start_y + slice_size * 2,
                            width=0,
                            fill=colors[2],
                            tags=tag)
    canvas.create_rectangle(start_x, start_y + slice_size,
                            start_x + slice_size, start_y + slice_size * 2,
                            width=0,
                            fill=colors[3],
                            tags=tag)
    return tag


def move_element_on_canvas(canvas, tag, dx, dy):
    canvas.move(tag, dx * SQUARE_SIZE, dy * SQUARE_SIZE)
