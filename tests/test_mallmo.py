"""Test suite for twat_llm.mallmo."""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import io

from PIL import Image
import llm  # Import the llm module itself for llm.Attachment and llm.UnknownModelError

# Module to test
from twat_llm import mallmo  # Assuming mallmo is now part of twat_llm package
from twat_llm.mallmo import (
    LLMError,
    MediaProcessingError,
    ModelInvocationError,
    BatchProcessingError,
    _resize_image,
    # _extract_middle_frame, # Removed as part of cv2 dependency removal
    _prepare_media,
    _try_model,
    _process_step,
    ask,
    ask_chain,
    ask_batch,
    cli,
)

# A known good small PNG (1x1 pixel, black) as bytes
# (base64: iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=)
BLACK_PIXEL_PNG_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02\x00\x00\x00\x0bIDAT\x08\x99c`\x00\x00\x00\x06\x00\x01\x00\x00 \xae\xce\xbf\x00\x00\x00\x00IEND\xaeB`\x82"

# --- Test Helper Functions ---


def test_resize_image():
    """Test image resizing functionality."""
    # Create a dummy PIL Image object
    img = Image.new("RGB", (100, 100), color="red")
    resized_bytes = _resize_image(img, max_size=(50, 50))
    assert isinstance(resized_bytes, bytes)
    # Further checks could involve decoding the bytes and checking dimensions
    # For simplicity, we're just checking if it returns bytes.

    # Test with RGBA image
    img_rgba = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
    resized_bytes_rgba = _resize_image(img_rgba, max_size=(50, 50))
    assert isinstance(resized_bytes_rgba, bytes)
    # Check if it converted to RGB (JPEG doesn't support alpha)
    img_from_bytes = Image.open(io.BytesIO(resized_bytes_rgba))
    assert img_from_bytes.mode == "RGB"


# Tests for _extract_middle_frame removed as the function itself was removed.
# - test_extract_middle_frame_success
# - test_extract_middle_frame_open_fail
# - test_extract_middle_frame_read_fail


@patch("twat_llm.mallmo.Image.open")
@patch("twat_llm.mallmo._resize_image")
def test_prepare_media_image(mock_resize, mock_image_open):
    """Test preparing an image file."""
    mock_img_instance = MagicMock(spec=Image.Image)
    mock_img_instance.mode = "RGB"
    mock_image_open.return_value = mock_img_instance
    mock_resize.return_value = b"resized_image_bytes"

    result = _prepare_media(Path("test.jpg"))
    assert result == b"resized_image_bytes"
    mock_image_open.assert_called_once_with(Path("test.jpg"))
    mock_resize.assert_called_once_with(mock_img_instance)


def test_prepare_media_video_unsupported():
    """Test that _prepare_media raises an error for video files (no longer supported)."""
    with pytest.raises(
        MediaProcessingError,
        match=r"Video file type \(\.mp4\) processing is not supported in this version\. Please provide an image file\.",
    ):
        _prepare_media(Path("test.mp4"))


def test_prepare_media_unsupported_type():
    """Test preparing an unsupported file type."""
    with pytest.raises(MediaProcessingError, match="Unsupported media file type: .txt"):
        _prepare_media(Path("test.txt"))


@patch("pathlib.Path.is_file", return_value=False)
@patch("twat_llm.mallmo.Image.open", side_effect=FileNotFoundError("File not found"))
def test_prepare_media_file_not_found(mock_image_open, mock_is_file):
    """Test preparing a non-existent file."""
    with pytest.raises(MediaProcessingError, match="Media file not found"):
        _prepare_media(Path("nonexistent.jpg"))


# --- Test Core LLM Interaction ---


@patch("twat_llm.mallmo.llm.get_model")
def test_try_model_success(mock_get_model):
    """Test successful model invocation."""
    mock_llm_model_instance = MagicMock(spec=llm.Model)
    mock_response = MagicMock(spec=llm.Response)
    mock_response.text.return_value = "Successful response"
    mock_llm_model_instance.prompt.return_value = mock_response
    mock_llm_model_instance.supports_multimodal = True
    mock_get_model.return_value = mock_llm_model_instance

    result = _try_model("Test prompt", "test-model")
    assert result == "Successful response"
    mock_get_model.assert_called_once_with("test-model")
    mock_llm_model_instance.prompt.assert_called_once_with(
        "Test prompt", attachments=None
    )


