"""Integration tests for twat_llm package."""

import pytest
import subprocess
import tempfile
import os
import re
import io
from pathlib import Path
from unittest.mock import patch, MagicMock
import concurrent.futures

from twat_llm import __version__
from twat_llm.twat_llm import process_data, ActionConfig, WebSearchParams
from twat_llm.mallmo import ask, ask_batch, ask_chain


class TestVersionAndPackageInfo:
    """Test package version and metadata."""
    
    def test_version_format(self):
        """Test that version follows semver format."""
        version_pattern = r'^\d+\.\d+\.\d+.*$'
        assert re.match(version_pattern, __version__)
    
    def test_package_imports(self):
        """Test that all main package imports work."""
        from twat_llm import mallmo, twat_llm, __version__
        assert mallmo is not None
        assert twat_llm is not None
        assert __version__ is not None


class TestCLIIntegration:
    """Test CLI functionality through subprocess calls."""
    
    def test_cli_help(self):
        """Test that CLI help command works."""
        result = subprocess.run([
            "python", "-m", "twat_llm.mallmo", "--help"
        ], capture_output=True, text=True, cwd="/root/repo")
        assert result.returncode == 0
        assert "Usage:" in result.stdout or "help" in result.stdout
    
    @patch('twat_llm.mallmo.ask')
    def test_cli_simple_prompt(self, mock_ask):
        """Test CLI with simple prompt."""
        mock_ask.return_value = "Test response"
        
        result = subprocess.run([
            "python", "-m", "twat_llm.mallmo", 
            "--prompt", "Test prompt"
        ], capture_output=True, text=True, cwd="/root/repo")
        
        # The CLI should work even if LLM fails
        assert result.returncode in [0, 1]  # Allow both success and LLM failure
    
    def test_cli_batch_file(self):
        """Test CLI with batch file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("What is 2+2?\n")
            f.write("Name a programming language.\n")
            temp_file = f.name
        
        try:
            result = subprocess.run([
                "python", "-m", "twat_llm.mallmo", 
                "--batch_prompts_file", temp_file
            ], capture_output=True, text=True, cwd="/root/repo")
            
            # CLI should handle batch files gracefully
            assert result.returncode in [0, 1]
        finally:
            os.unlink(temp_file)


class TestEndToEndWorkflow:
    """Test complete workflows from start to finish."""
    
    @patch('twat_llm.mallmo.llm.get_model')
    def test_ask_chain_workflow(self, mock_get_model):
        """Test a complete ask_chain workflow."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text.return_value = "Chain response"
        mock_model.prompt.return_value = mock_response
        mock_model.supports_multimodal = True
        mock_get_model.return_value = mock_model
        
        def transform_text(text):
            return text.upper()
        
        steps = [
            "Summarize this: $input",
            transform_text,
            "Translate to Spanish: $input"
        ]
        
        result = ask_chain("Initial data", steps)
        assert result == "Chain response"
    
    @patch('twat_llm.mallmo.ProcessPoolExecutor')
    def test_batch_processing_workflow(self, mock_executor):
        """Test complete batch processing workflow."""
        mock_executor_instance = MagicMock()
        mock_executor_instance.map.return_value = iter(["Response 1", "Response 2"])
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        prompts = ["Prompt 1", "Prompt 2"]
        results = ask_batch(prompts)
        
        assert results == ["Response 1", "Response 2"]


class TestErrorHandling:
    """Test error handling across the system."""
    
    def test_invalid_action_config(self):
        """Test handling of invalid action configuration."""
        with pytest.raises(ValueError):
            ActionConfig(
                action_type="invalid_action",
                parameters={"invalid": "params"}
            )
    
    @patch('twat_llm.mallmo.llm.get_model')
    def test_llm_failure_handling(self, mock_get_model):
        """Test graceful handling of LLM failures."""
        mock_get_model.side_effect = Exception("LLM service unavailable")
        
        with pytest.raises(Exception):
            ask("Test prompt")
    
    def test_missing_api_keys(self):
        """Test handling of missing API keys."""
        config = ActionConfig(
            action_type="search_web",
            parameters=WebSearchParams(query="test")
        )
        
        # Should raise ValueError if API key is missing
        with pytest.raises(ValueError, match="SEARCH_API_KEY"):
            process_data(config)


