#!/usr/bin/env python3
from __future__ import annotations

import io
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, cast

import cv2
import llm
from fire import Fire
from PIL import Image
from PIL.Image import Resampling
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


DEFAULT_RETRY_ATTEMPTS: int = 2
MAX_STEP_TUPLE_LENGTH: int = 2


DEFAULT_FALLBACK_MODELS: list[str] = [
    "gpt-4o-mini",  # Default OpenAI model
    "openrouter/google/gemini-flash-1.5",
    "openrouter/openai/gpt-4o-mini",
    "claude-3-haiku-20240307",  # Updated Claude Haiku model ID
]


class LLMError(Exception):
    """Base exception class for LLM errors."""


class MediaProcessingError(LLMError):
    """Exception for errors during media processing."""


class ModelInvocationError(LLMError):
    """Exception for errors when invoking an LLM model."""


class BatchProcessingError(LLMError):
    """Exception for errors during batch processing."""


def _resize_image(image: Image.Image, max_size: tuple[int, int] = (512, 512)) -> bytes:
    """Resize an image while maintaining aspect ratio."""
    try:
        # Ensure image is in RGB mode for JPEG saving
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.thumbnail(max_size, Resampling.LANCZOS)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG")
        return img_byte_arr.getvalue()
    except Exception as e:
        raise MediaProcessingError(f"Failed to resize image: {e!s}") from e


