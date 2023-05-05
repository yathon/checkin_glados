#!/bin/bash

if [ -f requirements.txt ]; then
  pip3 install -r requirements.txt
fi

for key in $( compgen -v ); do
  export ${key}=${ !key }
done
