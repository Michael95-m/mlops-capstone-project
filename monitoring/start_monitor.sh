#!/bin/bash

python create_db.py

python prepare_reference_data.py

gunicorn --bind 0.0.0.0:5020 monitor:app