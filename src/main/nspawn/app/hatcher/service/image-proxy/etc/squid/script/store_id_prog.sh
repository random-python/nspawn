#!/bin/sh

set -e
#set -x

# http://wiki.squid-cache.org/Features/StoreID

# http://www.squid-cache.org/Doc/config/store_id_program/

# archive site pattern
#readonly prefix="http://download.oracle.com/otn-pub"

# transform input url to store id response
#readonly command="s%${prefix}/(.+)\?.+%OK store-id=${prefix}/\1%"
#readonly command="s%(${prefix})/(.+)(\?).+%OK store-id=\1/\2%"

[[ "$log_dir" ]] || log_dir="/var/log/squid"

log() {
    [[ -e "$log_dir" ]] || return 0
    echo "$1" >> "$log_dir/store_id_prog.log"
}

# line: head'?'tail' 'rest

while IFS='\n'; read line; do
    log "### $(date)"
    log "1: $line"
    
    IFS=' '; set -- $line
    line=$1 # no rest
    log "2: $line"
    
    IFS='?'; set -- $line
    line=$1 # no tail
    log "3: $line"
    
    echo "OK store-id=$line"
done
