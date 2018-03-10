
from PIL import Image


class ImageMerge(object):

    def __init__(self):
        pass

    @staticmethod
    def int_to_bin(value):
        return '{0:08b}'.format(int(value))

    @staticmethod
    def bin_to_int(value):
        return int(str(value), 2)

    @staticmethod
    def merge(image_path1, image_path2):

        img1 = Image.open(image_path1)
        img2 = Image.open(image_path2)

        pixel_map1 = img1.load()
        pixel_map2 = img2.load()

        new_image = Image.new(img1.mode, img1.size)
        new_image.resize(img1.size, Image.ANTIALIAS)
        pixels_new = new_image.load()

        for i in range(img1.size[0]):
            for j in range(img1.size[1]):
                r1 = ImageMerge.int_to_bin(pixel_map1[i,j][0])
                g1 = ImageMerge.int_to_bin(pixel_map1[i,j][1])
                b1 = ImageMerge.int_to_bin(pixel_map1[i,j][2])

                r2 = "00000000"
                g2 = "00000000"
                b2 = "00000000"

                if i < img2.size[0] and j < img2.size[1]:
                    r2 = ImageMerge.int_to_bin(pixel_map2[i,j][0])
                    g2 = ImageMerge.int_to_bin(pixel_map2[i,j][1])
                    b2 = ImageMerge.int_to_bin(pixel_map2[i,j][2])

                r = r1[:4] + r2[:4]
                g = g1[:4] + g2[:4]
                b = b1[:4] + b2[:4]

                r = ImageMerge.bin_to_int(r)
                g = ImageMerge.bin_to_int(g)
                b = ImageMerge.bin_to_int(b)

                pixels_new[i,j] = (r,g,b,255)

        return new_image

    @staticmethod
    def unmerge(image_path):

        img = Image.open(image_path)

        pixel_map = img.load()

        new_image = Image.new(img.mode, img.size)
        pixels_new = new_image.load()

        for i in range(img.size[0]):
            for j in range(img.size[1]):
                r1 = ImageMerge.int_to_bin(pixel_map[i,j][0])
                g1 = ImageMerge.int_to_bin(pixel_map[i,j][1])
                b1 = ImageMerge.int_to_bin(pixel_map[i,j][2])

                r2 = r1[4:] + "0000"
                g2 = g1[4:] + "0000"
                b2 = b1[4:] + "0000"

                r1 = r1[:4] + "0000"
                g1 = g1[:4] + "0000"
                b1 = b1[:4] + "0000"

                r1 = ImageMerge.bin_to_int(r1)
                g1 = ImageMerge.bin_to_int(g1)
                b1 = ImageMerge.bin_to_int(b1)

                r2 = ImageMerge.bin_to_int(r2)
                g2 = ImageMerge.bin_to_int(g2)
                b2 = ImageMerge.bin_to_int(b2)

                pixel_map[i,j] = (r1,g1,b1,255)
                pixels_new[i,j] = (r2,g2,b2,255)

        return img, new_image

if __name__ == "__main__":
    path1 = "res/img2.jpg"
    path2 = "res/img4.png"

    final_image = ImageMerge.merge(path1, path2)
    final_image.save("result_image.png")
    final_image.show()

    unmerged_image1, unmerged_image2 = ImageMerge.unmerge("result_image.png")
    unmerged_image1.show()
    unmerged_image2.show()
