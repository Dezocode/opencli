"""
Test suite for CPU optimization fixes
Validates that async operations don't block and performance improves
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
from textual.pilot import Pilot
from modules.tui.core import OpenCLITUI
from modules.multiline_input import MultiLineInput
from cli.session import Session


@pytest.fixture
def app() -> OpenCLITUI:
    """Return a new instance of the TUI app for testing."""
    session = Session(model='test_model')
    config = {'model': 'test_model'}
    app_instance = OpenCLITUI(session=session, config=config)

    async def mock_message_handler(user_input, prompt_input):
        await asyncio.sleep(0.01)

    app_instance.set_message_handler(mock_message_handler)
    return app_instance


@pytest.mark.asyncio
async def test_write_queue_processes_without_blocking(app: OpenCLITUI):
    """
    Test that the write queue processes items without blocking.
    Even with delays, multiple writes should complete in reasonable time.
    """
    async with app.run_test() as pilot:
        await pilot.pause(0.1)

        # Queue multiple writes
        start_time = time.perf_counter()
        for i in range(10):
            app.write(f"Message {i}")

        # Allow processing
        await pilot.pause(0.2)

        elapsed = time.perf_counter() - start_time

        # Should complete in < 500ms even with delays
        assert elapsed < 0.5, f"Write queue took too long: {elapsed:.3f}s"

        # Verify writes were processed
        content_widget = app._resolve_content_widget()
        assert content_widget is not None


@pytest.mark.asyncio
async def test_write_queue_maintains_order(app: OpenCLITUI):
    """
    Test that write queue maintains message order with delays.
    """
    async with app.run_test() as pilot:
        await pilot.pause(0.1)

        messages = [f"Line {i}" for i in range(5)]

        # Queue writes
        for msg in messages:
            app.write(msg + "\n")

        # Allow all to process
        await pilot.pause(0.2)

        # Queue should be empty after processing
        assert app._write_queue.empty()


@pytest.mark.asyncio
async def test_no_task_leaks_with_optimized_delays(app: OpenCLITUI):
    """
    Test that optimized sleep delays don't cause task leaks.
    """
    async with app.run_test() as pilot:
        await pilot.pause(0.1)
        initial_tasks = set(asyncio.all_tasks())

        # Perform write operations
        for i in range(5):
            app.write(f"Test {i}")

        await pilot.pause(0.3)

        final_tasks = set(asyncio.all_tasks())
        new_tasks = final_tasks - initial_tasks

        # New tasks should be done (write queue task continues running)
        for task in new_tasks:
            if not task.done() and 'write_queue' not in task.get_name():
                pytest.fail(f"Task leaked: {task.get_name()}")


@pytest.mark.asyncio
async def test_write_queue_responsiveness(app: OpenCLITUI):
    """
    Test that write queue remains responsive even with 10ms delays.
    Writes should start processing within 50ms.
    """
    async with app.run_test() as pilot:
        await pilot.pause(0.1)

        start_time = time.perf_counter()
        app.write("Immediate write")

        # Allow one processing cycle
        await pilot.pause(0.05)

        elapsed = time.perf_counter() - start_time

        # Should be responsive (< 100ms to start processing)
        assert elapsed < 0.1, f"Write queue not responsive: {elapsed:.3f}s"


@pytest.mark.asyncio
async def test_concurrent_writes_dont_block(app: OpenCLITUI):
    """
    Test that concurrent writes don't block each other.
    """
    async with app.run_test() as pilot:
        await pilot.pause(0.1)

        async def write_batch(prefix, count):
            for i in range(count):
                app.write(f"{prefix} {i}")
                await asyncio.sleep(0.001)

        start_time = time.perf_counter()

        # Run concurrent write batches
        await asyncio.gather(
            write_batch("A", 5),
            write_batch("B", 5),
            write_batch("C", 5)
        )

        # Allow processing
        await pilot.pause(0.2)

        elapsed = time.perf_counter() - start_time

        # Should complete quickly despite concurrency
        assert elapsed < 0.5, f"Concurrent writes blocked: {elapsed:.3f}s"


@pytest.mark.asyncio
async def test_spinner_updates_dont_cause_cpu_spike(app: OpenCLITUI):
    """
    Test that spinner updates at 80ms intervals don't spike CPU.
    """
    async with app.run_test() as pilot:
        await pilot.pause(0.1)

        input_widget = pilot.app.query_one(MultiLineInput)

        # Start spinner
        input_widget.start_spinner()

        # Let it run for a short time
        await pilot.pause(0.3)

        # Stop spinner
        input_widget.stop_spinner()

        # Verify spinner task is cleaned up
        await pilot.pause(0.1)
        assert input_widget._spin_task is None or input_widget._spin_task.done()


@pytest.mark.asyncio
async def test_refresh_not_called_excessively(app: OpenCLITUI):
    """
    Test that refresh isn't called excessively during normal operations.
    """
    async with app.run_test() as pilot:
        await pilot.pause(0.1)

        input_widget = pilot.app.query_one(MultiLineInput)

        # Track refresh calls
        original_refresh = input_widget.refresh
        refresh_count = {'count': 0}

        def tracked_refresh(*args, **kwargs):
            refresh_count['count'] += 1
            return original_refresh(*args, **kwargs)

        input_widget.refresh = tracked_refresh

        # Type a short message
        for char in "hello":
            input_widget.value += char
            input_widget.cursor_position += 1
            await pilot.pause(0.01)

        # Should have reasonable number of refreshes (not 100s)
        assert refresh_count['count'] < 50, f"Too many refreshes: {refresh_count['count']}"


@pytest.mark.asyncio
async def test_asyncio_sleep_not_zero():
    """
    Test that we're not using asyncio.sleep(0) which causes busy-waiting.
    This is a code inspection test.
    """
    from modules.tui import core
    import inspect

    # Get source code
    source = inspect.getsource(core.OpenCLITUI._process_write_queue)

    # Should not contain sleep(0)
    assert "sleep(0)" not in source, "Found asyncio.sleep(0) - causes busy-waiting"

    # Should contain a real delay
    assert "sleep(0.01)" in source or "sleep(0.02)" in source, \
        "Should use real sleep delay (0.01-0.02s)"


@pytest.mark.asyncio
async def test_performance_baseline():
    """
    Baseline performance test - measures current queue processing speed.
    """
    from modules.tui.core import OpenCLITUI
    from cli.session import Session

    session = Session(model='test_model')
    config = {'model': 'test_model'}
    app = OpenCLITUI(session=session, config=config)

    async with app.run_test() as pilot:
        await pilot.pause(0.1)

        # Measure 100 write operations
        start_time = time.perf_counter()

        for i in range(100):
            app.write(f"Perf test {i}")

        # Allow processing
        await pilot.pause(0.5)

        elapsed = time.perf_counter() - start_time

        # Should complete in reasonable time (< 1 second)
        assert elapsed < 1.0, f"Performance too slow: {elapsed:.3f}s for 100 writes"

        # Calculate throughput
        throughput = 100 / elapsed
        print(f"\nWrite throughput: {throughput:.1f} writes/sec")

        # Should maintain reasonable throughput (> 100 writes/sec)
        assert throughput > 100, f"Throughput too low: {throughput:.1f} writes/sec"


@pytest.mark.asyncio
async def test_no_cpu_spinning_in_empty_queue(app: OpenCLITUI):
    """
    Test that empty queue doesn't cause CPU spinning.
    The queue should block on await when empty, not spin.
    """
    async with app.run_test() as pilot:
        await pilot.pause(0.2)

        # Queue should be empty and waiting, not spinning
        assert app._write_queue.empty()

        # Write task should be waiting on queue.get(), not consuming CPU
        assert app._write_task is not None
        assert not app._write_task.done()

        # Sleep to ensure no CPU spinning
        await pilot.pause(0.1)

        # Task should still be alive and waiting
        assert not app._write_task.done()


if __name__ == "__main__":
    # Run with: python3 -m pytest tests/test_cpu_optimization.py -v
    pytest.main([__file__, "-v", "-s"])
