#!/usr/bin/env bash

#
# verify option="lowerdir+":" 
# https://docs.kernel.org/filesystems/overlayfs.html
#

lower1="/var/lib/nspawn/extract/localhost//var/lib/nspawn/tempdir/provision/alpine/image-server/default-3.11.3-x86_64.tar.gz/"
lower2="/var/lib/nspawn/extract/dl-cdn.alpinelinux.org/alpine/v3.11/releases/x86_64/alpine-minirootfs-3.11.3-x86_64.tar.gz/"
lower3="/var/lib/nspawn/runtime/nspawn-image-server/zero"
upper0="/var/lib/nspawn/runtime/nspawn-image-server/root"
work0="/var/lib/nspawn/runtime/nspawn-image-server/work"
base0="/var/lib/machines/nspawn-image-server"

#sudo ls -las $base0
#sudo ls -las $wor0
#sudo ls -las $upper0
#sudo ls -las $lower1
#sudo ls -las $lower2
#sudo ls -las $lower3

sudo umount $base0

#sudo sync

sudo /usr/bin/mount \
	-t overlay \
	-o xino=on \
	-o index=off \
	-o metacopy=off \
	-o lowerdir+=$lower1 \
	-o lowerdir+=$lower2 \
	-o lowerdir+=$lower3 \
	-o upperdir=$upper0 \
	-o workdir=$work0 \
	 overlay $base0

#
#
#
	 