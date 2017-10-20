#!/bin/bash

if [[ "$1" == "start" ]]; then
  if [[ -f {{ BASE }}/workshop/.clean ]]; then
    su - stack -c {{ BASE }}/devstack/stack.sh
    rm {{ BASE }}/workshop/.clean
  fi
fi
