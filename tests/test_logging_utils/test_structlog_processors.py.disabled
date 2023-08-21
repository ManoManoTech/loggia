import logging
import os
import sys

import pytest
import structlog

from mm_logger.structlog_utils.processors import (
    EventAttributeMapper,
    ManoManoDataDogAttributesProcessor,
    RemoveKeysProcessor,
    datadog_add_log_level,
    datadog_add_logger_name,
    datadog_error_mapping_processor,
    extract_from_record_datadog,
)

structlog.configure(processors=[])


# A helper function to create a test logger
def create_test_logger():
    return logging.getLogger("test")


# Test ManoManoDataDogAttributesProcessor
def test_mm_dd_attributes_processor():
    os.environ["SERVICE"] = "test_service"
    os.environ["OWNER"] = "test_owner"
    os.environ["ENV"] = "test_env"
    os.environ["PROJECT"] = "test_project"

    processor = ManoManoDataDogAttributesProcessor()
    logger = create_test_logger()
    event_dict = processor(logger, "test", {"key": "value"})

    assert event_dict["service"] == "test_service"
    assert event_dict["owner"] == "test_owner"
    assert event_dict["env"] == "test_env"
    assert event_dict["project"] == "test_project"
    assert event_dict["key"] == "value"


@pytest.mark.parametrize(
    ("service_env", "owner_env", "env_env", "project_env"),
    [
        (None, None, None, None),
        ("DD_SERVICE", None, "DD_ENV", None),
    ],
)
def test_mm_dd_attributes_processor_partial_values(monkeypatch, service_env, owner_env, env_env, project_env):
    monkeypatch.setenv("SERVICE", "service_from_env") if service_env else monkeypatch.delenv("SERVICE", raising=False)
    monkeypatch.setenv("OWNER", "owner_from_env") if owner_env else monkeypatch.delenv("OWNER", raising=False)
    monkeypatch.setenv("ENV", "env_from_env") if env_env else monkeypatch.delenv("ENV", raising=False)
    monkeypatch.setenv("PROJECT", "project_from_env") if project_env else monkeypatch.delenv("PROJECT", raising=False)

    processor = ManoManoDataDogAttributesProcessor(service="custom_service", owner=None, env="custom_env", project=None)
    logger = create_test_logger()
    event_dict = processor(logger, "test", {"key": "value"})

    assert event_dict["service"] == "custom_service"
    assert event_dict["env"] == "custom_env"

    # Check that the missing attributes are not added to the event_dict
    assert "owner" not in event_dict
    assert "project" not in event_dict

    assert event_dict["key"] == "value"


# Test EventAttributeMapper
def test_event_attribute_mapper():
    processor = EventAttributeMapper({"key1": "new_key1", "key2": "new_key2"})
    logger = create_test_logger()
    event_dict = processor(logger, "test", {"key1": "value1", "key2": "value2", "key3": "value3"})

    assert "key1" not in event_dict
    assert "key2" not in event_dict
    assert event_dict["new_key1"] == "value1"
    assert event_dict["new_key2"] == "value2"
    assert event_dict["key3"] == "value3"


def test_event_attribute_mapper_missing_values():
    event_attribute_map = {
        "missing_key_1": "new_missing_key_1",
        "missing_key_2": "new_missing_key_2",
    }

    processor = EventAttributeMapper(event_attribute_map)
    logger = create_test_logger()
    event_dict = {"key": "value"}

    updated_event_dict = processor(logger, "test", event_dict)

    # Check that the missing keys in the event dictionary are not added
    assert "new_missing_key_1" not in updated_event_dict
    assert "new_missing_key_2" not in updated_event_dict

    # Check that the existing key is unchanged
    assert updated_event_dict["key"] == "value"


# Test datadog_add_logger_name
def test_datadog_add_logger_name_no_record():
    logger = create_test_logger()
    event_dict = datadog_add_logger_name(logger, "test", {})
    assert event_dict["logger.name"] == logger.name


def test_datadog_add_logger_name_with_record():
    logger = create_test_logger()

    record = logging.LogRecord(
        name="test_logger",
        level=logging.DEBUG,
        pathname="test_file.py",
        lineno=1,
        msg="Test message",
        args=None,
        exc_info=None,
    )

    event_dict = datadog_add_logger_name(logger, "test", {"_record": record})

    assert "logger.name" in event_dict
    assert event_dict["logger.name"] == record.name


# Test datadog_add_log_level
def test_datadog_add_log_level():
    logger = create_test_logger()
    event_dict = datadog_add_log_level(logger, "warning", {})
    assert event_dict["status"] == "warning"


def test_datadog_add_log_level_with_warn():
    logger = create_test_logger()
    method_name = "warn"

    event_dict = datadog_add_log_level(logger, method_name, {})

    assert "status" in event_dict
    assert event_dict["status"] == "warning"  # The function should replace "warn" with "warning"


