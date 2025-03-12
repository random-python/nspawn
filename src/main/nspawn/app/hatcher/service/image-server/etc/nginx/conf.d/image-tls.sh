#!/usr/bin/env sh

#
# image server
#

# generate tls keys
# https://smoothnet.org/squid-proxy-with-ssl-bump/
# https://github.com/vmware/ansible-kubernetes-ca/blob/master/tasks/main.yml

set -e -u

dir=$(dirname $0)
ca_key=$dir/image-key.pem
ca_csr=$dir/image-req.pem
ca_cert=$dir/image-cert.pem
ca_subj="/O=image"

openssl genrsa -out $ca_key 2048
openssl req -new -batch -key $ca_key -out $ca_csr -subj $ca_subj 
openssl x509 -req -days 10000 -in $ca_csr -signkey $ca_key -out $ca_cert  