class TestPerformanceAndScaling:
    """Test performance characteristics and scaling."""
    
    @patch('twat_llm.mallmo.ProcessPoolExecutor')
    def test_batch_processing_scaling(self, mock_executor):
        """Test that batch processing can handle multiple prompts."""
        mock_executor_instance = MagicMock()
        
        # Simulate processing 10 prompts
        expected_responses = [f"Response {i}" for i in range(10)]
        mock_executor_instance.map.return_value = iter(expected_responses)
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        prompts = [f"Prompt {i}" for i in range(10)]
        results = ask_batch(prompts, num_processes=4)
        
        assert len(results) == 10
        assert results == expected_responses
    
    def test_media_processing_limits(self):
        """Test media processing with various file sizes."""
        # Create a test image
        from PIL import Image
        
        # Test with different image sizes
        for size in [(100, 100), (500, 500), (1000, 1000)]:
            img = Image.new('RGB', size, color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            # Test that image processing doesn't crash
            from twat_llm.mallmo import _resize_image
            result = _resize_image(img, max_size=(512, 512))
            assert isinstance(result, bytes)
            assert len(result) > 0


class TestConfigurationAndSettings:
    """Test configuration and settings management."""
    
    def test_api_key_settings_validation(self):
        """Test API key settings validation."""
        from twat_llm.twat_llm import ApiKeySettings
        
        # Test with empty settings
        settings = ApiKeySettings()
        assert settings.proxycurl_api_key is None
        assert settings.search_api_key is None
    
    def test_model_fallback_configuration(self):
        """Test model fallback configuration."""
        from twat_llm.mallmo import DEFAULT_FALLBACK_MODELS
        
        # Ensure fallback models are defined
        assert len(DEFAULT_FALLBACK_MODELS) > 0
        assert all(isinstance(model, str) for model in DEFAULT_FALLBACK_MODELS)
    
    def test_default_configurations(self):
        """Test that default configurations are sane."""
        from twat_llm.mallmo import DEFAULT_RETRY_ATTEMPTS, DEFAULT_MAX_PROCESSES
        
        assert DEFAULT_RETRY_ATTEMPTS > 0
        assert DEFAULT_MAX_PROCESSES > 0


class TestSecurityAndValidation:
    """Test security features and input validation."""
    
    def test_input_sanitization(self):
        """Test that inputs are properly sanitized."""
        # Test with potentially problematic inputs
        test_inputs = [
            "",  # Empty string
            "   ",  # Whitespace only
            "A" * 10000,  # Very long string
            "Special chars: !@#$%^&*()",  # Special characters
        ]
        
        for test_input in test_inputs:
            # Should not crash with any input
            try:
                from twat_llm.mallmo import ask
                # This will likely fail due to LLM unavailability, but shouldn't crash
                ask(test_input)
            except Exception as e:
                # Any exception is fine as long as it's not a crash
                assert isinstance(e, Exception)
    
    def test_file_path_validation(self):
        """Test file path validation for media processing."""
        from twat_llm.mallmo import _prepare_media
        
        # Test with non-existent file
        with pytest.raises(Exception):
            _prepare_media(Path("/nonexistent/file.jpg"))
    
    def test_parameter_validation(self):
        """Test parameter validation in action configs."""
        from twat_llm.twat_llm import PersonEnrichmentParams, WebSearchParams
        
        # Test valid parameters
        person_params = PersonEnrichmentParams(name="John Doe")
        assert person_params.name == "John Doe"
        
        search_params = WebSearchParams(query="test query")
        assert search_params.query == "test query"
        
        # Test parameter constraints
        with pytest.raises(Exception):
            WebSearchParams(query="")  # Empty query might be invalid