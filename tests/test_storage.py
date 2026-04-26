"""Basic tests for ChatStorage."""
import os
import tempfile
import pytest

from chatbot.storage import ChatStorage


@pytest.fixture
def storage():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield ChatStorage(db_path=path)
    os.remove(path)


def test_save_and_get_messages(storage):
    storage.save_message("s1", "user", "Hello", "2025-01-01T00:00:00")
    storage.save_message("s1", "assistant", "Hi there!", "2025-01-01T00:00:01")

    messages = storage.get_messages("s1")
    assert len(messages) == 2
    assert messages[0] == {"role": "user", "content": "Hello"}
    assert messages[1] == {"role": "assistant", "content": "Hi there!"}


def test_sessions_are_isolated(storage):
    storage.save_message("s1", "user", "msg in s1", "2025-01-01T00:00:00")
    storage.save_message("s2", "user", "msg in s2", "2025-01-01T00:00:01")

    assert len(storage.get_messages("s1")) == 1
    assert len(storage.get_messages("s2")) == 1
    assert storage.get_messages("s1")[0]["content"] == "msg in s1"


def test_list_sessions_returns_first_message(storage):
    storage.save_message("s1", "user", "First question", "2025-01-01T00:00:00")
    storage.save_message("s1", "assistant", "Answer", "2025-01-01T00:00:01")

    sessions = storage.list_sessions()
    assert len(sessions) == 1
    assert sessions[0][0] == "s1"
    assert sessions[0][1] == "First question"
