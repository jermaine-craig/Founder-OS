#!/usr/bin/env bash
set -e

REPO="https://github.com/jermaine-craig/Founder-OS.git"
DIR="Founder-OS"

echo "Installing Founder OS..."

# Clone if not already in the repo
if [ ! -f "setup.py" ]; then
    if [ -d "$DIR" ]; then
        echo "  $DIR already exists, using existing directory"
        cd "$DIR"
    else
        git clone "$REPO" "$DIR"
        cd "$DIR"
    fi
fi

# Run the setup wizard
python3 setup.py
