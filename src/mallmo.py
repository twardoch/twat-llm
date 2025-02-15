#!/usr/bin/env python3
from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import llm
from fire import Fire
from pathos.helpers import mp
from pathos.pools import ProcessPool
from PIL import Image
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

if TYPE_CHECKING:
    from collections.abc import Iterable


class pathos_with:
    def __init__(self, pool_class=ProcessPool, nodes=None):
        self.pool_class = pool_class
        self.nodes = nodes if nodes is not None else mp.cpu_count()

    def __enter__(self):
        self.pool = self.pool_class(nodes=self.nodes)
        return self.pool

    def __exit__(self, exc_type, exc_value, traceback):
        self.pool.close()
        self.pool.join()
        self.pool.clear()
        return False  # To propagate exceptions if they occur


DEFAULT_FALLBACK_MODELS = [
    "gpt-4o-mini",  # Default OpenAI model
    "openrouter/google/gemini-flash-1.5",
    "openrouter/openai/gpt-4o-mini",
    "haiku",  # Claude 3 Haiku
]


class LLMError(Exception):
    """Base exception class for LLM errors"""


def _resize_image(image: Image.Image, max_size: tuple = (512, 512)) -> bytes:
    """Resize an image while maintaining aspect ratio"""
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="JPEG")
    return img_byte_arr.getvalue()


def _extract_middle_frame(video_path: str | Path) -> Image.Image:
    """Extract the middle frame from a video file"""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        msg = f"Unable to open video file: {video_path}"
        raise LLMError(msg)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    middle_frame_index = total_frames // 2

    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_index)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        msg = f"Unable to read frame at index {middle_frame_index} from video: {video_path}"
        raise LLMError(msg)

    return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


def _prepare_media(path: str | Path) -> bytes:
    """Process image or video file and return resized image bytes"""
    path = Path(path)
    file_ext = path.suffix.lower()

    image = (
        _extract_middle_frame(path)
        if file_ext in {".mp4", ".avi", ".mov", ".mkv"}
        else Image.open(path)
    )

    return _resize_image(image)


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def _try_model(
    prompt: str, model_id: str, attachments: list[llm.Attachment] | None = None
) -> str:
    """Try a single model with retry logic"""
    model = llm.get_model(model_id)
    response = model.prompt(prompt, attachments=attachments)
    return str(response)


def _process_step(step, current_data: str) -> str:
    """Process a single step in the chain and return the result."""
    # Convert single item to tuple if needed
    if isinstance(step, str | callable):
        step = (step,)

    # Validate step format
    if not isinstance(step, tuple) or len(step) > 2:
        msg = "Step must be a string, function, or 1-2 element tuple"
        raise TypeError(msg)

    # Unpack step elements
    processor = step[0]
    kwargs = step[1] if len(step) > 1 else {}

    if not isinstance(kwargs, dict):
        msg = "Optional second element must be a dictionary"
        raise TypeError(msg)

    # Process step based on processor type
    if callable(processor):
        # Function step
        result = processor(current_data, **kwargs)
    elif isinstance(processor, str):
        # Prompt step
        result = ask(prompt=processor, data=current_data, **kwargs)
    else:
        msg = (
            f"Step processor must be either a function or string, got {type(processor)}"
        )
        raise TypeError(msg)

    return str(result)


def ask_chain(data: str, steps: Iterable) -> str:
    """
    Process a chain of steps where each step is either a function call or a prompt.

    Args:
        initial_input (str): The initial input string to process
        steps (Iterable): Iterable of steps where each step can be:
            - A string (prompt)
            - A function
            - A tuple containing:
                - First element: Either a function or a string (prompt)
                - Second element (optional): Dictionary of parameters

    Returns:
        str: The final processed output

    Raises:
        TypeError: If input/output is not a string or if step format is invalid
    """
    current_data = str(data)

    for step in steps:
        current_data = _process_step(step, current_data)

    return current_data


def ask(
    prompt: str,
    data: str | None = None,
    model_ids: list[str] | tuple[str, ...] | None = None,
    media_paths: list[str | Path] | tuple[str | Path, ...] | None = None,
) -> str:
    """
    Send a prompt to LLM with optional media attachments and fallback models.

    Args:
        prompt: The text prompt to send
        model_ids: List of model IDs to try in order (falls back through the list)
        media_paths: Optional list of paths to image or video files to attach

    Returns:
        String response from the LLM

    Raises:
        LLMError: If all models fail
    """

    if data:
        prompt = (
            prompt.replace("$input", data)
            if "$input" in prompt
            else f"{prompt}:\n\n<input>{data}</input>"
        )
    models_to_try = model_ids if model_ids else DEFAULT_FALLBACK_MODELS

    # Process media if provided
    attachments = None
    if media_paths:
        attachments = []
        for path in media_paths:
            try:
                image_bytes = _prepare_media(path)
                attachments.append(llm.Attachment(content=image_bytes))
            except Exception as e:
                msg = f"Error processing media file {path}: {e!s}"
                raise LLMError(msg)

    # Try each model in sequence
    last_error = None
    for model_id in models_to_try:
        try:
            return _try_model(prompt, model_id, attachments)
        except Exception as e:
            last_error = e
            continue

    msg = f"All models failed. Last error: {last_error!s}"
    raise LLMError(msg)


def _process_single_prompt(args: tuple) -> str:
    """Helper function for parallel processing that unpacks arguments"""
    prompt, model_ids = args
    return ask(prompt, model_ids)


def ask_batch(
    prompts: list[str] | tuple[str, ...],
    model_ids: list[str] | tuple[str, ...] | None = None,
    num_processes: int | None = None,
) -> list[str]:
    """
    Process multiple prompts in parallel using pathos multiprocessing.

    Args:
        prompts: List of text prompts to process
        model_ids: Optional list of model IDs to try for each prompt
        num_processes: Optional number of processes to use (defaults to CPU count)

    Returns:
        List of responses corresponding to the input prompts

    Raises:
        LLMError: If parallel processing fails
    """
    if not prompts:
        return []

    # Prepare arguments for parallel processing
    args = [(prompt, model_ids) for prompt in prompts]

    try:
        with pathos_with(nodes=num_processes) as pool:
            results = pool.map(_process_single_prompt, args)
            return list(results)
    except Exception as e:
        msg = f"Batch processing failed: {e!s}"
        raise LLMError(msg)


def cli(
    prompt: str,
    model: str | None = None,
    media: list[str | Path] | tuple[str | Path, ...] | None = None,
    batch_prompts: list[str] | tuple[str, ...] | None = None,
    processes: int | None = None,
):
    """
    CLI interface for LLM interactions.

    Args:
        prompt: The text prompt to send to the LLM
        model: Optional specific model to use (falls back to defaults if not specified)
        media: Optional list of media file paths to include with the prompt
        batch_prompts: Optional list of prompts to process in parallel
        processes: Optional number of processes for batch processing
    """
    try:
        if batch_prompts:
            responses = ask_batch(
                batch_prompts,
                model_ids=[model] if model else None,
                num_processes=processes,
            )
            for _i, _response in enumerate(responses):
                pass
        else:
            ask(
                prompt,
                model_ids=[model] if model else None,
                media_paths=[Path(path) for path in media] if media else None,
            )
    except LLMError:
        sys.exit(1)


if __name__ == "__main__":
    Fire(cli)
