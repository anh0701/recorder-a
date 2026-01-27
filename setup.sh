#!/bin/bash

python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt

# sudo apt update
# sudo apt install -y ffmpeg libxcb-cursor0