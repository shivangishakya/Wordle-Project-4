#!/bin/sh

# Check if command hypercorn exist
if [ -x "$(command -v hypercorn.exe)" ]; then
  # For use with WSL/WSL2
  hypercorn.exe "$@";
elif [ -f "/mnt/c/Program Files (Portable & CMD)/python/Scripts/hypercorn.exe" ]; then
  # Manual resolve
  "/mnt/c/Program Files (Portable & CMD)/python/Scripts/hypercorn.exe" "$@";
else
  # Normal way to works with Tuffix
  hypercorn "$@";
fi

kill -TERM -$$