"""
Unit tests for CircuitBreaker class.
Tests failure tracking, state transitions, and recovery.
"""
import pytest
import time
from src.auditor import CircuitBreaker


class TestCircuitBreaker:
    def test_initial_state(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        assert not cb.is_open("ollama")
        assert not cb.is_open("gemini")

    def test_record_failure(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        cb.record_failure("ollama")
        status = cb.get_status()
        assert status["ollama"]["failures"] == 1

    def test_record_success_resets(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        cb.record_failure("ollama")
        cb.record_failure("ollama")
        cb.record_success("ollama")
        status = cb.get_status()
        assert status["ollama"]["failures"] == 0

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        for _ in range(3):
            cb.record_failure("ollama")
        assert cb.is_open("ollama")

    def test_recovery_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)
        cb.record_failure("ollama")
        assert cb.is_open("ollama")
        time.sleep(1.1)
        assert not cb.is_open("ollama")

    def test_multiple_providers_independent(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=60)
        cb.record_failure("ollama")
        cb.record_failure("ollama")
        assert cb.is_open("ollama")
        assert not cb.is_open("gemini")

    def test_get_status_format(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        cb.record_failure("ollama")
        status = cb.get_status()
        assert "ollama" in status
        assert "failures" in status["ollama"]
        assert "open" in status["ollama"]
        assert "last_failure" in status["ollama"]
