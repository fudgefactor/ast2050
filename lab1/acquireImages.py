#=============================================================================
# Modified code that draws from FLIR's PyCapture2 Example
# Suresh Sivanandam (Jan 9, 2019)
# This code sets up camera parameters and takes a number of 8-bit TIFF images.
# All parameters are set to manual mode to ensure measurements are repeatable.
# You can set the gain and exposure time with this code.
# This code is compatible with Python 2.x
#=============================================================================

import PyCapture2

# Output FlyCapture Library Version being used.
def printBuildInfo():
	libVer = PyCapture2.getLibraryVersion()
	print("PyCapture2 library version: ", libVer[0], libVer[1], libVer[2], libVer[3])

# Output details about the camera
def printCameraInfo(cam):
	camInfo = cam.getCameraInfo()
	print("\n*** CAMERA INFORMATION ***\n")
	print("Serial number - ", camInfo.serialNumber)
	print("Camera model - ", camInfo.modelName)
	print("Camera vendor - ", camInfo.vendorName)
	print("Sensor - ", camInfo.sensorInfo)
	print("Resolution - ", camInfo.sensorResolution)
	print("Firmware version - ", camInfo.firmwareVersion)
	print("Firmware build time - ", camInfo.firmwareBuildTime)

# Setup camera to run in manual mode.
# We need to turn off things like auto exposure, image sharpening.
# This ensures that we always have a consistent setup when taking data.
def setupCamera(cam):
    cam.setProperty(type=PyCapture2.PROPERTY_TYPE.AUTO_EXPOSURE,onOff=False)
    cam.setProperty(type=PyCapture2.PROPERTY_TYPE.AUTO_EXPOSURE,autoManualMode=False)
    cam.setProperty(type=PyCapture2.PROPERTY_TYPE.SHARPNESS,onOff=False)
    cam.setProperty(type=PyCapture2.PROPERTY_TYPE.SHARPNESS,onOff=False)
    cam.setProperty(type=PyCapture2.PROPERTY_TYPE.SHARPNESS,autoManualMode=False)
    cam.setProperty(type=PyCapture2.PROPERTY_TYPE.SHUTTER,autoManualMode=False)
    cam.setProperty(type=PyCapture2.PROPERTY_TYPE.GAIN,autoManualMode=False)
    cam.setProperty(type=PyCapture2.PROPERTY_TYPE.SHUTTER,absControl=True)
    cam.setProperty(type=PyCapture2.PROPERTY_TYPE.GAIN,absControl=True)
    cam.setProperty(type=PyCapture2.PROPERTY_TYPE.FRAME_RATE,onOff=False)
    cam.setProperty(type=PyCapture2.PROPERTY_TYPE.FRAME_RATE,autoManualMode=False)

# Query the camera for the current exposure time (units: ms).    
def getExposureTime(cam):
    p = cam.getProperty(PyCapture2.PROPERTY_TYPE.SHUTTER)
    
    return(p.absValue)

# Set camera's exposure time (units: ms). The exposure time won't exactly be
# what you set because the camera has a fixed set of values to choose from
# but it will be close.
def setExposureTime(cam, time):
    p = cam.setProperty(type=PyCapture2.PROPERTY_TYPE.SHUTTER,absValue=time)
    print("Exposure Time Set To : %f ms" % getExposureTime(cam))

# Query the camera for the current gain value (units: dB).
def getGain(cam):
    p = cam.getProperty(PyCapture2.PROPERTY_TYPE.GAIN)
    
    return(p.absValue)    

# Set camera's gain (units: dB). The gain value won't exactly be
# what you set because the camera has a fixed set of values to choose from
# but it will be close.
def setGain(cam, gain):
    p = cam.setProperty(type=PyCapture2.PROPERTY_TYPE.GAIN,absValue=gain)
    print("Sensor Gain Set To : %f dB" % getGain(cam))

# Get the temperature of the camera. It has a tendency to heat up 
# quite a bit. Output in Celcius.
def getCameraTemperature(cam):
    p = cam.getProperty(PyCapture2.PROPERTY_TYPE.TEMPERATURE)
    
    return(p.absValue*100-273.0)

# This turns on time stamping of each image from the camera. You can see
# how long it takes to transfer one frame back to the computer. This is often
# longer than the exposure time because it includes the digitization, data
# transfer time, and file saving time.
def enableEmbeddedTimeStamp(cam, enableTimeStamp):
	embeddedInfo = cam.getEmbeddedImageInfo()
	if embeddedInfo.available.timestamp:
		cam.setEmbeddedImageInfo(timestamp = enableTimeStamp)
		if(enableTimeStamp):
			print("\nTimeStamp is enabled.\n")
		else:
			print("\nTimeStamp is disabled.\n")

# Grab a fixed number of images and save them with a filename header.
def grabImages(cam, numImagesToGrab,header='image'):
    prevts = None
    
    for i in xrange(numImagesToGrab):
        image = cam.retrieveBuffer()
        ts = image.getTimeStamp()
        
        if (prevts):
            diff = (ts.cycleSeconds - prevts.cycleSeconds) * 8000 + (ts.cycleCount - prevts.cycleCount)
            print("Timestamp [" + str(ts.cycleSeconds) + "," + str(ts.cycleCount) + "] " + str(diff))
        prevts = ts
        
        # Save image to TIFF
        filename = header + ("%05d.tiff" % i)
        newimg = image.convert(PyCapture2.PIXEL_FORMAT.MONO8)
        print("Saving the last image to ", filename)
        newimg.save(filename, PyCapture2.IMAGE_FILE_FORMAT.TIFF)
		
               
#
# Main Program
#

# Print PyCapture2 Library Information
printBuildInfo()

# Ensure sufficient cameras are found
bus = PyCapture2.BusManager()
numCams = bus.getNumOfCameras()
print("Number of cameras detected: %d" % numCams)
if not numCams:
	print("Insufficient number of cameras. Exiting...")
	exit()

# Select camera on 0th index (the first and only camera)
c = PyCapture2.Camera()
uid = bus.getCameraFromIndex(0)
c.connect(uid)

printCameraInfo(c)

# Print Camera Temperature
print("Camera Temperature: %f" % getCameraTemperature(c))

# Initialize Camera Parameters
setupCamera(c)

# Enable camera embedded timestamp
enableEmbeddedTimeStamp(c, True)

# Set up exposure time and gain of camera
setExposureTime(c,60)
setGain(c,12)

print("Starting image capture...")
c.startCapture()
grabImages(c, 100)
c.stopCapture()

# Disable camera embedded timestamp
enableEmbeddedTimeStamp(c, False)

c.disconnect()

raw_input("Done! Press Enter to exit...\n")
