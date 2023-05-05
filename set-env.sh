#!/bin/bash

if [ -f requirements.txt ]; then
  pip3 install -r requirements.txt
fi

echo "compgen ====="
compgen -v
echo "compgen ====="

for key in $(compgen -v secrets_); do
  echo $key
  export ${key/secrets_/}=${ !key }
done
