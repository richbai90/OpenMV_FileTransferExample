from PIL import Image
import io
import rpc
import struct

interface = rpc.rpc_usb_vcp_master(port="COM4") # Change this to the port you are using.

if interface is None:
    print("Failed to connect to the remote device!")
    exit()


def get_frame_buffer_call_back(pixformat_str="sensor.GRAYSCALE", framesize_str="sensor.B128X128", cutthrough=True, silent=True):
    ''' Gets a frame buffer from the remote device.

    Gets a frame buffer in JPEG format from the remote device
    and returns it as a bytearray. If cutthrough is True then the data is transferred in one large chunk with no error checking.
    If cutthrough is False then the data is transferred in 32 KB chunks with error checking.

    Parameters
    ----------
    pixformat_str : str (optional) The pixel format to use. Default is "sensor.GRAYSCALE".
    framesize_str : str (optional) The frame size to use. Default is "sensor.B128X128" (128x128px).
    cutthrough : bool (optional) If True then the data is transferred in one large chunk with no error checking. If False then the data is transferred in 32 KB chunks with error checking. Default is True.
    silent : bool (optional) If True then no debug messages are printed. Default is True.
    '''
    if not silent:
        print("Getting Remote Frame...")

    result = interface.call("jpeg_image_snapshot", "%s,%s" %
                            (pixformat_str, framesize_str))
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


def get_image():
    img = get_frame_buffer_call_back()
    if img is not None:
        # save the image to a file
        image = Image.open(io.BytesIO(img))
        return image
    return None
