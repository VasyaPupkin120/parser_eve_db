import time

# Простая задача
def add2(x, y):
    time.sleep(3)  # Задержка 3 секунд
    return x + y

# Долгая задача (имитация)
def upper_text(data):
    time.sleep(13)  # Задержка 13 секунд
    return f"Processed: {data.upper()}"

# быстрый тест
def long_calculations(**kwargs):
    x = kwargs.get("x")
    y = kwargs.get("y")
    text = kwargs.get("text")
    if x is None:
        x = 1
    if y is None:
        y = 2
    if text is None:
        text = "test text"

    res = add2(x,y)
    text = upper_text(text)

    return {"res": res, "text": text}

