#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!

def get_pixel(image, x, y):
    pixel = image['pixels'][flat_index(image, x, y)]
    return pixel

def set_pixel(image, x, y, c):
    image['pixels'][flat_index(image, x, y)] = c


def apply_per_pixel(image, func):
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:],
    }
    for x in range(image['width']):
        for y in range(image['height']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result

def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)

# HELPER FUNCTIONS
def flat_index(image, x, y):
    """
    Given coordinates for x and y, returns the appropriate location for where the 
    pixel of that x, y coordinate should be. 
    """
    return x + y*image['width']

def getPixelUnbounded(image, x, y):
    """
    If x and y are out of the bounds of the image, returns a pixel that is extended
    from the closest pixel from that coordinate pair.
    """
    #normal case
    if x >= 0 and x <= (image['width'] - 1) and y >= 0 and y <= (image['height'] - 1):
        pixel = get_pixel(image, x, y)
    #out of bounds from top left corner
    elif x < 0 and y >= 0 and y <= (image['height'] - 1):
        pixel = get_pixel(image, 0, y)
    elif x >= 0 and x <= (image['width'] - 1) and y < 0:
        pixel = get_pixel(image, x, 0)
    elif x < 0 and y < 0:
        pixel = get_pixel(image, 0, 0)

    #out of bounds from top right corner 
    elif x > image['width'] - 1 and y >= 0 and y <= (image['height'] - 1):
        pixel = get_pixel(image, image['width'] - 1, y)
    elif x <= (image['width']) - 1 and x >= 0 and y < 0:
        pixel = get_pixel(image, x, 0)
    elif x > (image['width']) - 1 and y < 0:
        pixel = get_pixel(image, image['width'] - 1, 0)
    
    # #out of bounds bottom left corner 
    elif x < 0 and y <= (image['height'] - 1) and y >= 0:
        pixel = get_pixel(image, 0, y) 
    elif x >= 0 and x <= (image['width'] - 1) and y > (image['height']) - 1:
        pixel = get_pixel(image, x, (image['height'] - 1))
    elif x < 0 and y > (image['height']) - 1:
        pixel = get_pixel(image, 0, (image['height'] - 1))

    #out of bounds bottom right corner
    elif x > (image['width']) - 1 and y <= (image['height']) - 1:
        pixel = get_pixel(image, (image['width'] - 1), y)
    elif x <= (image['width']) - 1 and y > (image['height']) - 1:
        pixel = get_pixel(image, x, (image['height'] - 1))
    elif x > (image['width']) - 1 and y > (image['height']) - 1:
        pixel = get_pixel(image, (image['width'] - 1), (image['height'] - 1)) 

    return pixel

def correlate(image, kernel):
    """
    Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    The kernel will be represented in the same way as how the list for pixels was represented
    in a dictionary. It will rely upon the flat_index helper function I created earlier to 
    represent the x and y system of the kernel.
    """
    #find center of kernel
    kernelCenterX = int(kernel['width']/2) 
    kernelCenterY = int(kernel['height']/2)
    #apply operations of kernel starting from center out to edges to calculate the number

    # change number of location applied to new number
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:],
    }

    #the first two for loops parse through every pixel in the image 
    for x in range(result['width']):
        for y in range(result['height']):
            sum = 0
            startPositionX = x - kernelCenterX
            #the second two for loops are used to parse through each element of the kernel when applying the kernel to a specific pixel
            for x2 in range(0, kernel['width']):
                startPositionY = y - kernelCenterY
                for y2 in range(0, kernel['height']):
                    sum += getPixelUnbounded(image, startPositionX, startPositionY) * get_pixel(kernel, x2, y2)
                    startPositionY += 1
                startPositionX += 1
            set_pixel(result, x, y, sum)
    return result

def boxBlurCreator(n):
    """
    Given an integer n, return a kernel of size n x n where all the elements of 
    the kernel add up to 1.
    """
    val = 1/(n*n)
    pixels = [val]*n*n
    kernel = {
        'height': n,
        'width': n,
        'pixels': pixels,
    } 
    return kernel

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    roundedPixels = []
    for item in image['pixels']:
        if item > 255:
            roundedPixels.append(255)
        elif item < 0:
            roundedPixels.append(0)
        elif isinstance(item, float):
            roundedPixels.append(round(item))

    roundedImage = {
        'height': image['height'],
        'width': image['width'],
        'pixels': roundedPixels
    }
    return roundedImage

# FILTERS

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel = boxBlurCreator(n)

    # then compute the correlation of the input image with that kernel
    imageCorrelated = correlate(image, kernel)
    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    imageCorrelated = round_and_clip_image(imageCorrelated)
    return imageCorrelated

def blurredUnrounded(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image. However, the values are not 
    rounded to proper standards.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel = boxBlurCreator(n)

    # then compute the correlation of the input image with that kernel
    imageCorrelated = correlate(image, kernel)
    return imageCorrelated

def sharpened(image, n):
    """
    Return a new image representing the result of applying an unsharp 
    mask to the given input image.

    This process should not mutate the input image; rather, it should create a 
    separate structure to represent the output.
    """
    blurredImage = blurredUnrounded(image, n)
    sharpenedImage = {
        'height': image['height'],
        'width': image['width'],
        'pixels': []
    }
    for i in range(0, len(image['pixels'])):
        sharpenedImage['pixels'].append(2*image['pixels'][i] - blurredImage['pixels'][i])
    sharpenedImage = round_and_clip_image(sharpenedImage)
    return sharpenedImage

def edges(image):
    """
    Takes an image as an input and returns a new image where the edges should 
    be emphasized.

    This process should not mutate the input image; rather, it should create a 
    separate structure to represent the output.
    """
    kernelX = {
        'height': 3,
        'width': 3,
        'pixels': [-1, 0, 1,
                   -2, 0, 2,
                   -1, 0, 1]
    }

    kernelY = {
        'height': 3,
        'width': 3,
        'pixels': [-1, -2, -1,
                    0, 0, 0,
                    1, 2, 1]
    }
    Ox = correlate(image, kernelX)
    Oy = correlate(image, kernelY)

    edgedImage = {
        'height': image['height'],
        'width': image['width'],
        'pixels': []
    }

    for i in range(0, len(image['pixels'])):
        edgedImage['pixels'].append(math.sqrt((Ox['pixels'][i])**2 + (Oy['pixels'][i])**2))
    
    edgedImage = round_and_clip_image(edgedImage)
    return edgedImage




# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    pass


