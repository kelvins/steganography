#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import json
import numpy as np
from PIL import Image


class Steganography(object):

    @staticmethod
    def __change_char_at_string(string, char, index):
        """Efficient method for replacing a strings char at a given index.

        :param string: String to be edited
        :param char: Character to be inserted into string
        :param index: Index of character to be overwritten in string
        """
        l_str = list(string)
        l_str[index] = char
        return "".join(l_str)

    @staticmethod
    def __int_to_bin(rgb):
        """Convert an integer tuple to a binary (string) tuple.

        :param rgb: An integer tuple (e.g. (220, 110, 96))
        :return: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        """
        r, g, b = rgb[:3]
        return ('{0:08b}'.format(r),
                '{0:08b}'.format(g),
                '{0:08b}'.format(b))

    @staticmethod
    def __bin_to_int(rgb):
        """Convert a binary (string) tuple to an integer tuple.

        :param rgb: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        :return: Return an int tuple (e.g. (220, 110, 96))
        """
        r, g, b = rgb[:3]
        return (int(r, 2),
                int(g, 2),
                int(b, 2))

    @staticmethod
    def __merge_rgb(rgb1, rgb2):
        """Merge two RGB tuples.

        :param rgb1: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        :param rgb2: Another string tuple
        (e.g. ("00101010", "11101011", "00010110"))
        :return: An integer tuple with the two RGB values merged.
        """
        r1, g1, b1 = rgb1[:3]
        r2, g2, b2 = rgb2[:3]
        rgb = (r1[:4] + r2[:4],
               g1[:4] + g2[:4],
               b1[:4] + b2[:4])
        return rgb

    @staticmethod
    def merge(img1, img2):
        """Merge two images. The second one will be merged into the first one.

        :param img1: First image
        :param img2: Second image
        :return: A new merged image.
        """

        # Check the images dimensions
        if img2.size[0] > img1.size[0] or img2.size[1] > img1.size[1]:
            raise ValueError('Image 2 should not be larger than Image 1!')

        # Get the pixel map of the two images
        pixel_map1 = img1.load()
        pixel_map2 = img2.load()

        # Create a new image that will be outputted
        new_image = Image.new(img1.mode, img1.size)
        pixels_new = new_image.load()

        for i in range(img1.size[0]):
            for j in range(img1.size[1]):
                rgb1 = Steganography.__int_to_bin(pixel_map1[i, j])

                # Use a black pixel as default
                rgb2 = Steganography.__int_to_bin((0, 0, 0))

                # Check if the pixel map position is valid for the second image
                if i < img2.size[0] and j < img2.size[1]:
                    rgb2 = Steganography.__int_to_bin(pixel_map2[i, j])

                # Merge the two pixels and convert it to a integer tuple
                rgb = Steganography.__merge_rgb(rgb1, rgb2)

                pixels_new[i, j] = Steganography.__bin_to_int(rgb)

        return new_image

    @staticmethod
    def unmerge(img):
        """Unmerge an image.

        :param img: The input image.
        :return: The unmerged/extracted image.
        """

        # Load the pixel map
        pixel_map = img.load()

        # Create the new image and load the pixel map
        new_image = Image.new(img.mode, img.size)
        pixels_new = new_image.load()

        # Tuple used to store the image original size
        original_size = img.size

        for i in range(img.size[0]):
            for j in range(img.size[1]):
                # Get the RGB (as a string tuple) from the current pixel
                r, g, b = Steganography.__int_to_bin(pixel_map[i, j])[:3]

                # Extract the last 4 bits (corresponding to the hidden image)
                # Concatenate 4 zero bits because we are working with 8 bit
                rgb = (r[4:] + '0000',
                       g[4:] + '0000',
                       b[4:] + '0000')

                # Convert it to an integer tuple
                pixels_new[i, j] = Steganography.__bin_to_int(rgb)

                # If this is a 'valid' position, store it
                # as the last valid position
                if pixels_new[i, j] != (0, 0, 0):
                    original_size = (i + 1, j + 1)

        # Crop the image based on the 'valid' pixels
        new_image = new_image.crop((0, 0, original_size[0], original_size[1]))

        return new_image

    @staticmethod
    def insert_hex(img, hex_code, x, y, rgb):
        """Insert a hexadecimal pattern into the RGB values of an Image's pixels.

        :param img: PIL Image object
        :param hex_code: String of HEX code to be inserted into image
        :param x: X Co-ordinate of pixel pattern insertion should begin with
        :param y: Y Co-ordinate of pixel pattern insertion should begin with
        :param rgb: 2D array specifying which RGB values should be overwritten
        """
        # Converts NumPy array of 1 & 0 values to True & False values respectively as it plays better with np.sum
        rgb = np.array(json.loads(rgb), dtype=np.bool)

        # Gets indices of each RGB binary value to be overwritten
        rgb_indices = Steganography.__get_rgb_indices(rgb)

        # Gets binary of Hex Code
        bin_code = Steganography.__hex_to_bin(hex_code)

        # Tuple used to store the image original size
        original_size = img.size

        # Check if binary code can be inserted
        image_insert_size = ((original_size[0] - x) * (original_size[1] - y)) * len(rgb_indices)
        if image_insert_size < len(bin_code):
            print("Full length of hex code binary {} is too large for insertion space in image {}"
                  .format(len(bin_code), image_insert_size))
            return None

        # Load the pixel map
        pixel_map = img.load()

        # Set bin_code tracking vars
        bin_index = 0

        for i in range(x, img.size[0]):
            for j in range(y, img.size[1]):
                # Get the RGB (as a string tuple) from the current pixel
                rgb = list(Steganography.__int_to_bin(pixel_map[i, j]))

                # Insert binary code in given rgb indices
                for k in rgb_indices:
                    rgb[k[0]] = Steganography.__change_char_at_string(rgb[k[0]], bin_code[bin_index], k[1])
                    bin_index += 1

                    # If we have no more of the Hex pattern to insert
                    if bin_index == len(bin_code):
                        # Convert it to an integer tuple
                        pixel_map[i, j] = Steganography.__bin_to_int(rgb)
                        return img

                # Convert it to an integer tuple
                pixel_map[i, j] = Steganography.__bin_to_int(rgb)

        return img

    @staticmethod
    def get_hex_code(img, hex_length, x, y, rgb):
        """Extract a hexadecimal pattern from the RGB values of an Image's pixels.

        :param img: PIL Image object
        :param hex_length: Length of Hexadecimal pattern to be extracted
        :param x: X Co-ordinate of pixel pattern extraction should begin with
        :param y: Y Co-ordinate of pixel pattern extraction should begin with
        :param rgb: 2D array specifying which RGB values should be read
        """
        # Converts NumPy array of 1 & 0 values to True & False values respectively as it plays better with np.sum
        rgb = np.array(json.loads(rgb), dtype=np.bool)

        # Gets indices of each RGB binary value to be overwritten
        rgb_indices = Steganography.__get_rgb_indices(rgb)

        # Load the pixel map
        pixel_map = img.load()

        bin_pattern = ""
        for i in range(x, img.size[0]):
            for j in range(y, img.size[1]):
                # Get the RGB (as a string tuple) from the current pixel
                rgb = list(Steganography.__int_to_bin(pixel_map[i, j]))

                # Extract binary from given rgb indices
                for k in rgb_indices:
                    bin_pattern += rgb[k[0]][k[1]]

                    if len(bin_pattern) == hex_length * 4:
                        return Steganography.__bin_to_hex(bin_pattern)[2:]

        return Steganography.__bin_to_hex(bin_pattern)[2:]

    @staticmethod
    def __hex_to_bin(s):
        """Converts a String of Hexadecimal to a Binary String.

        :param s: String of Hexadecimal code
        :return: Binary String
        """
        return bin(int(s, 16))[2:].zfill(len(s) * 4)

    @staticmethod
    def __bin_to_hex(s):
        """Converts a String of Binary to a Hexadecimal String.

        :param s: String of Binary code
        :return: Hexadecimal String
        """
        return hex(int(s, 2))

    @staticmethod
    def __get_rgb_indices(rgb):
        """Returns Co-ordinates if all true/truthy values in a 2D array

        :param rgb: 2D array
        :return: List of tuples containing co-ordinates of true/truthy values in rgb
        """
        indices = []
        for (index, value) in np.ndenumerate(rgb):
            if rgb[index[0]][index[1]]:
                indices.append(index)
        return indices


