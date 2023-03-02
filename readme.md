# OpenMV Save Image Example

## About This Example
This example is a slightly modified version of OpenMV's offical jpg image transfer example. The original example can be found [here](https://github.com/openmv/openmv/tree/master/tools/rpc). In this example, the final image is saved to the local file system as well as being streamed to the viewer. Additionally, options have been added to allow the user to specify a delay in seconds. This delay may be useful if some setup time is required before the image is taken. If the delay is not desired, set the delay to 0. This example also includes the micropython firmware for the OpenMV camera in the for_camera folder. This firmware is required for the example to work. It is an unmodified version of the firmware found [here](https://github.com/openmv/openmv/blob/master/scripts/examples/08-RPC-Library/34-Remote-Control/image_transfer_jpg_as_the_remote_device_for_your_computer.py). The images are saved to the same directory that the script is run from with the name `imageN.jpg`, where N is the number of images taken.

## How to Use This Example
1. Connect the OpenMV camera to your computer via USB.
2. Copy the micropython firmware from the for_camera folder to the OpenMV camera's SD card, replacing any main.py file that already exists there.
3. **IMPORTANT:** If you are using a Windows computer, you must eject the camera from your computer before continuing. If you do not, the main.py file will not be updated.
4. Reset the OpenMV by unplugging the camera and plugging it back in.
5. In your terminal of choice, navigate to this folder and run `pip install -r requirements.txt`. This will install the required python packages.
6. Run `python main.py` to start the example.

## Note on python versions
This example has been tested with python 3.6.8. It may work with other versions of python 3, but it has not been tested.
On some systems, python 3 is aliased to python3. If this is the case, you will need to run `python3 main.py` instead of `python main.py` and `pip3` instead of `pip`.
