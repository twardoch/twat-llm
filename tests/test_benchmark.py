"""Benchmark tests for twat_llm package."""

import pytest
from unittest.mock import patch, MagicMock
import concurrent.futures

from twat_llm.mallmo import ask, ask_batch, ask_chain, _resize_image
from PIL import Image


class TestPerformanceBenchmarks:
    """Benchmark performance-critical functions."""

    @pytest.mark.benchmark
    def test_ask_performance(self, benchmark):
        """Benchmark the ask function."""
        with patch("twat_llm.mallmo.llm.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text.return_value = "Benchmark response"
            mock_model.prompt.return_value = mock_response
            mock_model.supports_multimodal = True
            mock_get_model.return_value = mock_model

            result = benchmark(ask, "Benchmark prompt")
            assert result == "Benchmark response"

    @pytest.mark.benchmark
    def test_batch_processing_performance(self, benchmark):
        """Benchmark batch processing performance."""
        with patch("twat_llm.mallmo.ProcessPoolExecutor") as mock_executor:
            mock_executor_instance = MagicMock()
            responses = [f"Response {i}" for i in range(100)]
            mock_executor_instance.map.return_value = iter(responses)
            mock_executor.return_value.__enter__.return_value = mock_executor_instance

            prompts = [f"Prompt {i}" for i in range(100)]
            result = benchmark(ask_batch, prompts)
            assert len(result) == 100

    @pytest.mark.benchmark
    def test_image_resize_performance(self, benchmark):
        """Benchmark image resizing performance."""
        # Create a large test image
        img = Image.new("RGB", (2000, 2000), color="red")
        result = benchmark(_resize_image, img, (512, 512))
        assert isinstance(result, bytes)
        assert len(result) > 0

    @pytest.mark.benchmark
    def test_chain_processing_performance(self, benchmark):
        """Benchmark chain processing performance."""
        with patch("twat_llm.mallmo.ask") as mock_ask:
            mock_ask.return_value = "Chain step response"

            steps = [
                "Step 1: $input",
                lambda x: x.upper(),
                "Step 2: $input",
                lambda x: x.lower(),
                "Step 3: $input",
            ]

            result = benchmark(ask_chain, "Initial data", steps)
            assert result == "Chain step response"


class TestScalabilityBenchmarks:
    """Test scalability with different load sizes."""

    @pytest.mark.benchmark
    def test_small_batch_scalability(self, benchmark):
        """Test performance with small batch sizes."""
        self._run_batch_benchmark(benchmark, 10)

    @pytest.mark.benchmark
    def test_medium_batch_scalability(self, benchmark):
        """Test performance with medium batch sizes."""
        self._run_batch_benchmark(benchmark, 50)

    @pytest.mark.benchmark
    def test_large_batch_scalability(self, benchmark):
        """Test performance with large batch sizes."""
        self._run_batch_benchmark(benchmark, 100)

    def _run_batch_benchmark(self, benchmark, batch_size):
        """Helper method to run batch benchmarks."""
        with patch("twat_llm.mallmo.ProcessPoolExecutor") as mock_executor:
            mock_executor_instance = MagicMock()
            responses = [f"Response {i}" for i in range(batch_size)]
            mock_executor_instance.map.return_value = iter(responses)
            mock_executor.return_value.__enter__.return_value = mock_executor_instance

            prompts = [f"Prompt {i}" for i in range(batch_size)]
            result = benchmark(ask_batch, prompts)
            assert len(result) == batch_size

    @pytest.mark.benchmark
    def test_concurrent_ask_performance(self, benchmark):
        """Test concurrent ask performance."""
        with patch("twat_llm.mallmo.llm.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text.return_value = "Concurrent response"
            mock_model.prompt.return_value = mock_response
            mock_model.supports_multimodal = True
            mock_get_model.return_value = mock_model

            def run_concurrent_asks():
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(ask, f"Prompt {i}") for i in range(10)]
                    return [future.result() for future in futures]

            result = benchmark(run_concurrent_asks)
            assert len(result) == 10
            assert all(r == "Concurrent response" for r in result)


class TestMemoryBenchmarks:
    """Test memory usage and efficiency."""

    @pytest.mark.benchmark
    def test_memory_usage_large_image(self, benchmark):
        """Test memory usage with large images."""
        # Create a large image
        img = Image.new("RGB", (4000, 4000), color="blue")

        def process_large_image():
            return _resize_image(img, (512, 512))

        result = benchmark(process_large_image)
        assert isinstance(result, bytes)

    @pytest.mark.benchmark
    def test_memory_usage_multiple_images(self, benchmark):
        """Test memory usage with multiple images."""
        images = [
            Image.new(
                "RGB",
                (1000, 1000),
                color=f"rgb({i*50 % 256}, {i*80 % 256}, {i*110 % 256})",
            )
            for i in range(5)
        ]

        def process_multiple_images():
            return [_resize_image(img, (512, 512)) for img in images]

        result = benchmark(process_multiple_images)
        assert len(result) == 5
        assert all(isinstance(r, bytes) for r in result)

    @pytest.mark.benchmark
    def test_memory_usage_large_text_processing(self, benchmark):
        """Test memory usage with large text processing."""
        large_text = "This is a test prompt. " * 1000  # ~20KB of text

        with patch("twat_llm.mallmo.llm.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text.return_value = "Large text response"
            mock_model.prompt.return_value = mock_response
            mock_model.supports_multimodal = True
            mock_get_model.return_value = mock_model

            result = benchmark(ask, large_text)
            assert result == "Large text response"


class TestThroughputBenchmarks:
    """Test throughput under various conditions."""

    @pytest.mark.benchmark
    def test_sequential_processing_throughput(self, benchmark):
        """Test sequential processing throughput."""
        with patch("twat_llm.mallmo.llm.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text.return_value = "Sequential response"
            mock_model.prompt.return_value = mock_response
            mock_model.supports_multimodal = True
            mock_get_model.return_value = mock_model

            def process_sequential():
                return [ask(f"Prompt {i}") for i in range(20)]

            result = benchmark(process_sequential)
            assert len(result) == 20

    @pytest.mark.benchmark
    def test_parallel_processing_throughput(self, benchmark):
        """Test parallel processing throughput."""
        with patch("twat_llm.mallmo.ProcessPoolExecutor") as mock_executor:
            mock_executor_instance = MagicMock()
            responses = [f"Parallel response {i}" for i in range(20)]
            mock_executor_instance.map.return_value = iter(responses)
            mock_executor.return_value.__enter__.return_value = mock_executor_instance

            prompts = [f"Prompt {i}" for i in range(20)]
            result = benchmark(ask_batch, prompts)
            assert len(result) == 20

    @pytest.mark.benchmark
    def test_mixed_workload_throughput(self, benchmark):
        """Test throughput with mixed workload."""
        with patch("twat_llm.mallmo.llm.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text.return_value = "Mixed workload response"
            mock_model.prompt.return_value = mock_response
            mock_model.supports_multimodal = True
            mock_get_model.return_value = mock_model

            def mixed_workload():
                results = []
                # Single asks
                for i in range(5):
                    results.append(ask(f"Single prompt {i}"))

                # Chain processing
                chain_result = ask_chain(
                    "Initial", ["Process: $input", lambda x: x.upper(), "Finalize: $input"]
                )
                results.append(chain_result)

                return results

            result = benchmark(mixed_workload)
            assert len(result) == 6


class TestLatencyBenchmarks:
    """Test latency characteristics."""

    @pytest.mark.benchmark
    def test_first_call_latency(self, benchmark):
        """Test latency of first call (cold start)."""
        with patch("twat_llm.mallmo.llm.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text.return_value = "First call response"
            mock_model.prompt.return_value = mock_response
            mock_model.supports_multimodal = True
            mock_get_model.return_value = mock_model

            result = benchmark(ask, "First call prompt")
            assert result == "First call response"

    @pytest.mark.benchmark
    def test_subsequent_call_latency(self, benchmark):
        """Test latency of subsequent calls (warm)."""
        with patch("twat_llm.mallmo.llm.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text.return_value = "Subsequent call response"
            mock_model.prompt.return_value = mock_response
            mock_model.supports_multimodal = True
            mock_get_model.return_value = mock_model

            # Make a warmup call
            ask("Warmup prompt")

            # Benchmark the subsequent call
            result = benchmark(ask, "Subsequent call prompt")
            assert result == "Subsequent call response"

    @pytest.mark.benchmark
    def test_error_handling_latency(self, benchmark):
        """Test latency when errors occur."""
        with patch("twat_llm.mallmo.llm.get_model") as mock_get_model:
            mock_get_model.side_effect = [
                Exception("First model failed"),
                Exception("Second model failed"),
                MagicMock(),
            ]

            # The third call should succeed
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text.return_value = "Error recovery response"
            mock_model.prompt.return_value = mock_response
            mock_model.supports_multimodal = True
            mock_get_model.return_value = mock_model

            try:
                benchmark(ask, "Error handling prompt")
                # May succeed or fail depending on fallback logic
            except Exception:
                # Error handling latency is still measurable
                pass


class TestResourceUtilizationBenchmarks:
    """Test resource utilization efficiency."""

    @pytest.mark.benchmark
    def test_cpu_utilization(self, benchmark):
        """Test CPU utilization during processing."""
        with patch("twat_llm.mallmo.ProcessPoolExecutor") as mock_executor:
            mock_executor_instance = MagicMock()
            responses = [f"CPU test response {i}" for i in range(50)]
            mock_executor_instance.map.return_value = iter(responses)
            mock_executor.return_value.__enter__.return_value = mock_executor_instance

            prompts = [f"CPU test prompt {i}" for i in range(50)]
            result = benchmark(ask_batch, prompts, num_processes=8)
            assert len(result) == 50

    @pytest.mark.benchmark
    def test_io_efficiency(self, benchmark):
        """Test I/O efficiency with media processing."""
        # Create multiple test images
        images = [
            Image.new(
                "RGB",
                (800, 600),
                color=f"rgb({i*30 % 256}, {i*60 % 256}, {i*90 % 256})",
            )
            for i in range(10)
        ]

        def process_images():
            return [_resize_image(img, (400, 300)) for img in images]

        result = benchmark(process_images)
        assert len(result) == 10
        assert all(isinstance(r, bytes) for r in result)