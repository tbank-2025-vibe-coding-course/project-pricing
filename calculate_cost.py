#!/usr/bin/env python3
"""
Скрипт для расчета стоимости AI-проекта на 2 месяца
"""

# Константы проекта
INITIAL_USERS = 1000
WEEKLY_GROWTH = 100
WEEKS = 8  # 2 месяца

# Расценки OpenAI (по данным на декабрь 2025)
# GPT-4o цены за 1M токенов
GPT4O_INPUT_PRICE = 2.50  # $ за 1M токенов
GPT4O_OUTPUT_PRICE = 10.00  # $ за 1M токенов

# DALL-E 3 цены
DALLE3_1024_STANDARD = 0.04  # $ за изображение 1024x1024

# TTS стандарт
TTS_STANDARD_PRICE = 15.00  # $ за 1M символов

# Vision (GPT-4o) - обработка изображений
# Для high-detail изображений: ~1100 токенов на изображение

# Коэффициент перевода символов в токены для русского языка
# Для русского: ~1 токен = 2-3 символа (берем 2.5 для точности)
CHARS_PER_TOKEN = 2.5

# Данные из Excel файла
SYSTEM_PROMPT_LENGTH = 5000  # символов для каждой функции

# Функция 1: Ежедневное приветствие (картинка + стих)
MORNING_GREETING = {
    "frequency": "daily",  # 1 раз в день на пользователя
    "image_gen": True,  # генерация картинки через DALL-E
    "text_gen": True,  # генерация стиха
    "input_chars": 0,  # нет входного текста от пользователя
    "output_chars": 500,  # длина стиха
    "image_prompt_chars": 200,  # промпт для генерации картинки
}

# Функция 2: Вечерний отчет о настроении
EVENING_MOOD = {
    "frequency": "daily",  # 1 раз в день на пользователя
    "input_chars": 1000,  # сообщение пользователя о настроении
    "output_chars": 300,  # подбадривающая фраза или факт
}

# Функция 3: Недельный подкаст
WEEKLY_PODCAST = {
    "frequency": "weekly",  # 1 раз в неделю на пользователя
    "input_chars": 1000 * 7,  # анализ настроения за неделю
    "output_chars": 2000,  # текст для озвучки
    "tts_chars": 2000,  # генерация голоса
}

# Функция 4: Оценка внешности (Vision)
APPEARANCE_EVAL = {
    "frequency": 1/3,  # 1 раз в 3 дня (в среднем)
    "image_analysis": True,  # анализ фото через Vision
    "input_chars": 0,  # изображение
    "output_chars": 600,  # рекомендации
    "vision_tokens": 1100,  # high-detail обработка изображения
}

# Функция 5: Регистрация (аватарка + звание)
REGISTRATION = {
    "frequency": "once",  # 1 раз при регистрации
    "image_gen": True,  # генерация аватарки
    "text_gen": True,  # генерация звания
    "input_chars": 0,
    "output_chars": 100,  # шуточное звание
    "image_prompt_chars": 150,  # промпт для аватарки
}


def calculate_users_per_week():
    """Рассчитывает количество пользователей на каждую неделю"""
    users_by_week = []
    for week in range(WEEKS):
        users = INITIAL_USERS + (week * WEEKLY_GROWTH)
        users_by_week.append(users)
    return users_by_week


def chars_to_tokens(chars):
    """Конвертирует символы в токены для русского языка"""
    return chars / CHARS_PER_TOKEN


def calculate_gpt4o_cost(input_chars, output_chars, system_prompt_chars=SYSTEM_PROMPT_LENGTH):
    """Рассчитывает стоимость GPT-4o запроса"""
    input_tokens = chars_to_tokens(input_chars + system_prompt_chars)
    output_tokens = chars_to_tokens(output_chars)

    input_cost = (input_tokens / 1_000_000) * GPT4O_INPUT_PRICE
    output_cost = (output_tokens / 1_000_000) * GPT4O_OUTPUT_PRICE

    return input_cost + output_cost


def calculate_dalle_cost():
    """Рассчитывает стоимость генерации изображения DALL-E 3"""
    return DALLE3_1024_STANDARD


def calculate_tts_cost(chars):
    """Рассчитывает стоимость TTS"""
    return (chars / 1_000_000) * TTS_STANDARD_PRICE


def calculate_vision_cost(vision_tokens, output_chars, system_prompt_chars=SYSTEM_PROMPT_LENGTH):
    """Рассчитывает стоимость Vision анализа"""
    # Vision использует токены для изображения + промпт
    input_tokens = vision_tokens + chars_to_tokens(system_prompt_chars)
    output_tokens = chars_to_tokens(output_chars)

    input_cost = (input_tokens / 1_000_000) * GPT4O_INPUT_PRICE
    output_cost = (output_tokens / 1_000_000) * GPT4O_OUTPUT_PRICE

    return input_cost + output_cost


