#Project WebVRApp

The Project WebVRApp is an attempt to bring existing Linux applications
to be available for VR display using Web browser.

#Requirements
## 1. VR Display
![Image of Google Cardboard] (https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Google-Cardboard.jpg/800px-Google-Cardboard.jpg )

## 2. Smartphone 
![Image of Google Cardboard] (https://upload.wikimedia.org/wikipedia/commons/d/dc/Samsung_Galaxy_S_White.png )

## 3. Chrome 
![Image of Google Cardboard] (https://upload.wikimedia.org/wikipedia/en/d/d0/Chrome_Logo.svg )

#Installation setup
## Linux Tools Installation
 $sudo apt-get install python-virtualenv

 $sudo apt-get install libjpeg8-dev

 $sudo apt-get install libudev-dev

 $sudo apt-get install xserver-xephyr

 $tar -xzf python-uinput-0.10.2.tar.gz

 $cd python-uinput

 $python setup.py build

 $python setup.py install

 $sudo apt-get install imagemagick

 $sudo apt-get install scrot

## Python installation
 $virtualenv localpy

 $source localpy/bin/activate
	
 $pip install -U -r requirements.txt


#Usage

$modprobe uinput

$chown pi.pi /dev/uinput

$source localpy/bin/activate

(localpy)$cd WebVRApp/src

(localpy)$crossbar start

