#!/bin/bash

if [ -f requirements.txt ]; then
  pip3 install -r requirements.txt
fi

locale

for key in $(compgen -v secrets_); do
  echo $key
  export ${key/secrets_/}=${ !key }
done
