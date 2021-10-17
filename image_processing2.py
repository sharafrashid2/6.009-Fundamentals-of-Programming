#!/usr/bin/env python3

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image


# CODE FROM LAB 1 (replace with your code)

# HELPER FUNCTIONS FROM LAB 1
def flat_index(image, x, y):
    """
    Given coordinates for x and y, returns the appropriate location for where the 
    pixel of that x, y coordinate should be. 
    """
    return x + y*image['width']

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

# FILTERS FROM LAB 1

def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)

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


#LAB 2 HELPER FUNCTIONS
def imageColorSplitter(image, color):
    """
    Given an image and a color name that is a string (either 'red', 'green', or 
    'blue') as an input, returns an image that contains pixels of only that 
    input color.
    """
    unicolorPixels = []
    if color == 'red':
        i = 0
    elif color == 'green':
        i = 1
    elif color == 'blue':
        i = 2
    else:
        raise ValueError('Choose a color that is either red, green, or blue')

    for pixel in image['pixels']:
        unicolorPixels.append(pixel[i])

    unicolorImage = {
        'height': image['height'],
        'width': image['width'],
        'pixels': unicolorPixels
    }

    return unicolorImage

def imageColorCombiner(imageRed, imageGreen, imageBlue):
    """
    Given three images of same height and width that are each of a single, different color, the 
    function combines them into an image with RGB color pixels represented as a tuple.
    """

    colorsCombined = zip(imageRed['pixels'], imageGreen['pixels'], imageBlue['pixels'])
    coloredPixels = []
    for pixel in colorsCombined:
        coloredPixels.append(pixel)
    coloredImage = {
        'height': imageRed['height'],
        'width': imageRed['width'],
        'pixels': coloredPixels
    }
    return coloredImage

# LAB 2 FILTERS

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def colorFilter(image):
        colors = []
        colors.extend((imageColorSplitter(image, 'red'), imageColorSplitter(image, 'green'), imageColorSplitter(image, 'blue')))
        coloredPixelsFiltered = [filt(color) for color in colors]
        return imageColorCombiner(coloredPixelsFiltered[0], coloredPixelsFiltered[1], coloredPixelsFiltered[2])
    return colorFilter

def make_blur_filter(n):
    """
    Given an input n, creates a blur filter that takes an image and applys a box blur filter
    of size n to it.
    """
    def newBlurred(image):
        return blurred(image, n)
    return newBlurred   


def make_sharpen_filter(n):
    """
    Given an input n, creates a sharpen filter that takes an image and sharpens it using a 
    box blur filter of size n.
    """
    def newSharpen(image):
        return sharpened(image, n)
    return newSharpen   


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def applyCascade(image):
        filteredImage = {'width': image['width'], 'height': image['height'], 'pixels': image['pixels'][:]}
        for filter in filters:
            filteredImage = filter(filteredImage)
        return filteredImage
    return applyCascade



# SEAM CARVING

