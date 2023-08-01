#!/bin/bash

# Copy wordpress files into web root folder (htdocs)
cd "$HOME/app/wordpress" || exit
cp -R ./* "$HOME/app/htdocs"