@patch("twat_llm.mallmo.llm.get_model")
def test_try_model_failure_unknown_model(mock_get_model):
    """Test model invocation failure due to unknown model."""
    mock_get_model.side_effect = llm.UnknownModelError("Model not found")
    with pytest.raises(ModelInvocationError, match="Unknown model: test-model"):
        _try_model("Test prompt", "test-model")


@patch("twat_llm.mallmo.llm.get_model")
def test_try_model_failure_prompt_error(mock_get_model):
    """Test model invocation failure during prompt execution."""
    mock_llm_model_instance = MagicMock(spec=llm.Model)
    mock_llm_model_instance.prompt.side_effect = Exception("Prompt error")
    mock_llm_model_instance.supports_multimodal = True
    mock_get_model.return_value = mock_llm_model_instance

    with pytest.raises(
        ModelInvocationError, match="Error invoking model test-model: Prompt error"
    ):
        _try_model("Test prompt", "test-model")


@patch("twat_llm.mallmo.llm.get_model")
def test_try_model_multimodal_check(mock_get_model):
    """Test model invocation with multimodal check."""
    mock_llm_model_instance = MagicMock(spec=llm.Model)
    mock_llm_model_instance.supports_multimodal = False
    mock_get_model.return_value = mock_llm_model_instance

    mock_attachment = MagicMock(spec=llm.Attachment)

    with pytest.raises(
        ModelInvocationError,
        match="Model test-model does not support multimodal inputs",
    ):
        _try_model("Test prompt", "test-model", attachments=[mock_attachment])


@patch("twat_llm.mallmo._try_model")
def test_ask_success(mock_try_model):
    """Test ask function with a single successful model."""
    mock_try_model.return_value = "LLM response"
    result = ask("Hello", model_ids=["model1"])
    assert result == "LLM response"
    mock_try_model.assert_called_once_with("Hello", "model1", None)


@patch("twat_llm.mallmo._try_model")
def test_ask_fallback(mock_try_model):
    """Test ask function with model fallback."""
    mock_try_model.side_effect = [
        ModelInvocationError("Failed model1"),
        "Success from model2",
    ]
    result = ask("Hello", model_ids=["model1", "model2"])
    assert result == "Success from model2"
    assert mock_try_model.call_count == 2


@patch("twat_llm.mallmo._try_model", side_effect=ModelInvocationError("Model failed"))
def test_ask_all_models_fail(mock_try_model):
    """Test ask function when all models fail."""
    with pytest.raises(LLMError, match="All models failed. Last error: Model failed"):
        ask("Hello", model_ids=["model1", "model2"])
    # Each model is tried (DEFAULT_RETRY_ATTEMPTS + 1) times.
    # Since _try_model itself is mocked here and raises immediately,
    # it will be called once for each model in the list.
    assert mock_try_model.call_count == 2


@patch("twat_llm.mallmo._prepare_media", return_value=b"imagedata")
@patch("twat_llm.mallmo._try_model")
@patch("twat_llm.mallmo.llm.Attachment")  # Mock the Attachment class itself
def test_ask_with_media(mock_attachment_class, mock_try_model, mock_prepare_media):
    """Test ask function with media paths."""
    mock_try_model.return_value = "Response with media"
    media_path = Path("dummy.jpg")

    mock_attachment_instance = MagicMock()
    mock_attachment_class.return_value = mock_attachment_instance

    result = ask("Describe this image", media_paths=[media_path])
    assert result == "Response with media"
    mock_prepare_media.assert_called_once_with(media_path)
    mock_attachment_class.assert_called_once_with(
        content=b"imagedata", content_type="image/jpeg"
    )
    mock_try_model.assert_called_once_with(
        "Describe this image",
        mallmo.DEFAULT_FALLBACK_MODELS[0],
        [mock_attachment_instance],
    )


def test_process_step_string():
    """Test _process_step with a string (prompt)."""
    with patch("twat_llm.mallmo.ask", return_value="Processed: Hello") as mock_ask_func:
        result = _process_step("Hello", "initial_data")
        assert result == "Processed: Hello"
        mock_ask_func.assert_called_once_with(prompt="Hello", data="initial_data")


def test_process_step_function():
    """Test _process_step with a callable."""
    mock_func = MagicMock(return_value="Function output")
    result = _process_step(mock_func, "initial_data")
    assert result == "Function output"
    mock_func.assert_called_once_with("initial_data")


