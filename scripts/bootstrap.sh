#!/bin/bash

APP_ROOT="$HOME"

# $HOME env var changes depending on whether you're in the
# running "lifecycle" shell or SSH session shell
if [[ $HOME != *"app"* ]]; then
  APP_ROOT="$APP_ROOT/app"
fi

# Copy wordpress files into web root folder if they
# haven't been already
if [ ! -d "$APP_ROOT/htdocs/wp-content" ]; then
  echo "Copying Wordpress files into place"
  cd "$APP_ROOT/wordpress" || exit
  cp -R ./* "$APP_ROOT/htdocs"
fi