@click.group()
def cli():
    pass


@cli.command()
@click.option('--img1', required=True, type=str, help='Image that will hide another image')
@click.option('--img2', required=True, type=str, help='Image that will be hidden')
@click.option('--output', required=True, type=str, help='Output image')
def merge(img1, img2, output):
    merged_image = Steganography.merge(Image.open(img1), Image.open(img2))
    merged_image.save(output)


@cli.command()
@click.option('--img', required=True, type=str, help='Image that will be hidden')
@click.option('--output', required=True, type=str, help='Output image')
def unmerge(img, output):
    unmerged_image = Steganography.unmerge(Image.open(img))
    unmerged_image.save(output)


@cli.command()
@click.option('--img', required=True, type=str, help='Image to insert hex code into')
@click.option('--hex_code', required=True, type=str, help='Hex code to be inserted into the image')
@click.option('--output', required=True, type=str, help='Output Image')
@click.option('--x', required=False, type=int, default=0, help='X Co-ordinate for pixel that hex_insertion beings with.'
                                                               ' Defaults to 0.')
@click.option('--y', required=False, type=int, default=0, help='Y Co-ordinate for pixel that hex_insertion begins with.'
                                                               ' Defaults to 0.')
@click.option('--rgb', required=False, type=str,
              help='2D JSON Array (3x8) of [1/0] values to indicate which RGB values should be overwritten. '
                   'Defaults to the four LSBs of each RGB value.',
              default="[[0,0,0,0,1,1,1,1],[0,0,0,0,1,1,1,1],[0,0,0,0,1,1,1,1]]")