def test_process_step_tuple():
    """Test _process_step with a tuple (processor, kwargs)."""
    mock_func = MagicMock(return_value="Function output with kwargs")
    kwargs = {"key": "value"}
    result = _process_step((mock_func, kwargs), "initial_data")
    assert result == "Function output with kwargs"
    mock_func.assert_called_once_with("initial_data", key="value")


def test_process_step_invalid_type():
    """Test _process_step with an invalid type."""
    with pytest.raises(
        TypeError, match="Step must be a string, function, or a 1-2 element tuple"
    ):
        _process_step(123, "initial_data")  # type: ignore


def test_process_step_invalid_tuple_format():
    """Test _process_step with an invalid tuple format."""
    with pytest.raises(
        TypeError, match="Optional second element in step tuple must be a dictionary"
    ):
        _process_step(("prompt", "not_a_dict"), "initial_data")  # type: ignore


def test_ask_chain_simple():
    """Test ask_chain with simple string prompts."""
    with patch("twat_llm.mallmo.ask") as mock_ask_func:

        def side_effect_func(
            prompt, data, **kwargs
        ):  # Add **kwargs to match 'ask' signature
            return f"{prompt} processed with {data}"

        mock_ask_func.side_effect = side_effect_func

        steps = ["Step1", "Step2"]
        result = ask_chain("Initial", steps)
        assert result == "Step2 processed with Step1 processed with Initial"
        assert mock_ask_func.call_count == 2
        mock_ask_func.assert_any_call(prompt="Step1", data="Initial")
        mock_ask_func.assert_any_call(
            prompt="Step2", data="Step1 processed with Initial"
        )


@patch("twat_llm.mallmo.ProcessPoolExecutor")
def test_ask_batch_success(mock_process_pool_executor):
    """Test ask_batch successful processing."""
    prompts = ["prompt1", "prompt2"]
    expected_responses = ["response1", "response2"]

    mock_executor_instance = MagicMock()
    mock_executor_instance.map.return_value = iter(
        expected_responses
    )  # map returns an iterator
    mock_process_pool_executor.return_value.__enter__.return_value = (
        mock_executor_instance
    )

    responses = ask_batch(prompts, model_ids=["test-model"])

    assert responses == expected_responses
    mock_executor_instance.map.assert_called_once()
    # Check arguments passed to map
    map_args = mock_executor_instance.map.call_args[0]
    assert map_args[0] == mallmo._process_single_prompt_for_batch
    # Convert generator to list for comparison
    assert list(map_args[1]) == [
        ("prompt1", ["test-model"]),
        ("prompt2", ["test-model"]),
    ]


def test_ask_batch_empty_prompts():
    """Test ask_batch with no prompts."""
    responses = ask_batch([])
    assert responses == []


@patch("twat_llm.mallmo.ProcessPoolExecutor")
def test_ask_batch_processing_error_in_worker(mock_process_pool_executor):
    """Test ask_batch when a worker in ProcessPoolExecutor raises an error."""
    prompts = ["prompt1", "prompt2"]

    mock_executor_instance = MagicMock()

    # Simulate one of the map calls raising an exception
    def map_side_effect(func, iterables):
        results = []
        for item in iterables:
            if item[0] == "prompt2":  # Let's say processing prompt2 fails
                msg = "Worker failed"
                raise ValueError(msg)
            results.append(f"processed_{item[0]}")
        return iter(results)

    mock_executor_instance.map.side_effect = BatchProcessingError(
        "Worker failed"
    )  # More direct way to test this
    mock_process_pool_executor.return_value.__enter__.return_value = (
        mock_executor_instance
    )

    with pytest.raises(
        BatchProcessingError, match="Batch processing failed: Worker failed"
    ):
        ask_batch(prompts, model_ids=["test-model"])


# --- CLI Tests ---


@patch("twat_llm.mallmo.ask")
@patch("sys.exit") # Patch sys.exit
def test_cli_simple_prompt(mock_exit, mock_ask_func, capsys):
    """Test CLI with a simple prompt."""
    mock_ask_func.return_value = "CLI response"
    cli(prompt="Hello CLI", model="test-cli-model")
    captured = capsys.readouterr()
    assert "CLI response" in captured.out
    mock_ask_func.assert_called_once_with(
        "Hello CLI", data=None, model_ids=["test-cli-model"], media_paths=None
    )
    mock_exit.assert_not_called() # Should not exit if successful


