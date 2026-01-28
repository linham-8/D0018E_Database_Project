#!/bin/bash

trap "kill 0" EXIT
tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch &
python app.py
wait
