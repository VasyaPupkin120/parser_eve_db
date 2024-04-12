import functools
import time
from typing import Callable, Any
import uuid

def async_timed():
    """
    Измеряет время работы асинхронных функций.
    uuid используется чтобы отличать вызовы этой функции между собой, 
    т.к. у них почему то одинаковый id в pyhton.
    """
    def wrapper(func: Callable) -> Any:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            this_uuid = str(uuid.uuid4()).split("-")[-2]
            print(f"start {this_uuid}: выполняется {func} с аргументами {args} {kwargs}")
            start = time.time()
            try:
                res = await func(*args, **kwargs)
                print(res)
                return res
                # return await func(*args, **kwargs)
            finally:
                end = time.time()
                total = end - start
                print(f"end {this_uuid}: функция {func} завершилась за {total:.4f} секунд")
        return wrapped
    return wrapper

