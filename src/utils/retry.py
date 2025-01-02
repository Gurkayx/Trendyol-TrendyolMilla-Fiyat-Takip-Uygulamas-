import asyncio
from functools import wraps
from typing import TypeVar, Callable, Any
import logging

T = TypeVar('T')

def async_retry(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Asenkron fonksiyonlar için yeniden deneme dekoratörü
    
    Args:
        retries: Maksimum deneme sayısı
        delay: İlk bekleme süresi (saniye)
        backoff: Her denemede bekleme süresinin çarpanı
        exceptions: Yakalanacak hata tipleri
        
    Returns:
        Callable: Dekoratör fonksiyon
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            current_delay = delay
            
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < retries - 1:
                        logging.warning(
                            f"{func.__name__} başarısız oldu, {retries-attempt-1} "
                            f"deneme kaldı. Hata: {str(e)}"
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logging.error(
                            f"{func.__name__} {retries} denemeden sonra başarısız oldu. "
                            f"Son hata: {str(e)}"
                        )
            
            raise last_exception
            
        return wrapper
    return decorator 