# Test datadog_error_mapping_processor
def test_datadog_error_mapping_processor():
    logger = create_test_logger()
    try:
        1 / 0
    except ZeroDivisionError as e:
        exc_info = (type(e), e, e.__traceback__)
        event_dict = datadog_error_mapping_processor(logger, "test", {"exc_info": exc_info})

        assert "error.stack" in event_dict
        assert "error.message" in event_dict
        assert "error.kind" in event_dict
        assert event_dict["error.message"] == "division by zero"
        assert event_dict["error.kind"] == "builtins.ZeroDivisionError"


def test_extract_from_record_datadog_with_exc_info():
    logger = create_test_logger()

    try:
        raise ValueError("Test exception")
    except ValueError:
        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test_file.py",
        lineno=1,
        msg="Test message",
        args=None,
        exc_info=exc_info,
    )

    event_dict = extract_from_record_datadog(logger, "test", {"_record": record})

    assert "logger.thread_name" in event_dict
    assert event_dict["logger.thread_name"] == record.threadName

    assert "logger.name" in event_dict
    assert event_dict["logger.name"] == record.name

    assert "logger.method_name" in event_dict
    assert event_dict["logger.method_name"] == record.funcName

    assert "exc_info" in event_dict
    assert event_dict["exc_info"] == record.exc_info


def test_datadog_error_mapping_processor_with_exception_instance():
    try:
        raise ValueError("Test exception")
    except ValueError as e:
        event_dict = datadog_error_mapping_processor(None, None, {"exc_info": e})

    assert "error.stack" in event_dict
    assert "error.message" in event_dict
    assert event_dict["error.message"] == "Test exception"
    assert "error.kind" in event_dict
    assert event_dict["error.kind"] == "builtins.ValueError"


def test_datadog_error_mapping_processor_with_exc_info_tuple():
    try:
        raise ValueError("Test exception")
    except ValueError:
        exc_info = sys.exc_info()

    event_dict = datadog_error_mapping_processor(None, None, {"exc_info": exc_info})

    assert "error.stack" in event_dict
    assert "error.message" in event_dict
    assert event_dict["error.message"] == "Test exception"
    assert "error.kind" in event_dict
    assert event_dict["error.kind"] == "builtins.ValueError"


def test_datadog_error_mapping_processor_with_true():
    try:
        raise ValueError("Test exception")
    except ValueError:
        event_dict = datadog_error_mapping_processor(None, None, {"exc_info": True})

    assert "error.stack" in event_dict
    assert "error.message" in event_dict
    assert event_dict["error.message"] == "Test exception"
    assert "error.kind" in event_dict
    assert event_dict["error.kind"] == "builtins.ValueError"


def test_datadog_error_mapping_processor_without_exc_info():
    event_dict = datadog_error_mapping_processor(None, None, {})

    assert "error.stack" not in event_dict
    assert "error.message" not in event_dict
    assert "error.kind" not in event_dict


def test_datadog_error_mapping_processor_with_none():
    event_dict = datadog_error_mapping_processor(None, None, {"exc_info": None})

    assert "error.stack" not in event_dict
    assert "error.message" not in event_dict
    assert "error.kind" not in event_dict


# Test RemoveKeysProcessor
def test_remove_keys_processor():
    processor = RemoveKeysProcessor(["key1", "key3"])
    logger = create_test_logger()
    event_dict = processor(logger, "test", {"key1": "value1", "key2": "value2", "key3": "value3"})

    assert "key1" not in event_dict
    assert "key3" not in event_dict
    assert event_dict["key2"] == "value2"


# Test ManoManoDataDogAttributesProcessor with custom attributes
def test_mm_dd_attributes_processor_custom_attributes():
    processor = ManoManoDataDogAttributesProcessor(
        service="custom_service",
        owner="custom_owner",
        env="custom_env",
        project="custom_project",
    )
    logger = create_test_logger()
    event_dict = processor(logger, "test", {"key": "value"})

    assert event_dict["service"] == "custom_service"
    assert event_dict["owner"] == "custom_owner"
    assert event_dict["env"] == "custom_env"
    assert event_dict["project"] == "custom_project"
    assert event_dict["key"] == "value"


def test_extract_from_record_datadog():
    logger = create_test_logger()

    record = logging.LogRecord(
        name="test_logger",
        level=logging.DEBUG,
        pathname="test_file.py",
        lineno=1,
        msg="Test message",
        args=None,
        exc_info=None,
        func="test_function",
    )

    event_dict = extract_from_record_datadog(logger, "test", {"_record": record})

    assert "logger.thread_name" in event_dict
    assert "logger.name" in event_dict
    assert "logger.method_name" in event_dict

    assert event_dict["logger.thread_name"] == record.threadName
    assert event_dict["logger.name"] == record.name
    assert event_dict["logger.method_name"] == record.funcName
