#!/bin/sh

# http://wiki.squid-cache.org/Features/StoreID

base=$(dirname $0)

#url="http://download.oracle.com/otn-pub/java/jce/8/jce_policy-8.zip?AuthParam=1465952700_368f05a55369f4f4e95e8430a2d1b3a3"
#url="http://download.oracle.com/otn-pub/java/jdk/8u92-b14/jdk-8u92-linux-x64.tar.gz?AuthParam=1465954431_534cee932ed1b6efc4c08bdd483c5591"
#echo "$url" | $base/store_id.sh 

export log_dir="$base"

invoke() {
    echo "line 0: $line"
    echo $line | $base/store_id_prog.sh
    busybox sh -c "echo $line" | busybox sh -c "$base/store_id_prog.sh"
}

echo

line="http://download.oracle.com/otn-pub/java/jce/8/jce_policy-8.zip 192.168.1.103/192.168.1.103 - GET myip=192.168.1.137 myport=3128"
invoke

echo

line="http://download.oracle.com/otn-pub/java/jce/8/jce_policy-8.zip?AuthParam=1468794966_3ec82d3de3b479a3fc7faec9ca20180b 192.168.1.103/work3 - GET myip=192.168.1.137 myport=3128"
invoke
