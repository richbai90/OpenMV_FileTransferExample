::Prompt for the path to jpg stream
set /p jpgstream=Enter the path to the jpg stream:
::Prompt for the path to the output directory
set /p outputdir=Enter the path to the output directory:
::Prompt for the path to slideshow app
set /p slideshowapp=Enter the path to the slideshow app:
::Prompt for the images path
set /p imagespath=Enter the path to the images:
::Prompt for delay time for camera
set /p delaytime=Enter the delay time for the camera:
::Prompt for the camera port
set /p cameraport=Enter the camera port:
::Prompt for slideshow interval
set /p slideshowinterval=Enter the slideshow interval:

cd %outputdir%
::Start the jpgstream
%slideshowapp% %imagespath% -i %slideshowinterval%
py %jpgstream% -d %delaytime% -p %cameraport%


