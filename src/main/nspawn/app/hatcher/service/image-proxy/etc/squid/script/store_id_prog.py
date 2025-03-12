#!/usr/bin/env python3

import re
import sys
from urllib.parse import urlparse, urlunparse

domain_mapper = dict([
    (re.compile("(.+)[.](.+)[.]archive.org"), "local-squid.archive.org"),
])


def squash_domain(base_url:str) -> str:
    ""
    source_url = urlparse(base_url)
    source_host = source_url.hostname
    if source_host is not None:
        for pattern, target_host in domain_mapper.items():
            if pattern.match(source_host):
                target_loc = source_url.netloc.replace(source_host, target_host)
                target_url = source_url._replace(netloc=target_loc)
                return urlunparse(target_url)
    return base_url


def strip_query(full_url:str) -> str:
    ""
    term_url = full_url.split('?')
    base_url = term_url[0]
    return base_url


def produce_id(term_line:str) -> str:
    ""
    term_list = term_line.split(' ')
    full_url = term_list[0]
    base_url = strip_query(full_url)
    store_id = squash_domain(base_url)
    return store_id


def invoke_main():
    ""
    log_dir = "/var/log/squid"
    log_file = f"{log_dir}/store_id_prog.log"
    with open(log_file, "a") as logger:
        for term_line in sys.stdin:
            store_id = produce_id(term_line)
            sys.stdout.write(f"OK store-id={store_id}\n")
            sys.stdout.flush()
            logger.write(f"{store_id} <- {term_line}\n")


if __name__ == '__main__':
    invoke_main()
