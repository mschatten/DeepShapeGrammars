#!/usr/bin/env bash

PATHS=$(readlink --canonicalize /var/lib/flatpak/app/org.gimp.GIMP/*/beta/*/files/lib/gimp/2.99/plug-ins)

IFS=' ' read -r -a INSTALL_PATHS <<< "$PATHS"

INSTALL_PATH=${INSTALL_PATHS[0]}

echo ""
echo "Installing deep-shape-grammars plug-in to:"
echo "$INSTALL_PATH"
echo ""

cd src
sudo cp -r deep-shape-grammars $INSTALL_PATH
sudo chmod +x $INSTALL_PATH/deep-shape-grammars/deep-shape-grammars.py

echo "Finished!"




