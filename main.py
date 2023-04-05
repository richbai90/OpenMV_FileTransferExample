import pygame
import os
import sys
import camera
import logging
import processing


def load_images_from_folder(folder, start, end) -> tuple:
    '''Load a given number of images from a folder into a list of Pygame images

    Load images beginning at the start index and ending at the end index (exclusive) from the given folder into a list of Pygame images.

    Parameters
    ----------
    folder : str The folder containing the images
    start : int The index of the first image to load
    end : int The index of the last image to load (exclusive)

    Returns
    -------
    tuple(list, bool, int) A tuple containing a list of Pygame images, a boolean indicating whether the last image was loaded, and the index of the last image loaded
    '''
    last_img = False
    image_files = sorted([os.path.join(folder, f) for f in os.listdir(
        folder) if f.endswith(".jpg") or f.endswith(".png")])
    if len(image_files) == 0:
        raise Exception("No images found in the given folder")
    if len(image_files) < end:
        end = len(image_files)
        last_img = True
    return ([pygame.image.load(f).convert() for f in image_files[start:end]], last_img, end)


if __name__ == "__main__":
    # Set up logging
    # Configure the logging system
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("log.txt"),
            logging.StreamHandler()
        ])
    logger = logging.getLogger(__name__)
    # check for help flag
    if len(sys.argv) > 1 and sys.argv[1] == "-h":
        print("Usage: python3 main.py [image_folder] [delay] [img_path]")
        print("")
        print("Arguments:")
        print("image_folder: The path to the folder containing the images")
        print("delay: The delay between each image (in milliseconds)")
        print("img_path: The path to the folder where the images will be saved")
    # Prompt user for inputs unless they are provided as command line arguments
    if len(sys.argv) > 1:
        image_folder = sys.argv[1]
        delay = int(sys.argv[2])
        img_path = sys.argv[3]
        interface = sys.argv[4]
    else:
        image_folder = input(
            "Enter the path to the folder containing the images: ")
        delay = int(
            input("Enter the delay between each image (in milliseconds): "))
        img_path = input(
            "Enter the path to the folder where the images will be saved: ")
        interface = camera.get_interface()

    # Set up the Pygame environment
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    # Set the initial image and start time
    current_image = 0
    start_time = pygame.time.get_ticks()
    screen_info = pygame.display.Info()

    # Main loop
    start_index = 0
    end_index = 100
    imgs_displayed = 0
    load_first_batch = True
    last_img = False
    images = []
    img_captured = False
    while True:
        # Handle the loading of images in batches of 100
        # As well as the loading of the last batch of images
        # And the stopping of the program when the last image is displayed
        if imgs_displayed >= end_index or load_first_batch:
            load_first_batch = False
            if (last_img):
                logger.debug("Last image displayed")
                break
            # Load the next 100 images and set the start index to the last image.
            # This is done to prevent loading the same images multiple times.
            # If the last image was loaded, set the end index to the last image
            # This is done to prevent attempting to load images that don't exist
            images, last_img, start_index = load_images_from_folder(
                image_folder, start_index, end_index)
            load_new_images = False
            # If the last image was loaded, set the end index to the last image
            if not last_img:
                logger.debug(f"Loaded images {start_index} to {end_index}")
                end_index = start_index + 100
            else:
                logger.debug(f"Loaded last image {start_index}")
                end_index = start_index

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Get the elapsed time since the last image was displayed
        # So that the next image can be displayed after the delay
        elapsed_time = pygame.time.get_ticks() - start_time

        # Handle the display of the next image
        # And the resetting of the start time and captured image flag
        if elapsed_time >= delay:
            logger.debug(f"Elapsed time: {elapsed_time}")
            current_image = (current_image + 1) % len(images)
            start_time = pygame.time.get_ticks()
            imgs_displayed += 1
            img_captured = False

        # Handle the capture of the image
        # This is done after the delay/2 to ensure that the correct image is being displayed
        if elapsed_time >= delay/2 and not img_captured:
            imgs = [img for img in map(lambda _: camera.capture_image(interface, exposure_us=500), range(10)) if img is not None]
            # stack images
            img = processing.stackImagesECC(imgs)
            if img is not None:
                processing.save_image(img, os.path.join(img_path, str(imgs_displayed) + ".jpg"))
                img_captured = True
                logger.debug(f"Captured image {imgs_displayed}.jpg")
            else:
                logger.debug(f"No image captured for {imgs_displayed}")
            # If the image is None, then the camera didn't capture an image and the code will try again on the next frame
            # This will continue until the camera captures an image or the next image is displayed

        # Clear the screen
        screen.fill((0, 0, 0))

        # Calculate the center of the screen
        center_x = screen_info.current_w / 2
        center_y = screen_info.current_h / 2

        # Get the current image and its dimensions
        img = images[current_image]
        img_width, img_height = img.get_size()

        # Calculate the position to center the image on the screen
        img_x = center_x - img_width / 2
        img_y = center_y - img_height / 2

        # Draw the current image to the screen
        screen.blit(img, (img_x, img_y))
        pygame.display.flip()

        # Wait for the next frame
        clock.tick(60)
