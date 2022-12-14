import pytest

from mm_utils.utils.dictutils import get_all, get_in, get_path_in, make_fast_get_in, mapdict, set_in, set_in_path
from mm_utils.utils.hashutils import HashableDict

DICO_A = dict(a=2, b=dict(ba=3, bb=4, bc=dict(bca=5, bcb=6, bcd=707)))


def test_get_in_bad_signature():
    with pytest.raises(AssertionError):
        assert get_in(DICO_A, "nonsense") is None

    with pytest.raises(AssertionError):
        assert get_in(DICO_A, DICO_A) is None

    with pytest.raises(AssertionError):
        assert get_in(DICO_A, (1, 2, 3)) is None


def test_get_in_path():
    assert get_path_in(DICO_A, "a") == 2
    assert get_path_in(DICO_A, "nope") is None
    assert get_path_in(DICO_A, "nope", "ehh") == "ehh"
    assert get_path_in(DICO_A, "b.bb") == 4
    assert isinstance(get_path_in(DICO_A, "b.bc"), dict)
    assert get_path_in(DICO_A, "b.bc.bca") == 5


def test_set_in():
    d = dict(a=1, b=dict(ba=1, bb=dict(bba=1, bbb=dict())))

    set_in(d, ["x"], 1000)
    assert d["x"] == 1000

    set_in(d, ["b", "x"], 2000)
    assert d["b"]["x"] == 2000

    set_in(d, ["b", "bb", "bbb", "x"], 3000)
    assert d["b"]["bb"]["bbb"]["x"] == 3000

    with pytest.raises(KeyError):
        set_in(d, ["y", "z", "zz"], 42)  # no subdict there, it should raise

    set_in(d, ["y", "z", "zz", "zzz", "zzzz", "zzzzz", "zzzzzz"], 42, create=True)
    assert d["y"]["z"]["zz"]["zzz"]["zzzz"]["zzzzz"]["zzzzzz"] == 42


def test_set_in_path():
    d = dict(a=1, b=dict(ba=1, bb=dict(bba=1, bbb=dict())), bob=42)

    set_in_path(d, "b.bb.bbb.x", 4242)
    assert d["b"]["bb"]["bbb"]["x"] == 4242

    set_in_path(d, "y.z.zz.zzz.zzzz.zzzzz.zzzzzz", 5000, create=True)
    assert d["y"]["z"]["zz"]["zzz"]["zzzz"]["zzzzz"]["zzzzzz"] == 5000

    e = dict()
    set_in_path(e, "simple", "test")
    assert e["simple"] == "test"

    with pytest.raises(KeyError):  # facepalm error type
        set_in_path(d, "bob.x", 1000)  # bob is not a subdict, so it should raise

    with pytest.raises(KeyError):
        set_in_path(d, "b.ba.x", 1000)  # b.ba is not a subdict, so it should raise


def test_mapdict():
    d = dict(a=1, b=dict(ba=1, bb=dict(bba=1, bbb=dict())))
    d_ = mapdict(d, HashableDict)
    assert id(d) != id(d_)
    assert isinstance(d_, HashableDict)
    assert isinstance(d_["b"], HashableDict)
    assert isinstance(d_["b"]["bb"], HashableDict)
    assert isinstance(d_["b"]["bb"]["bbb"], HashableDict)


def compiled_get_in(dict_, keys, default=None):
    compiled_fn = make_fast_get_in(keys, default)
    return compiled_fn(dict_)


@pytest.mark.parametrize("get_in_fn", [get_in, compiled_get_in])
def test_get_in(get_in_fn):
    assert get_in_fn(DICO_A, ["a"]) == 2
    assert get_in_fn(DICO_A, ["nonsense"], 4242) == 4242
    assert get_in_fn(DICO_A, ["b", "nonsense", "c"], 4242) == 4242
    assert get_in_fn(DICO_A, ["b", "ba"]) == 3
    assert get_in_fn(DICO_A, ["b", "bc", "bcd"]) == 707
    assert get_in_fn(DICO_A, ["b", "bc", "bcohno"]) is None
    assert get_in_fn(DICO_A, ["b", "bc", "bcohnoNONONO"], "nope") == "nope"

    d = dict(a=1, b=dict(ba=2, bbs=[dict(c=dict(d=3)), dict(c=dict(d=4))]))
    assert get_in_fn(d, ["a"]) == 1
    assert get_in_fn(d, ["b", "ba"]) == 2
    # assert get_in(d, ["b", "bbs", "*", "c", ",*"]) == [3, 4] # ",*" support is vaporware

    assert get_in_fn(d, ["b", "no"], "toto!") == "toto!"


def test_get_all_in():
    d = dict(a=1, b=dict(ba=2, bbs=[dict(c=dict(d=3)), dict(c=dict(d=4))]))
    assert get_all(d, ["b", "bbs", "*", "c", "d"]) == [3, 4]
    assert get_all(d, ["b", "bbs", "*", "c", "e"], "toto!") == ["toto!", "toto!"]
    assert get_all(d, ["b", "bbs", "*", "c", "tutu"], "toto!") == ["toto!", "toto!"]

    d2 = [11, 12, 13]
    assert get_all(d2, ["*"]) == [11, 12, 13]

    d3 = [[11, 12, 13], [21, 22, 23], [31, 32, 33]]
    assert get_all(d3, ["*", "*"]) == [11, 12, 13, 21, 22, 23, 31, 32, 33]

    d4 = dict(
        a="aa", b=["bb", "bbb"], c=dict(d="e"), f=dict(g="gg", h=[dict(i="ii", j="jj", k="kk"), dict(i="iii", j="jj", k="klk", l="ll")])
    )
    assert get_all(d4, ["*", "h", "*", "i"]) == ["ii", "iii"]
    assert get_all(d4, ["*", "h", "*", "*"]) == ["ii", "jj", "kk", "iii", "jj", "klk", "ll"]
