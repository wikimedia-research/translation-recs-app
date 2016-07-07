sudo apt-get update
sudo apt-get install python3 python3-dev build-essentials libatlas-base-dev gfortran
curl https://bootstrap.pypa.io/get-pip.py | sudo python3.4
sudo python3 -m pip install uwsgi flask requests futures numpy

sudo apt-get install nginx
