import cv2
import numpy as np
import rpc
import struct
import serial.tools.list_ports

def get_interface():
    # list available ports
    ports = serial.tools.list_ports.comports()
    print("Available ports:")
    for port in ports:
        print(port.device)
    
    input_port = int(input("Enter the port you want to use: "))
    port = ports[input_port].device
    interface = rpc.rpc_usb_vcp_master(port=port) # Change this to the port you are using.
    return interface




def get_frame_buffer_call_back(interface, pixformat_str="sensor.GRAYSCALE", framesize_str="sensor.VGA", framerate_str="10", cutthrough=True, silent=True):
    ''' Gets a frame buffer from the remote device.

    Gets a frame buffer in JPEG format from the remote device
    and returns it as a bytearray. If cutthrough is True then the data is transferred in one large chunk with no error checking.
    If cutthrough is False then the data is transferred in 32 KB chunks with error checking.

    Parameters
    ----------
    pixformat_str : str (optional) The pixel format to use. Default is "sensor.GRAYSCALE".
    framesize_str : str (optional) The frame size to use. Default is "sensor.VGA". (VGA = 640x480)
    framerate_str : str (optional) The frame rate to use. Default is "10".
    cutthrough : bool (optional) If True then the data is transferred in one large chunk with no error checking. If False then the data is transferred in 32 KB chunks with error checking. Default is True.
    silent : bool (optional) If True then no debug messages are printed. Default is True.
    '''
    if not silent:
        print("Getting Remote Frame...")

    result = interface.call("jpeg_image_snapshot", "%s,%s" %
                            (pixformat_str, framesize_str, framerate_str))
    if result is not None:

        size = struct.unpack("<I", result)[0]
        img = bytearray(size)

        if cutthrough:
            # Fast cutthrough data transfer with no error checking.

            # Before starting the cut through data transfer we need to sync both the master and the
            # slave device. On return both devices are in sync.
            result = interface.call("jpeg_image_read")
            if result is not None:

                # GET BYTES NEEDS TO EXECUTE NEXT IMMEDIATELY WITH LITTLE DELAY NEXT.

                # Read all the image data in one very large transfer.
                interface.get_bytes(img, 5000)  # timeout

        else:
            # Slower data transfer with error checking.

            # Transfer 32 KB chunks.
            chunk_size = (1 << 15)

            if not silent:
                print("Reading %d bytes..." % size)
            for i in range(0, size, chunk_size):
                ok = False
                for j in range(3):  # Try up to 3 times.
                    result = interface.call(
                        "jpeg_image_read", struct.pack("<II", i, chunk_size))
                    if result is not None:
                        img[i:i+chunk_size] = result  # Write the image data.
                        if not silent:
                            print("%.2f%%" % ((i * 100) / size))
                        ok = True
                        break
                    if not silent:
                        print("Retrying... %d/2" % (j + 1))
                if not ok:
                    if not silent:
                        print("Error!")
                    return None

        return img

    else:
        if not silent:
            print("Failed to get Remote Frame!")

    return None


def capture_image(interface: rpc.rpc_usb_vcp_master) -> np.ndarray:
    ''' Captures an image from the remote device.
    
    Captures an image from the remote device and returns it as a numpy array. Suitable for use with OpenCV.
    
    Parameters
    ----------
    interface : rpc.rpc_usb_vcp_master The interface to use.
    '''    
    img = get_frame_buffer_call_back(interface)
    if img is not None:
        # save the image to a file
        np_arr = np.frombuffer(img, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
        return image
    return None