def _extract_middle_frame(video_path: Path) -> Image.Image:
    """Extract the middle frame from a video file."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise MediaProcessingError(f"Unable to open video file: {video_path}")

    try:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            raise MediaProcessingError(f"Video file has no frames: {video_path}")
        middle_frame_index = total_frames // 2

        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_index)
        ret, frame = cap.read()

        if not ret or frame is None:
            raise MediaProcessingError(
                f"Unable to read frame at index {middle_frame_index} from video: {video_path}"
            )
        # Convert BGR (OpenCV default) to RGB for PIL
        return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    except Exception as e:
        raise MediaProcessingError(f"Failed to extract frame from video {video_path}: {e!s}") from e
    finally:
        cap.release()


def _prepare_media(path: Path) -> bytes:
    """Process image or video file and return resized image bytes."""
    file_ext = path.suffix.lower()
    try:
        if file_ext in {".mp4", ".avi", ".mov", ".mkv"}:
            image = _extract_middle_frame(path)
        elif file_ext in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}:
            image = Image.open(path)
        else:
            raise MediaProcessingError(f"Unsupported media file type: {file_ext} for {path}")
        return _resize_image(image)
    except FileNotFoundError:
        raise MediaProcessingError(f"Media file not found: {path}")
    except MediaProcessingError: # Re-raise specific media errors
        raise
    except Exception as e:
        raise MediaProcessingError(f"Error processing media file {path}: {e!s}") from e


@retry(
    retry=retry_if_exception_type(ModelInvocationError),
    stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS + 1), # +1 because first attempt is not a "retry"
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True,
)
def _try_model(
    prompt: str, model_id: str, attachments: list[llm.Attachment] | None = None
) -> str:
    """Try a single model with retry logic."""
    try:
        model = llm.get_model(model_id)
        if not model.supports_multimodal and attachments: # Corrected attribute name
             raise ModelInvocationError(f"Model {model_id} does not support multimodal inputs, but attachments were provided.")
        response = model.prompt(prompt, attachments=attachments)
        text_response = response.text()
        if text_response is None: # Handle cases where response.text() might be None
            raise ModelInvocationError(f"Model {model_id} returned an empty response.")
        return text_response
    except llm.UnknownModelError as e:
        raise ModelInvocationError(f"Unknown model: {model_id}. {e!s}") from e
    except RetryError: # Let tenacity's RetryError propagate if all attempts fail
        raise
    except Exception as e:
        raise ModelInvocationError(f"Error invoking model {model_id}: {e!s}") from e


def _process_step(
    step: str | Callable[..., Any] | tuple[str | Callable[..., Any], dict[str, Any]],
    current_data: str,
) -> str:
    """Process a single step in the chain and return the result."""
    processor: str | Callable[..., Any]
    kwargs: dict[str, Any] = {}

    if isinstance(step, str) or callable(step):
        processor = step
    elif isinstance(step, tuple) and 1 <= len(step) <= MAX_STEP_TUPLE_LENGTH:
        processor = step[0]
        if len(step) == MAX_STEP_TUPLE_LENGTH:
            if not isinstance(step[1], dict):
                raise TypeError(
                    f"Optional second element in step tuple must be a dictionary, got {type(step[1])}"
                )
            kwargs = cast(dict[str, Any], step[1]) # Cast for type checker
    else:
        raise TypeError(
            "Step must be a string, function, or a 1-2 element tuple (processor, kwargs_dict)."
        )

    if callable(processor):
        result = processor(current_data, **kwargs)
    elif isinstance(processor, str):
        # Type checker might complain here if 'ask' is not yet fully defined or imported in a way it can resolve.
        # For now, assuming 'ask' will be available in the scope this function is used.
        result = ask(prompt=processor, data=current_data, **kwargs) # type: ignore[misc]
    else:
        raise TypeError( # Should be unreachable due to earlier checks
            f"Step processor must be either a function or string, got {type(processor)}"
        )

    return str(result)


def ask_chain(data: str, steps: Iterable[str | Callable[..., Any] | tuple[str | Callable[..., Any], dict[str, Any]]]) -> str:
    """
    Process a chain of steps where each step is either a function call or a prompt.

    Args:
        data: The initial input string to process.
        steps: Iterable of steps. Each step can be:
            - A string (prompt).
            - A function (Callable[[str, ...], Any]).
            - A tuple: (processor: str | Callable, kwargs: dict[str, Any]).

    Returns:
        The final processed output as a string.

    Raises:
        TypeError: If step format is invalid.
        LLMError: If any LLM-related error occurs during processing.
    """
    current_data = str(data)
    for step_item in steps: # Renamed to avoid conflict with outer 'step' if this were nested
        current_data = _process_step(step_item, current_data)
    return current_data


def ask(
    prompt: str,
    data: str | None = None,
    model_ids: Sequence[str] | None = None,
    media_paths: Sequence[Path | str] | None = None,
) -> str:
    """
    Send a prompt to LLM with optional media attachments and fallback models.

    Args:
        prompt: The text prompt to send.
        data: Optional input data to be incorporated into the prompt.
        model_ids: List of model IDs to try in order. Defaults to DEFAULT_FALLBACK_MODELS.
        media_paths: Optional list of paths to image or video files to attach.

    Returns:
        String response from the LLM.

    Raises:
        LLMError: If all models fail or media processing fails.
        MediaProcessingError: If there's an issue with a media file.
        ModelInvocationError: If a model fails to process the request.
    """
    if data:
        prompt = (
            prompt.replace("$input", data)
            if "$input" in prompt
            else f"{prompt}:\n\n<input>{data}</input>"
        )

    models_to_try_list = list(model_ids) if model_ids is not None else DEFAULT_FALLBACK_MODELS
    if not models_to_try_list: # Ensure there's at least one model to try
        raise ValueError("No model_ids provided and no default models configured.")


    attachments_list: list[llm.Attachment] | None = None
    if media_paths:
        attachments_list = []
        for p_item in media_paths:
            path = Path(p_item) # Ensure it's a Path object
            try:
                image_bytes = _prepare_media(path)
                # Assuming JPEG for all prepared media for simplicity, adjust if other formats are possible
                attachments_list.append(llm.Attachment(content=image_bytes, content_type="image/jpeg"))
            except MediaProcessingError:
                raise
            except Exception as e:
                raise MediaProcessingError(f"Unexpected error processing media file {path}: {e!s}") from e


    last_error: Exception | None = None
    for model_id in models_to_try_list:
        try:
            return _try_model(prompt, model_id, attachments_list)
        except ModelInvocationError as e:
            last_error = e
            # print(f"Model {model_id} failed: {e!s}", file=sys.stderr) # Optional: log attempt failure
            continue
        except Exception as e: # Should ideally not happen if _try_model handles its errors well
            last_error = e
            # print(f"Unexpected error with model {model_id}: {e!s}", file=sys.stderr) # Optional: log attempt failure
            continue

    if last_error:
        raise LLMError(f"All models failed. Last error: {last_error!s}") from last_error
    # This case should be rare if models_to_try_list was not empty initially
    raise LLMError("All models failed, but no specific error was captured (this indicates an issue with the model list or retry logic).")


def _process_single_prompt_for_batch(prompt_tuple: tuple[str, Sequence[str] | None]) -> str:
    """
    Helper function for parallel processing, takes a tuple of (prompt, model_ids).
    Media paths are not supported in this batch version for simplicity.
    """
    prompt, model_ids = prompt_tuple
    return ask(prompt=prompt, model_ids=model_ids, media_paths=None)


def ask_batch(
    prompts: Sequence[str],
    model_ids: Sequence[str] | None = None,
    num_processes: int | None = None,
) -> list[str]:
    """
    Process multiple prompts in parallel using concurrent.futures.ProcessPoolExecutor.
    Note: This batch version does not support media attachments per prompt.

    Args:
        prompts: List of text prompts to process.
        model_ids: Optional list of model IDs to try for each prompt.
        num_processes: Optional number of processes to use (defaults to CPU count).

    Returns:
        List of responses corresponding to the input prompts.

    Raises:
        BatchProcessingError: If parallel processing fails or any prompt processing fails.
    """
    if not prompts:
        return []

    actual_num_processes = num_processes if num_processes is not None else os.cpu_count()
    if actual_num_processes is None: # os.cpu_count() can return None
        actual_num_processes = 1 # Default to 1 if cpu_count is not available

    # Prepare arguments for map: list of (prompt, model_ids) tuples
    args_for_map = [(prompt, model_ids) for prompt in prompts]

    results: list[str]
    try:
        with ProcessPoolExecutor(max_workers=actual_num_processes) as executor:
            # executor.map processes items in order and collects results
            # It will raise the first exception encountered in a worker.
            results = list(executor.map(_process_single_prompt_for_batch, args_for_map))
        return results
    except Exception as e:
        raise BatchProcessingError(f"Batch processing failed: {e!s}") from e


def cli(
    prompt: str | None = None,
    model: str | None = None,
    media: list[str] | None = None,
    batch_prompts_file: str | None = None,
    output_file: str | None = None,
    processes: int | None = None,
) -> None:
    """
    CLI interface for LLM interactions.

    Args:
        prompt: The text prompt to send to the LLM.
        model: Optional specific model ID to use.
        media: Optional list of media file paths.
        batch_prompts_file: Path to a file with prompts (one per line) for batch processing.
        output_file: Path to save batch output (one response per line).
        processes: Number of processes for batch processing.
    """
    model_ids_list: Sequence[str] | None = [model] if model else None
    media_paths_list: Sequence[Path] | None = [Path(p) for p in media] if media else None

    try:
        if batch_prompts_file:
            try:
                with open(batch_prompts_file, "r", encoding="utf-8") as f:
                    prompts_for_batch = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print(f"Error: Batch prompts file not found: {batch_prompts_file}", file=sys.stderr)
                sys.exit(1)
            except Exception as e: # pylint: disable=broad-except
                print(f"Error reading batch prompts file {batch_prompts_file}: {e!s}", file=sys.stderr)
                sys.exit(1)

            if not prompts_for_batch:
                print("No prompts found in batch file.", file=sys.stderr)
                sys.exit(0)

            print(f"Processing {len(prompts_for_batch)} prompts in batch mode...")
            responses = ask_batch(
                prompts_for_batch,
                model_ids=model_ids_list,
                num_processes=processes,
            )
            if output_file:
                try:
                    with open(output_file, "w", encoding="utf-8") as f:
                        for response_text in responses:
                            f.write(response_text + "\n")
                    print(f"Batch output written to {output_file}")
                except Exception as e: # pylint: disable=broad-except
                    print(f"Error writing batch output to {output_file}: {e!s}", file=sys.stderr)
                    sys.exit(1)
            else:
                for i, response_text in enumerate(responses):
                    print(f"Response for prompt {i+1}:\n{response_text}\n---")

        elif prompt:
            response_text = ask(
                prompt,
                model_ids=model_ids_list,
                media_paths=media_paths_list,
            )
            print(response_text)
        else:
            print("Error: You must provide a 'prompt' or use '--batch_prompts_file'.", file=sys.stderr)
            sys.exit(1)

    except LLMError as e:
        print(f"LLM Error: {e!s}", file=sys.stderr)
        sys.exit(1)
    except Exception as e: # pylint: disable=broad-except
        print(f"An unexpected error occurred: {e!s}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    Fire(cli)