# Main Seam Carving Implementation

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image.
    """
    nSeamCarves = [oneSeamCarve] * ncols
    apply = filter_cascade(nSeamCarves)
    return apply(image)


# Optional Helper Functions for Seam Carving

def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    greyscaleIm = {'width': image['width'], 'height': image['height'], 'pixels': []}
    for pixel in image['pixels']:
        v = round(.299 * pixel[0] + .587 * pixel[1] + .114 * pixel[2])
        greyscaleIm['pixels'].append(v)
    return greyscaleIm


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    energy = edges(grey)
    return energy


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    # the cumulative energy map starts with energy map's top row duplicated
    energyMap = {'width': energy['width'], 'height': energy['height'], 'pixels': energy['pixels'][:][0:energy['width']]}

    # 
    for y in range(1, energy['height']):
        for x in range(0, energy['width']):
            adjacentPixels = [getPixelUnbounded(energyMap, x-1, y-1), getPixelUnbounded(energyMap, x, y-1), getPixelUnbounded(energyMap, x+1, y-1)]
            if (x-1) < 0:
                adjacentPixels.remove(getPixelUnbounded(energyMap, x-1, y-1))
            elif (x+1) >= energy['width']:
                adjacentPixels.remove(getPixelUnbounded(energyMap, x+1, y-1))
            minAdj = min(adjacentPixels)
            energyMap['pixels'].append(get_pixel(energy, x, y) + minAdj)
    return energyMap
    


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    path = []
    #finding min val pixel in bottom row
    bottomRowPosition = cem['height'] - 1
    minVal = 1e99
    minPosX = 0
    for x in range(0, cem['width']):
        if get_pixel(cem, x, bottomRowPosition) < minVal:
            minVal = get_pixel(cem, x, bottomRowPosition)
            minPos = flat_index(cem, x, bottomRowPosition)
            minPosX = x
    path.append(minPos)

    #finding the remaining path
    for y in range(bottomRowPosition - 1, -1, -1):
        minVal = 1e99
        for x in range(minPosX-1, minPosX+2):
            if 0 <= x < cem['width']:
                if get_pixel(cem, x, y) < minVal:
                    minVal = get_pixel(cem, x, y)
                    minPos = flat_index(cem, x, y)
                    minPosX = x
        path.append(minPos)
    path.reverse()
    return path


def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    result = {'width': image['width'] - 1, 'height': image['height'], 'pixels': []}
    for i in range(0, len(image['pixels'])):
        if i not in seam:
            result['pixels'].append(image['pixels'][i])
    return result

def oneSeamCarve(image):
    """
    Given a (color) image, uses the seamcarving technique to remove one column of pixels
    from the image.
    """
    result = greyscale_image_from_color_image(image)
    result = compute_energy(result)
    result = cumulative_energy_map(result)
    path = minimum_energy_seam(result)
    result = image_without_seam(image, path)
    return result

#Drawing Primitives
def rectangle(image, x, y, r, g, b, length, width):
    """
    Given an image, draws a rectangle of a specified length, width, and color (using r, g, b
    values) at the specified coordinates (x, y point) over the image.
    """
    imageDrawn = {'width': image['width'], 'height': image['height'], 'pixels': image['pixels'][:]}
    for xIndex in range(x, x + length):
        imageDrawn['pixels'][flat_index(image, xIndex, y)] = (r,g,b)
        imageDrawn['pixels'][flat_index(image, xIndex, y + width)] = (r,g,b)
    for yIndex in range(y, y + width):
        imageDrawn['pixels'][flat_index(image, x, yIndex)] = (r,g,b)
        imageDrawn['pixels'][flat_index(image, x + length, yIndex)] = (r,g,b)
    return imageDrawn

def circle(image, centerX, centerY, r, g, b, radius):
    """
    Given an image, draws a circle of a specified radius and color (using r, g, b
    values) at the specified coordinates (x, y point) over the image.
    """
    imageDrawn = {'width': image['width'], 'height': image['height'], 'pixels': image['pixels'][:]}
    for theta in range(0, 361):
        x = round(radius*math.cos(theta))
        y = round(radius*math.sin(theta))
        imageDrawn['pixels'][flat_index(image, centerX + x, centerY + y)] = (r,g,b)
    return imageDrawn

def line(image, r, g, b, x1, y1, x2, y2):
    """
    Given an image, draws a line connecting the two specified coordinates (of x, y points) over
    the image.
    """
    imageDrawn = {'width': image['width'], 'height': image['height'], 'pixels': image['pixels'][:]}
    x = x1
    if x2 > x1:
        slopeAtoB = (y2 - y1)/(x2 - x1)
        y = y1
        for delta in range(x1, x2):
            x = delta
            y += slopeAtoB
            print(x, y)
            imageDrawn['pixels'][flat_index(image, x, round(y))] = (r,g,b)
    elif x1 > x2:
        slopeBtoA = (y1 - y2)/(x1 - x2)
        y = y2
        for delta in range(x2, x1):
            x = delta
            y += slopeBtoA
            imageDrawn['pixels'][flat_index(image, x, round(y))] = (r,g,b)
    return imageDrawn




# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
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


def save_greyscale_image(image, filename, mode='PNG'):
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

    original = load_color_image('test_images/sparrowchick.png')
    original = circle(original, 50, 100, 137, 207, 240, 40)
    original = circle(original, 150, 75, 255, 87, 51, 20)
    original = circle(original, 250, 40, 88, 24, 69, 30)
    original = rectangle(original, 50, 300, 218, 247, 166, 60, 40)
    original = rectangle(original, 125, 250, 137, 207, 240, 40, 10)
    original = rectangle(original, 250, 350, 255, 195, 0, 30, 30)
    original = line(original, 255, 255, 255, 275, 250, 200, 350)
    original = line(original, 0, 0, 0, 275, 235, 225, 120)
    original = line(original, 255, 255, 255, 50, 50, 50, 50)
    save_color_image(original, 'test.png')
