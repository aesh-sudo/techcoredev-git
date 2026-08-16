import os
import time

# Читаем переменную окружения, чтобы понять, где мы работаем
env = os.getenv("ENV", "production")
print(f"App is running in [{env}] environment!")

# Бесконечный цикл, чтобы контейнер не падал
while True:
    time.sleep(5)
