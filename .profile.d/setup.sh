#!/bin/bash
#
#  Setup wp-content on SSHFS
#   Author:  Daniel Mikusa <dmikusa@pivotal.io>
#     Date:  4/23/2015
#

# move scripts out of public directory
mv "$HOME/htdocs/scripts" "$HOME/"

# If there's an SSHFS, mount it
SSHFS_CREDS=$(echo $VCAP_SERVICES | "$HOME/scripts/json.sh" | grep '\["sshfs"\]' | awk '{print $2}')
if [ "$SSHFS_CREDS" != "" ]; then
    echo "Found SSHFS, mounting to 'wp-content' directory"
    # path to wp-content directory, this is where we mount the sshfs
    WP_CONTENT="$HOME/htdocs/wp-content"
    # move WP defaults to /tmp to save a copy
    mv "$WP_CONTENT" /tmp/wp-content
    # create a directory where we can mount sshfs
    mkdir -p "$WP_CONTENT"
    # use mountie to mount sshfs
    BROKER_HOST=`echo $VCAP_SERVICES | "$HOME/scripts/json.sh" | grep '\["sshfs",0,"credentials","host"\]' | awk '{print $2}' | tr -d '"'`
    curl -s "http://$BROKER_HOST/assets/mountie" -o "$HOME/scripts/mountie"
    chmod +x "$HOME/scripts/mountie"
    cd "$HOME/htdocs/"
    "$HOME/scripts/mountie"
    echo "Done"
    df -h
    # copy WP original files to sshfs, -u makes it skip if remote is newer
    rsync -rtvu /tmp/wp-content "$WP_CONTENT"
    # remove WP original files
    rm -rf /tmp/wp-content
    # write a warning file to sshfs, in case someone looks at the mount directly
    WF="$WP_CONTENT/ WARNING_DO_NOT_EDIT_THIS_DIRECTORY"
    echo "!! WARNING !! DO NOT EDIT FILES IN THIS DIRECTORY!!\n" > "$WF"
    echo "These files are managed by a WordPress instance running " >> "$WF"
    echo "on CloudFoundry.  Editing them directly may break things " >> "$WF"
    echo " and changes may be overwritten the next time the " >> "$WF"
    echo "application is staged on CloudFoundry.\n" >> "$WF"
    echo "YOU HAVE BEEN WARNED!!" >> "$WF"
    # we're done
fi