# Default RGB values to be overwritten:
#        0  1  2  3  4  5  6  7
#       _______________________
# R)  0 |0  0  0  0  1  1  1  1
# G)  1 |0  0  0  0  1  1  1  1
# B)  2 |0  0  0  0  1  1  1  1
def insert_hex_code(img, hex_code, output, x, y, rgb):
    hexed_image = Steganography.insert_hex(Image.open(img), hex_code, x, y, rgb)
    hexed_image.save(output)


@cli.command()
@click.option('--img', required=True, type=str, help='Image to retrieve hex code from')
@click.option('--hex_length', required=True, type=int, help='Length of Hex Pattern to be retrieved')
@click.option('--x', required=False, type=int, default=0, help='X Co-ordinate for pixel that hex_insertion beings with.'
                                                               ' Defaults to 0.')
@click.option('--y', required=False, type=int, default=0, help='Y Co-ordinate for pixel that hex_insertion begins with.'
                                                               ' Defaults to 0.')
@click.option('--rgb', required=False, type=str,
              help='2D JSON Array (3x8) of [1/0] values to indicate which RGB values should be overwritten. '
                   'Defaults to the four LSBs of each RGB value.',
              default="[[0,0,0,0,1,1,1,1],[0,0,0,0,1,1,1,1],[0,0,0,0,1,1,1,1]]")
# Default RGB values to be overwritten:
#        0  1  2  3  4  5  6  7
#       _______________________
# R)  0 |0  0  0  0  1  1  1  1
# G)  1 |0  0  0  0  1  1  1  1
# B)  2 |0  0  0  0  1  1  1  1
def get_hex_code(img, hex_length, x, y, rgb):
    extracted_pattern = Steganography.get_hex_code(Image.open(img), hex_length, x, y, rgb)
    print("Extracted pattern: \n\n{}\n{}".format(extracted_pattern, "" if len(extracted_pattern) == hex_length else
        "Extracted pattern doesn't match hex_length. This can be caused by placing X & Y too far into the image."))


if __name__ == '__main__':
    cli()