def main():
    print("=" * 80)
    print("РАСЧЕТ СТОИМОСТИ AI-ПРОЕКТА НА 2 МЕСЯЦА")
    print("=" * 80)
    print()

    users_by_week = calculate_users_per_week()

    print("Исходные данные:")
    print(f"- Начальное количество пользователей: {INITIAL_USERS}")
    print(f"- Прирост пользователей в неделю: {WEEKLY_GROWTH}")
    print(f"- Период расчета: {WEEKS} недель (2 месяца)")
    print(f"- Пользователи по неделям: {users_by_week}")
    print()

    # Расчет для каждой функции
    total_cost = 0

    # 1. Утреннее приветствие (daily)
    print("-" * 80)
    print("1. УТРЕННЕЕ ПРИВЕТСТВИЕ (картинка + стих)")
    print("-" * 80)

    morning_text_cost_per_request = calculate_gpt4o_cost(
        MORNING_GREETING["input_chars"] + MORNING_GREETING["image_prompt_chars"],
        MORNING_GREETING["output_chars"]
    )
    morning_image_cost_per_request = calculate_dalle_cost()
    morning_cost_per_request = morning_text_cost_per_request + morning_image_cost_per_request

    # Рассчитываем для каждой недели
    morning_total = 0
    for week, users in enumerate(users_by_week, 1):
        week_requests = users * 7  # ежедневно
        week_cost = week_requests * morning_cost_per_request
        morning_total += week_cost
        print(f"  Неделя {week}: {users} пользователей × 7 дней = {week_requests} запросов × ${morning_cost_per_request:.6f} = ${week_cost:.2f}")

    print(f"\nСтоимость за запрос:")
    print(f"  - Генерация стиха (GPT-4o): ${morning_text_cost_per_request:.6f}")
    print(f"  - Генерация картинки (DALL-E 3): ${morning_image_cost_per_request:.6f}")
    print(f"  - ИТОГО за запрос: ${morning_cost_per_request:.6f}")
    print(f"ИТОГО за 2 месяца: ${morning_total:.2f}")
    total_cost += morning_total
    print()

    # 2. Вечерний отчет о настроении (daily)
    print("-" * 80)
    print("2. ВЕЧЕРНИЙ ОТЧЕТ О НАСТРОЕНИИ")
    print("-" * 80)

    evening_cost_per_request = calculate_gpt4o_cost(
        EVENING_MOOD["input_chars"],
        EVENING_MOOD["output_chars"]
    )

    evening_total = 0
    for week, users in enumerate(users_by_week, 1):
        week_requests = users * 7  # ежедневно
        week_cost = week_requests * evening_cost_per_request
        evening_total += week_cost
        print(f"  Неделя {week}: {users} пользователей × 7 дней = {week_requests} запросов × ${evening_cost_per_request:.6f} = ${week_cost:.2f}")

    print(f"\nСтоимость за запрос (GPT-4o): ${evening_cost_per_request:.6f}")
    print(f"ИТОГО за 2 месяца: ${evening_total:.2f}")
    total_cost += evening_total
    print()

    # 3. Недельный подкаст (weekly)
    print("-" * 80)
    print("3. НЕДЕЛЬНЫЙ ПОДКАСТ (анализ + озвучка)")
    print("-" * 80)

    podcast_text_cost_per_request = calculate_gpt4o_cost(
        WEEKLY_PODCAST["input_chars"],
        WEEKLY_PODCAST["output_chars"]
    )
    podcast_tts_cost_per_request = calculate_tts_cost(WEEKLY_PODCAST["tts_chars"])
    podcast_cost_per_request = podcast_text_cost_per_request + podcast_tts_cost_per_request

    podcast_total = 0
    for week, users in enumerate(users_by_week, 1):
        week_requests = users * 1  # еженедельно
        week_cost = week_requests * podcast_cost_per_request
        podcast_total += week_cost
        print(f"  Неделя {week}: {users} пользователей × 1 раз = {week_requests} запросов × ${podcast_cost_per_request:.6f} = ${week_cost:.2f}")

    print(f"\nСтоимость за запрос:")
    print(f"  - Анализ настроения (GPT-4o): ${podcast_text_cost_per_request:.6f}")
    print(f"  - Озвучка (TTS): ${podcast_tts_cost_per_request:.6f}")
    print(f"  - ИТОГО за запрос: ${podcast_cost_per_request:.6f}")
    print(f"ИТОГО за 2 месяца: ${podcast_total:.2f}")
    total_cost += podcast_total
    print()

    # 4. Оценка внешности (1 раз в 3 дня)
    print("-" * 80)
    print("4. ОЦЕНКА ВНЕШНОСТИ (Vision анализ фото)")
    print("-" * 80)

    appearance_cost_per_request = calculate_vision_cost(
        APPEARANCE_EVAL["vision_tokens"],
        APPEARANCE_EVAL["output_chars"]
    )

    appearance_total = 0
    for week, users in enumerate(users_by_week, 1):
        week_requests = users * (7 / 3)  # 1 раз в 3 дня ≈ 2.33 раза в неделю
        week_cost = week_requests * appearance_cost_per_request
        appearance_total += week_cost
        print(f"  Неделя {week}: {users} пользователей × {7/3:.2f} раз = {week_requests:.0f} запросов × ${appearance_cost_per_request:.6f} = ${week_cost:.2f}")

    print(f"\nСтоимость за запрос (GPT-4o Vision): ${appearance_cost_per_request:.6f}")
    print(f"ИТОГО за 2 месяца: ${appearance_total:.2f}")
    total_cost += appearance_total
    print()

    # 5. Регистрация (аватарка + звание) - только для новых пользователей
    print("-" * 80)
    print("5. РЕГИСТРАЦИЯ (аватарка + звание)")
    print("-" * 80)

    registration_text_cost = calculate_gpt4o_cost(
        REGISTRATION["input_chars"] + REGISTRATION["image_prompt_chars"],
        REGISTRATION["output_chars"]
    )
    registration_image_cost = calculate_dalle_cost()
    registration_cost_per_user = registration_text_cost + registration_image_cost

    # Новые пользователи: 1000 на старте + 100 каждую неделю
    new_users_total = INITIAL_USERS + (WEEKLY_GROWTH * WEEKS)
    registration_total = new_users_total * registration_cost_per_user

    print(f"  Изначальные пользователи: {INITIAL_USERS}")
    print(f"  Новые пользователи за {WEEKS} недель: {WEEKLY_GROWTH * WEEKS}")
    print(f"  Всего новых пользователей: {new_users_total}")
    print(f"\nСтоимость на пользователя:")
    print(f"  - Генерация звания (GPT-4o): ${registration_text_cost:.6f}")
    print(f"  - Генерация аватарки (DALL-E 3): ${registration_image_cost:.6f}")
    print(f"  - ИТОГО на пользователя: ${registration_cost_per_user:.6f}")
    print(f"ИТОГО за 2 месяца: ${registration_total:.2f}")
    total_cost += registration_total
    print()

    # Итоговая сумма
    print("=" * 80)
    print("ИТОГОВАЯ СТОИМОСТЬ")
    print("=" * 80)
    print(f"1. Утреннее приветствие:        ${morning_total:>10.2f}")
    print(f"2. Вечерний отчет о настроении: ${evening_total:>10.2f}")
    print(f"3. Недельный подкаст:           ${podcast_total:>10.2f}")
    print(f"4. Оценка внешности:            ${appearance_total:>10.2f}")
    print(f"5. Регистрация:                 ${registration_total:>10.2f}")
    print("-" * 80)
    print(f"ВСЕГО ЗА 2 МЕСЯЦА:              ${total_cost:>10.2f}")
    print("=" * 80)
    print()

    # Детальная разбивка по типам API
    print("ДЕТАЛЬНАЯ РАЗБИВКА ПО ТИПАМ API:")
    print("-" * 80)

    # GPT-4o (текст)
    gpt4o_cost = (
        morning_total - (sum(users_by_week) * 7 * morning_image_cost_per_request) +
        evening_total +
        (podcast_total - sum(users_by_week) * podcast_tts_cost_per_request) +
        appearance_total +
        (registration_total - new_users_total * registration_image_cost)
    )

    # DALL-E
    dalle_cost = (
        sum(users_by_week) * 7 * morning_image_cost_per_request +
        new_users_total * registration_image_cost
    )

    # TTS
    tts_cost = sum(users_by_week) * podcast_tts_cost_per_request

    print(f"GPT-4o (текст + Vision): ${gpt4o_cost:.2f}")
    print(f"DALL-E 3 (изображения):  ${dalle_cost:.2f}")
    print(f"TTS (озвучка):           ${tts_cost:.2f}")
    print("-" * 80)
    print(f"ИТОГО:                   ${gpt4o_cost + dalle_cost + tts_cost:.2f}")
    print("=" * 80)

    return total_cost


if __name__ == "__main__":
    total = main()
    print(f"\nФинальная стоимость проекта на 2 месяца: ${total:.2f}")
