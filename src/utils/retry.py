from typing import Callable, TypeVar, ParamSpec
from tenacity import retry as tenacity_retry, stop_after_attempt, wait_exponential
from config.settings import settings

P = ParamSpec("P")
R = TypeVar("R")


def retry(
    max_attempts: int | None = None,
    multiplier: float = 1.0,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
    reraise: bool = True,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    attempts = max_attempts or settings.max_retries
    
    return tenacity_retry(
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=multiplier, min=min_wait, max=max_wait),
        reraise=reraise,
    )

