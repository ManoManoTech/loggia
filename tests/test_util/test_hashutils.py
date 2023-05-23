from datetime import datetime

from mm_utils.utils.hashutils import HashableDict, HashableList, deep_hashable, hashable


def test_hashable_dict():
    assert hash(HashableDict(dict(a=1))) is not None
    assert hash(HashableDict({})) == hash(HashableDict({}))


def test_hashable_list():
    assert hash(HashableList([1, 2, 3])) is not None
    assert hash(HashableList()) == hash(HashableList())
    assert hash(HashableList()) == hash(HashableList([]))
    assert hash(HashableList((1, 2, 3))) != hash(HashableList((3, 2, 1)))


def test_hashable():
    # Boxing types
    assert hash(hashable([4, 3, 2])) == hash(hashable([4, 3, 2]))
    assert hash(hashable(dict(a=1, b=2))) == hash(hashable(dict(b=2, a=1)))

    # Already hashable types
    assert hash("abc") == hash(hashable("abc"))
    now = datetime.now()
    assert hash(hashable(now)) == hash(now)


def test_deep_hashable_1():
    d = dict(a=1, b=dict(ba=1, bb=[dict(bba=1, bbb=dict()), dict(bca=1, bcb=dict())]))
    d_ = dict(a=1, b=dict(ba=1, bb=[dict(bba=1, bbb=dict()), dict(bca=1, bcb=dict())]))

    assert hash(deep_hashable(d)) == hash(deep_hashable(d_))
    assert hash(deep_hashable(d["b"]["bb"][1]["bcb"])) is not None


def test_deep_hashable_2():
    d = [
        dict(a=1, b=[dict(baa=2, bab=3), [dict(bbaa=4, bbab=5), dict(bbba=6, bbbb=7)]]),
        "x",
        [dict(x=1000)],
    ]
    d_ = [
        dict(a=1, b=[dict(baa=2, bab=3), [dict(bbaa=4, bbab=5), dict(bbba=6, bbbb=7)]]),
        "x",
        [dict(x=1000)],
    ]

    assert hash(deep_hashable(d)) == hash(deep_hashable(d_))
    assert hash(deep_hashable(d[-1][0])) is not None
