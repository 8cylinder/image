import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import time
import click
import uuid
from enum import Enum
from pprint import pprint as pp


TRANSPARENT = (0, 0, 0, 0)


class style(Enum):
    CIRCLES = 'circles'
    DESCRIPTIVE = 'descriptive'


def compost_layers(layers):
    combined_image = layers[0]
    for layer in layers[1:]:
        combined_image = Image.alpha_composite(combined_image, layer)
        # combined_image = Image.composite(combined_image, layer)
    return combined_image


def generate_circles_image(image_size, background_color, extra_text):
    background_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    # background_color = 'black'
    layers = [
        make_circles_layer(background_color, image_size, num_circles=50, blur_radius=30),
        make_circles_layer(TRANSPARENT, image_size, num_circles=10, blur_radius=10, circle_scale=0.5),
        # make_text_layer(TRANSPARENT, image_size, extra_text, blur_radius=10),
        make_text_layer(TRANSPARENT, image_size, extra_text),
        make_circles_layer(TRANSPARENT, image_size, num_circles=10, blur_radius=1.5, circle_scale=0.5),
        make_circles_layer(TRANSPARENT, image_size, num_circles=3, blur_radius=0.3, circle_scale=0.2),
    ]
    combined_image = compost_layers(layers)

    return combined_image


def make_circles_layer(
        background_color, image_size, num_circles, blur_radius, circle_scale=1.0
    ):
    blur_radius = blur_radius * image_size[0] // 300   # Blur radius based on image width
    # blur_radius = max(blur_radius, 3)  # Limit blur radius to 30

    # Create a new image with white background
    layer = Image.new('RGBA', image_size, background_color)
    draw = ImageDraw.Draw(layer)

    # Generate and draw random circles for the first layer
    generate_circles(draw, image_size, num_circles, circle_scale=circle_scale)
    # alpha = 245
    # for _ in range(num_circles):
    #     add_ellipse(draw, image_size, alpha, circle_scale=circle_scale)

    layer = layer.filter(ImageFilter.GaussianBlur(blur_radius))
    # layer = layer.filter(ImageFilter.BoxBlur(blur_radius))

    # layer = layer.rotate(angle=random.randint(0, 360), expand=True)
    # layer.resize((image_size[0] * 2, image_size[1] * 2))
    # layer = layer.crop((0, 0, image_size[0], image_size[1]))
    return layer


# def add_ellipse(draw, image_size, alpha, circle_scale=1.0):
#     ...


def make_x_layer(background_color, image_size, line_width=2):
    line_color = '#6E6E6E'
    layer = Image.new('RGBA', image_size, background_color)
    draw = ImageDraw.Draw(layer)
    draw.line((0, 0) + image_size, fill=line_color, width=line_width)
    draw.line((0, image_size[1], image_size[0], 0), fill=line_color, width=line_width)

    return layer


def make_text_layer(background_color, size, extra_text, blur_radius=0):
    layer = Image.new('RGBA', size, background_color)
    draw = ImageDraw.Draw(layer)

    # Calculate font size based on 50% of the image width
    font_size = int(size[0] * 0.08)
    font = ImageFont.truetype("AndaleMonoSM5.ttf", font_size)

    # Calculate text size and position to center it
    extra_text = f'{extra_text}\n' if extra_text else ""
    text = f"{extra_text}{size[0]}px x {size[1]}px"
    _, _, text_width, text_height = draw.textbbox((0, 0), text, font=font)
    text_x = (size[0] - text_width) // 2
    text_y = (size[1] - text_height) // 2

    if blur_radius:
        offset = 10
        fill = 'black'
        positions = (
            (text_x - offset, text_y),
            (text_x + offset, text_y),
            (text_x, text_y - offset),
            (text_x, text_y + offset),
            (text_x + offset, text_y + offset),
            (text_x + offset, text_y - offset),
            (text_x - offset, text_y + offset),
            (text_x - offset, text_y - offset),
        )
        for pos in positions:
            draw.text(pos, text, fill=fill, font=font)
        layer = layer.filter(ImageFilter.GaussianBlur(blur_radius))
    else:
        draw.text((text_x, text_y), text, fill='white', font=font)

    return layer


