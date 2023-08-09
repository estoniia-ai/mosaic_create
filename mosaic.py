from PIL import Image
import os
import random

def resize_crop(image, size):
    crop_size = 0
    if image.size[0] > image.size[1]:
        crop_size = image.size[1]
    else:
        crop_size = image.size[0]
    image = image.crop((0,0,crop_size,crop_size))
    image.thumbnail((size, size), Image.ANTIALIAS)
    return image

def get_target_pixels(image):
    width, height = image.size
    for x in range(0, width):
        for y in range(0, height):
            r, g, b = image.getpixel((x,y))
            average = int((r+g+b)/3)
            target_image_pixels.append(average)

def get_small_averages(path):
    for file in os.listdir(path):
        small_image = Image.open("{}/{}".format(path, file))
        resized_small_image = resize_crop(small_image, small_image_size)
        image_list.append(resized_small_image)

    for image in image_list:
        width, height = image.size
        r_total, g_total, b_total, count = 0, 0, 0, 0
        for x in range(width):
            for y in range(height):
                r, g, b = image.getpixel((x, y))
                r_total += r
                g_total += g
                b_total += b
                count += 1
        average_brightness = int((((r_total + g_total + b_total) / count) / 3))
        image_brightness_list.append(average_brightness)

def get_choices():
    threshold = 40
    for pixel in target_image_pixels:
        possible_matches = []
        for b in image_brightness_list:
            if abs(b - pixel) <= threshold:
                possible_matches.append(image_list[image_brightness_list.index(b)])
        
        if not possible_matches:
            possible_matches.append(random.choice(image_list))
            print("Added a random choice!")
        choice_list.append(random.choice(possible_matches))

def stitch():
    w, h = new_image.size
    count = 0
    for x in range(0, w, small_image_size):
        for y in range(0, h, small_image_size):
            new_image.paste(choice_list[count], (x, y))
            count += 1

def main():
    target_image_path = input("Enter the path to the target image: ")
    small_image_folder = input("Enter the path to the small images folder(folder should contain between 400-1,000 images for best results: ")
    final_size = int(input("Enter target height of final image (pixel values between 1,000-20,000 for best results): "))
    small_image_size = int(input("Enter the size of small images (pixel values between 50-200 for best results): "))
    
    image_list = []
    image_brightness_list = []
    new_image = Image.new('RGBA', (final_size, final_size))
    target_image = Image.open(target_image_path)
    target_image_alpha = Image.open(target_image_path).convert('RGBA')
    
    scale = int(final_size/small_image_size)
    target_image_pixels = []

    print("Resizing target image...")
    target_image = resize_crop(target_image, scale)
    target_image_alpha = resize_crop(target_image_alpha, final_size)

    print("Getting pixel values from target image...")
    get_target_pixels(target_image)

    print("Resizing and gathering pixel data from small images...")
    get_small_averages(small_image_folder)

    print("Calculating matches for pixels...")
    get_choices()

    print("Stitching images into final output image...")
    stitch()

    final_image = Image.blend(target_image_alpha, new_image, .65)
    
    print("Finished processing!")
    final_image.save("result.png")

if __name__ == '__main__':
    main()
