#!/usr/bin/env bash
python3 manage.py flush --no-input
python3 manage.py migrate
python3 manage.py test
if [[ $? -eq 0 ]]
then
    python3 manage.py runserver 0.0.0.0:80
fi;