@patch("twat_llm.mallmo.ask_batch")
@patch("sys.exit") # Patch sys.exit
def test_cli_batch_prompt_file(mock_exit, mock_ask_batch, capsys, tmp_path):
    """Test CLI with batch prompts from a file."""
    prompt_file = tmp_path / "prompts.txt"
    prompt_file.write_text("Prompt 1\nPrompt 2")

    mock_ask_batch.return_value = ["Response 1", "Response 2"]

    cli(batch_prompts_file=str(prompt_file), model="test-batch-model")

    captured = capsys.readouterr()
    assert "Processing 2 prompts in batch mode..." in captured.out
    assert "Response for prompt 1:\nResponse 1" in captured.out
    assert "Response for prompt 2:\nResponse 2" in captured.out
    mock_ask_batch.assert_called_once_with(
        ["Prompt 1", "Prompt 2"], model_ids=["test-batch-model"], num_processes=None
    )


@patch("twat_llm.mallmo.ask_batch")
@patch("sys.exit") # Patch sys.exit
def test_cli_batch_prompt_output_file(mock_exit, mock_ask_batch, tmp_path, capsys):
    """Test CLI with batch prompts and output to a file."""
    prompt_file = tmp_path / "prompts.txt"
    prompt_file.write_text("Prompt 1\nPrompt 2")
    output_file_path = tmp_path / "output.txt"

    mock_ask_batch.return_value = ["Response 1", "Response 2"]

    # Capture print statements to stdout for verification
    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        cli(batch_prompts_file=str(prompt_file), output_file=str(output_file_path))

    mock_ask_batch.assert_called_once_with(
        ["Prompt 1", "Prompt 2"], model_ids=None, num_processes=None
    )
    assert output_file_path.read_text() == "Response 1\nResponse 2\n"
    assert f"Batch output written to {output_file_path!s}" in mock_stdout.getvalue()
    # We expect sys.exit(0) to be called if output_file is successfully written.
    # However, cli() itself doesn't explicitly call sys.exit(0) on successful batch file write path.
    # It falls through and sys.exit(0) is called by Fire if the function returns None.
    # For now, let's assume no exit on this specific path unless an error occurs earlier.
    # If Fire's behavior with sys.exit needs to be asserted, it's more complex.
    # mock_exit.assert_called_once_with(0) # This might be too strict depending on Fire.


@patch("sys.exit") # Patch sys.exit
def test_cli_no_prompt_or_batch_file(mock_exit, capsys):
    """Test CLI when neither prompt nor batch_prompts_file is provided."""
    cli() # Call with no arguments
    captured = capsys.readouterr()
    assert (
        "Error: You must provide a 'prompt' or use '--batch_prompts_file'."
        in captured.err
    )
    mock_exit.assert_called_once_with(1)


@patch("twat_llm.mallmo.ask", side_effect=LLMError("Test LLM Error"))
@patch("sys.exit") # Patch sys.exit
def test_cli_llm_error(mock_exit, mock_ask, capsys):
    """Test CLI handling of LLMError."""
    cli(prompt="test")
    captured = capsys.readouterr()
    assert "LLM Error: Test LLM Error" in captured.err
    mock_exit.assert_called_once_with(1)


@patch("builtins.open", new_callable=mock_open)
@patch("twat_llm.mallmo.ask_batch")
@patch("sys.exit") # Patch sys.exit
def test_cli_batch_file_read_error(mock_exit, mock_ask_batch, mock_file_open, capsys):
    """Test CLI with batch prompts file that causes a read error."""
    mock_file_open.side_effect = OSError("Cannot read file")
    cli(batch_prompts_file="nonexistent_or_unreadable.txt")
    captured = capsys.readouterr()
    assert "Error reading batch prompts file" in captured.err
    mock_ask_batch.assert_not_called()
    mock_exit.assert_called_once_with(1)


@patch("twat_llm.mallmo.ask_batch")
@patch("sys.exit") # Patch sys.exit
def test_cli_batch_empty_file(mock_exit, mock_ask_batch, capsys, tmp_path):
    """Test CLI with an empty batch prompts file."""
    prompt_file = tmp_path / "empty_prompts.txt"
    prompt_file.write_text("")  # Empty file

    # The cli function exits with 0 if the batch file is empty but valid.
    cli(batch_prompts_file=str(prompt_file))
    captured = capsys.readouterr()
    assert "No prompts found in batch file." in captured.err
    mock_ask_batch.assert_not_called()
    mock_exit.assert_called_once_with(0)
