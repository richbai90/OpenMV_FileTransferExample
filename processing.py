import cv2
import numpy as np


def stackImagesECC(im_list: np.ndarray):
    '''Stacks images using ECC algorithm and returns the final image.
    
    Stacks images using ECC algorithm and returns the final image. 
    ECC lets us deal with more complex transformations than traditional image alignment techniques.
    
    Parameters
    ----------
    im_list : np.ndarray (required) A list of grayscale images to be stacked.
    '''
    M = np.eye(3, 3, dtype=np.float32) # Identity Homography matrix (initialization)
    
    first_image:  np.ndarray = None # variable for storing the first image to compare with others
    stacked_image: np.ndarray = None # output variable for the stacked image
    
    for img in im_list:
        # Normalize pixel intensity of each image to [0-1] range 
        # because perspective transform is sensitive to brightness variations
        image = img.astype(np.float32) / 255
        
        if first_image is None:
            # if it is the first image, use it as a reference image and initialize the output variable
            first_image = image
            stacked_image = image
        else:
            # Estimate perspective transform between current image and reference (first) image
            # by finding the optical flow between two images using ECC algorithm
            # ECC lets us deal with more complex transformations than traditional image alignment techniques
            s, M = cv2.findTransformECC(
                image, first_image, M, cv2.MOTION_HOMOGRAPHY)
            
            w, h, _ = image.shape # width, height of the image
            
            # Correcting Image Alignment with respect to First_Image
            # Warping perspective transforms the source image (new frame) using known transformation matrix and size of the new image.
            image = cv2.warpPerspective(image, M, (h, w)) 
            stacked_image += image

    # Average the aligned images
    stacked_image /= len(im_list)
    
    # Scale back the image pixel values to [0-255] range and change type to uint8
    stacked_image = (stacked_image*255).astype(np.uint8)

    # return the final stacked-image
    return stacked_image
