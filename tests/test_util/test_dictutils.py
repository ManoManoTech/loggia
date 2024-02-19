import logging.config  # noqa: TCH003

from loggia.utils.dictutils import deep_merge_log_config, del_if_possible, del_many_if_possible, mv_attr


def test_mv_attr():
    # Test setup
    obj = {"a": 1, "b": 2}

    # Function call
    mv_attr(obj, "a", "c")

    # Check result
    assert obj == {"c": 1, "b": 2}


def test_del_if_possible():
    # Test setup
    obj = {"a": 1, "b": 2}

    # Function call
    del_if_possible(obj, "a")

    # Check result
    assert obj == {"b": 2}


def test_del_many_if_possible():
    # Test setup
    obj = {"a": 1, "b": 2, "c": 3}

    # Function call
    del_many_if_possible(obj, ["a", "b"])

    # Check result
    assert obj == {"c": 3}


def test_deep_merge_log_config():
    # Test setup
    dict_cfg: logging.config._DictConfigArgs = {
        "disable_existing_loggers": False,
        "version": 1,
        "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
    }

    opt_dict_cfg: logging.config._DictConfigArgs = {
        "version": 1,
        "handlers": {"console": {"level": "INFO"}},
        "root": {"handlers": ["console"]},
    }

    # Expected result
    expected: logging.config._DictConfigArgs = {
        "disable_existing_loggers": False,
        "version": 1,
        "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple", "level": "INFO"}},
        "root": {"handlers": ["console"]},
    }

    # Function call
    result = deep_merge_log_config(dict_cfg, opt_dict_cfg)

    # Check result
    assert result == expected


def test_mv_attr_missing_key():
    # Test setup
    obj = {"a": 1, "b": 2}

    # Function call
    mv_attr(obj, "c", "d")

    # Check result
    assert obj == {"a": 1, "b": 2}


def test_del_if_possible_missing_key():
    # Test setup
    obj = {"a": 1, "b": 2}

    # Function call
    del_if_possible(obj, "c")

    # Check result
    assert obj == {"a": 1, "b": 2}