def generate_circles(draw, image_size, num_circles, circle_scale=1.0):
    alpha = 245 #220
    for _ in range(num_circles):
        circle_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), alpha)
        radius = random.randint(10, 200)
        # Scale radius based on image width
        radius = radius * image_size[0] // 600 * circle_scale
        radius = int(radius)
        try:
            # this keeps all circles within the image
            # position = (random.randint(0, image_size[0] - radius * 2),
            #             random.randint(0, image_size[1] - radius * 2))
            position = (random.randint(0, image_size[0]),
                        random.randint(0, image_size[1]))
            # position = (image_size[0], 0)
            # pp(position)
        except ValueError:
            continue

        # size = (radius // 1.5, radius * 1.5)
        size = (radius, radius)

        box = [
            position[0] - size[0] //2,
            position[1] - size[1] //2,
            position[0] + size[1] //2,
            position[1] + size[1] //2,
        ]
        # pp(box)

        border_color = (
            random.randint(0, 255), random.randint(0, 255),
            random.randint(0, 255), alpha
        )
        border_width = random.randint(0, 30)
        draw.ellipse(box, fill=circle_color, outline=border_color, width=border_width)

        # draw.ellipse(
        #     [position, (position[0] + radius * 2, position[1] + radius * 2)],
        #     fill=circle_color, outline=border_color, width=border_width
        # )


def generate_descriptive_image(size, background_color, extra_text):
    """Generate a grey image with an x from corner to corner and the image size"""
    background_color = background_color if background_color else '#7D7D7D'
    layers = [
        make_x_layer(background_color, size),
        make_text_layer(TRANSPARENT, size, extra_text)
    ]
    combined_image = compost_layers(layers)
    return combined_image


def add_text(draw, extra_text, size):
    # Calculate font size based on 50% of the image width
    font_size = int(size[0] * 0.05)
    font = ImageFont.truetype("AndaleMonoSM5.ttf", font_size)

    # Calculate text size and position to center it
    extra_text = f'{extra_text}\n' if extra_text else ""
    text = f"{extra_text}{size[0]}px x {size[1]}px"
    _, _, text_width, text_height = draw.textbbox((0, 0), text, font=font)
    text_x = (size[0] - text_width) // 2
    text_y = (size[1] - text_height) // 2
    draw.text((text_x, text_y), text, fill='white', font=font)


def validate_image_type(ctx, param, value):
    options = [i.value for i in style]
    for option in options:
        if option.startswith(value):
            return option

    options = ', '.join(options)
    raise click.BadParameter(
        f"Invalid image style. Must be one of: {options}. \n"
        "You don't need to type the full style name, just enough to be unique.")


CONTEXT_SETTINGS = {
    'help_option_names':    ['-h', '--help'],
    # 'token_normalize_func': lambda x: x.lower(),
}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--size', '-s', nargs=2, type=int, default=(640, 480),
              help="Width and height of image in pixels.")
@click.option('--style', '-st',
              callback=validate_image_type,
              # type=click.Choice(style),
              default=style.CIRCLES.value,
              help="Style of image. The full string is not required, just enough to be unique.")
@click.option('--background-color', '-bc', type=str, default='#7D7D7D',
              help="Background color of image.")
@click.option('--extra-text', '-t', type=str, help="Text to add to image.")
@click.option('--show-preview', '-p', is_flag=True, help="Show image preview.")
@click.option('--save', '-sv', is_flag=True, help="Save image.")
def generate_images(save, show_preview, size, style, background_color, extra_text):
    """Generate random images"""

    if style == 'circles':
        image = generate_circles_image(size, background_color, extra_text)
    else:
        try:
            image = generate_descriptive_image(size, background_color, extra_text)
        except ValueError as e:
            print(f"Error: {e}")
            return

    if show_preview:
        image.show()
    if save:
        fsize = f"{size[0]}x{size[1]}"
        extra = '-' + extra_text.lower().replace(" ", "-") if extra_text else ""
        image.save(f"gi-{int(time.time())}-{fsize}{extra}.png")


if __name__ == '__main__':
    generate_images()
