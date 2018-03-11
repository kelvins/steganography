
import time
import argparse
from PIL import Image


class ImageMerge(object):

    @staticmethod
    def __int_to_bin(rgb):
        """
        Convert an integer tuple to a binary (string) tuple.
        :param rgb: An integer tuple (e.g. (220, 110, 96))
        :return: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        """
        r, g, b = rgb
        return ('{0:08b}'.format(r),
                '{0:08b}'.format(g),
                '{0:08b}'.format(b))

    @staticmethod
    def __bin_to_int(rgb):
        """
        Convert a binary (string) tuple to an integer tuple.
        :param rgb: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        :return: Return an int tuple (e.g. (220, 110, 96))
        """
        r, g, b = rgb
        return (int(r, 2),
                int(g, 2),
                int(b, 2))

    @staticmethod
    def __merge_rgb(rgb1, rgb2):
        """
        Merge two RGB tuples.
        :param rgb1: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        :param rgb2: Another string tuple (e.g. ("00101010", "11101011", "00010110"))
        :return: An integer tuple with the two RGB values merged.
        """
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        rgb = (r1[:4] + r2[:4],
               g1[:4] + g2[:4],
               b1[:4] + b2[:4])
        return rgb

    @staticmethod
    def merge(img1, img2):
        """
        Merge two images. The second one will be merged into the first one.
        :param img1: First image
        :param img2: Second image
        :return: A new merged image.
        """

        # Get the pixel map of the two images
        pixel_map1 = img1.load()
        pixel_map2 = img2.load()

        # Create a new image that will be outputted
        new_image = Image.new(img1.mode, img1.size)
        pixels_new = new_image.load()

        for i in range(img1.size[0]):
            for j in range(img1.size[1]):
                rgb1 = ImageMerge.__int_to_bin(pixel_map1[i, j])

                # Use a black pixel as default
                rgb2 = ImageMerge.__int_to_bin((0, 0, 0))

                # Check if the pixel map position is valid for the second image
                if i < img2.size[0] and j < img2.size[1]:
                    rgb2 = ImageMerge.__int_to_bin(pixel_map2[i, j])

                # Merge the two pixels and convert it to a integer tuple
                rgb = ImageMerge.__merge_rgb(rgb1, rgb2)

                pixels_new[i, j] = ImageMerge.__bin_to_int(rgb)

        return new_image

    @staticmethod
    def unmerge(img):
        """
        Unmerge an image.
        :param img: The input image.
        :return: The unmerged/extracted image.
        """

        # Load the pixel map
        pixel_map = img.load()

        # Create the new image and load the pixel map
        new_image = Image.new(img.mode, img.size)
        pixels_new = new_image.load()

        for i in range(img.size[0]):
            for j in range(img.size[1]):
                # Get the RGB (as a string tuple) from the current pixel
                r, g, b = ImageMerge.__int_to_bin(pixel_map[i, j])

                # Extract the last 4 bits (corresponding to the hidden image)
                # Concatenate 4 zero bits because we are working with 8 bit values
                rgb = (r[4:] + "0000",
                       g[4:] + "0000",
                       b[4:] + "0000")

                # Convert it to an integer tuple
                pixels_new[i, j] = ImageMerge.__bin_to_int(rgb)

        return new_image

if __name__ == "__main__":
    # Construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_image1", type=str, required=True, help="Path to the input image 1")
    ap.add_argument("--input_image2", type=str, required=False, help="Path to the input image 2")
    ap.add_argument("--output_image", type=str, required=False, help="Path to the output image")
    args = vars(ap.parse_args())

    # Get the current date time (e.g. 20180215221510)
    curr_time = time.strftime("%Y%m%d%H%M%S")

    # If the output image1 path is empty, set a unique name for it
    if not args["output_image"]:
        args["output_image"] = "output_image_" + curr_time + ".png"

    # If the input_image2 argument is valid (not empty), the user
    # is trying to merge two images, so call the merge method
    if args["input_image2"]:
        img1 = Image.open(args["input_image1"])
        img2 = Image.open(args["input_image2"])
        merged_image = ImageMerge.merge(img1, img2)
        merged_image.save(args["output_image"])
    # Else, try to unmerge the image
    else:
        img = Image.open(args["input_image1"])
        unmerged_image = ImageMerge.unmerge(img)
        unmerged_image.save(args["output_image"])
