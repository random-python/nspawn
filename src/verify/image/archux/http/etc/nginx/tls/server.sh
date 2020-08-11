#!/bin/sh

set -e -u

# https://smoothnet.org/squid-proxy-with-ssl-bump/

# https://github.com/vmware/ansible-kubernetes-ca/blob/master/tasks/main.yml

dir=$(dirname $0)
ca_key=$dir/server-key.pem
ca_req=$dir/server-req.pem
ca_cert=$dir/server-cert.pem
ca_subj="/O=server"

openssl genrsa -out $ca_key 2048
openssl req -new -batch -key $ca_key -out $ca_req -subj $ca_subj 
openssl x509 -req -days 10000 -in $ca_req -signkey $ca_key -out $ca_cert  
