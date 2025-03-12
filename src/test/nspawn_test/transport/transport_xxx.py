# import io
# import abc
# import email
# import pycurl
# from urllib.parse import urlparse
# 
# 
# class Provider(abc.ABC):
#     
#     def parse(self, local_url:str, remote_url:str):
#         self.local = urlparse(local_url)
#         self.remote = urlparse(remote_url)
#         pass
# 
#     @abc.abstractclassmethod
#     def head(self, remote_url:str) -> None:
#         pass    
#     
#     @abc.abstractclassmethod
#     def get(self, local_url:str, remote_url:str) -> None:
#         pass    
# 
#     @abc.abstractclassmethod
#     def put(self, local_url:str, remote_url:str) -> None:
#         pass    
# 
#         
# class ProviderCurl(Provider):
#     
#     def parse_header(self, buffer):
#         header = buffer.getvalue().decode("utf-8")
#         request_line, headers_text = header.split('\r\n', 1)
#         message = email.message_from_string(headers_text)
#         return dict(message.items())
#     
#     def progress(self, get_sum, get_now, put_sum, put_now):
#         # print(f"get_sum={get_sum} get_now={get_now} put_sum={put_sum} put_now={put_now}")
#         pass
#     
#     def head(self, remote_url:str) -> None:
#         buffer = io.BytesIO()
#         curl = pycurl.Curl()
#         curl.setopt(curl.NOBODY, True)
#         curl.setopt(curl.HEADERFUNCTION, buffer.write)
#         curl.setopt(curl.URL, remote_url)
#         curl.perform()
#         curl.close()
#         return self.parse_header(buffer)
# 
#     def get(self, local_url, remote_url):
#         return self.raw_get(local_url, remote_url)
# 
#     def put(self, local_url, remote_url):
#         return self.raw_put(local_url, remote_url)
#     
#     def raw_get(self, local_url, remote_url):
#         self.parse(local_url, remote_url)
#         with open(self.local.path, 'wb') as file:
#             curl = pycurl.Curl()
#             curl.setopt(curl.NOPROGRESS, False)
#             curl.setopt(curl.XFERINFOFUNCTION, self.progress)
#             curl.setopt(curl.WRITEDATA, file)
#             curl.setopt(curl.URL, remote_url)
#             curl.perform()
#             curl.close()
# 
#     def raw_put(self, local_url, remote_url):
#         self.parse(local_url, remote_url)
#         with open(self.local.path, 'rb') as file:
#             curl = pycurl.Curl()
#             curl.setopt(curl.NOPROGRESS, False)
#             curl.setopt(curl.XFERINFOFUNCTION, self.progress)
#             curl.setopt(curl.READDATA, file)
#             curl.setopt(curl.URL, remote_url)
#             curl.setopt(curl.UPLOAD, 1)
#             curl.perform()
#             curl.close()
# 
# 
# def transport_provider(remote_url: str) -> Provider:
#     remote = urlparse(remote_url)
#     if remote.scheme == 'http':
#         return ProviderCurl()
#     elif remote.scheme == 'https':
#         return ProviderCurl()
#     else:
#         raise Exception(f'unknown url={remote_url}')
