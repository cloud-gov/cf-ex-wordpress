#!/bin/bash

APP_ROOT=$(dirname "${BASH_SOURCE[0]}")

cd "$APP_ROOT" || exit
# mv manual-install S3-Uploads

# composer install

cp -R ../wp-content/* wp-content
