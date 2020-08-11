
from nspawn.support.header import *


def test_header():
    print()
    head_dict = {
        'etag':'some-hash',
        'last-modified':'some-time',
        'content-length':'some-size',
        'nspawn-digest':'some-text',
    }
    assert head_dict[Header.etag] == 'some-hash'
    assert head_dict[Header.last_modified] == 'some-time'
    assert head_dict[Header.content_length] == 'some-size'
    assert head_dict[Header.nspawn_digest] == 'some-text'


def test_compare_head():
    print()
    assert compare_header({
    }, {
    }) == HeadComp.undetermined
    assert compare_header({
        'etag':'123'
    }, {
        'etag':'"123"'
    }) == HeadComp.same
    assert compare_header({
        'last-modified':'some-time',
        'content-length':'some-size',
    }, {
        'last-modified':'some-time',
        'content-length':'some-size',
    }) == HeadComp.same
    assert compare_header({
        'last-modified':'some-time',
        'content-length':'some-size-1',
    }, {
        'last-modified':'some-time',
        'content-length':'some-size-2',
    }) == HeadComp.different
    assert compare_header({
        'last-modified':'some-time',
    }, {
        'content-length':'some-size',
    }) == HeadComp.undetermined

