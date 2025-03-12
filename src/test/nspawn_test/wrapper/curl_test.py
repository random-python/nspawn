from nspawn.wrapper.curl import Curl


def test_curl_head():
    url = "http://checkip.amazonaws.com/"
    path = "/tmp/test_curl_head.txt"
    curl = Curl()
    curl.with_url(url)
    curl.with_file_head(path)
    result = curl.execute_unit()
    print(result)
