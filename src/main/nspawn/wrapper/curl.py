"""
Wrapper for curl
https://curl.haxx.se/docs/manpage.html
"""

from nspawn.wrapper.base import Base
from nspawn.wrapper.sudo import Sudo


class Curl(Base):

    base = Sudo()

    def __init__(self):
        super().__init__('wrapper/curl')

    def with_url(self, url):
        self.with_option('url', url)
        return self

    def with_file_get(self, path):
        self.with_option('output', path)
        return self

    def with_file_put(self, path):
        self.with_option('upload-file', path)
        return self

    def with_file_head(self, path):
        self.with_option('output', path)
        self.with_option('head')
        return self

    def with_dump_header(self, path):
        self.with_option('dump-header', path)
        return self

    def with_header(self, text):
        self.with_option('header', text)
        return self

    # needs curl 7.49
    def with_connect_to(self, source_host, source_port, target_host, target_port):
        self.with_option('connect-to', f"{source_host}:{source_port}:{target_host}:{target_port}")
        return self

    def with_auth_basic(self, username, password):
        self.with_option('user', f"{username}:{password}")
        return self

    def with_auth_token(self, token):
        self.with_header(f"Authorization: Token {token}")
        return self

    def with_content_type(self, content_type):
        self.with_header(f"Content-Type: {content_type}")
        return self

    def with_no_proxy(self, entry_list:str):
        self.with_option('noproxy', entry_list)
        return self

    def with_proxy_entry(self, proxy_entry:str):
        self.with_option('proxy', proxy_entry)
        return self
