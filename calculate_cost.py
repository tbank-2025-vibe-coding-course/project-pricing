#!/usr/bin/env python3
"""
Расчет стоимости AI-приложения на 2 месяца (8 недель)
Используются модели OpenAI API согласно ценам из Pricing _OpenAI.html
"""

# Данные из приложения (приложение.xlsx)
FEATURE_DATA = {
    "ежедневный_стих": {
        "description": "Утреннее приветствие: картинка + стих",
        "input_chars": 0,  # только промпт системный
        "output_chars": 500,
        "system_prompt_chars": 5000,
        "frequency": "daily"  # 1 раз в день на пользователя
    },
    "настроение_вечером": {
        "description": "Вечерний отчет о настроении",
        "input_chars": 1000,
        "output_chars": 300,
        "system_prompt_chars": 5000,
        "frequency": "daily"
    },
    "анализ_недели": {
        "description": "Еженедельный подкаст на основе анализа настроения",
        "input_chars": 1000 * 7,
        "output_chars": 2000,
        "system_prompt_chars": 5000,
        "frequency": "weekly"
    },
    "оценка_внешности": {
        "description": "Оценка внешнего вида по фото (VLM)",
        "input_chars": 0,  # изображение
        "output_chars": 600,
        "system_prompt_chars": 5000,
        "frequency": "daily"
    },
    "регистрация": {
        "description": "Аватар + заголовок при регистрации (txt2img + LLM)",
        "input_chars": 0,
        "output_chars": 100,  # короткий заголовок
        "system_prompt_chars": 5000,
        "frequency": "once"  # только при регистрации
    }
}

# Цены из Pricing _OpenAI.html (актуальные модели)
PRICING = {
    # Текстовые модели (LLM)
    "gpt-5-mini": {
        "input": 0.250,  # $ за 1M токенов
        "output": 2.000
    },
    "gpt-5.2": {
        "input": 1.750,
        "output": 14.000
    },

    # Генерация изображений
    "gpt-image-1-mini": {
        "input": 2.00,  # текст -> изображение (промпт)
        "output": 8.00,  # само изображение
        # Примерно $0.01 за низкое качество, $0.04 за среднее, $0.17 за высокое (квадратное)
        "image_low": 0.01,
        "image_medium": 0.04,
        "image_high": 0.17
    },

    # Realtime Audio (для подкаста TTS)
    "gpt-realtime-mini-audio": {
        "input": 10.00,  # аудио вход
        "output": 20.00  # аудио выход
    },

    # Vision модели (для оценки внешности)
    "gpt-realtime-mini-image": {
        "input": 0.80,  # изображение на входе
        "output": 0  # нет выхода, только текст
    },
    "gpt-realtime-mini-text": {
        "input": 0.60,  # текстовый вход
        "output": 2.40  # текстовый выход
    }
}

# Параметры роста пользователей
INITIAL_USERS = 1000
WEEKLY_GROWTH = 100
WEEKS = 8

# Коэффициенты конверсии символов в токены
# Для русского языка: примерно 1 токен = 2-3 символа
CHARS_PER_TOKEN_RU = 2.5

# Токены для изображений (стандартное изображение)
IMAGE_TOKENS = 210  # из pricing calculator для 512x512


def chars_to_tokens(chars):
    """Конвертация символов в токены для русского текста"""
    return chars / CHARS_PER_TOKEN_RU


def calculate_weekly_users(week):
    """Количество пользователей на заданной неделе"""
    return INITIAL_USERS + WEEKLY_GROWTH * week


def calculate_costs():
    """Основной расчет стоимости"""

    total_cost = 0
    details = {}

    # 1. Ежедневный стих (картинка + стих на GPT-5 mini)
    print("\n=== 1. ЕЖЕДНЕВНЫЙ СТИХ (утреннее приветствие) ===")
    print("Модель: gpt-image-1-mini для картинки + gpt-5-mini для стиха")

    daily_poem_cost = 0
    for week in range(WEEKS):
        users = calculate_weekly_users(week)
        days = 7

        # Генерация изображения (низкое качество для экономии)
        image_cost_per_request = PRICING["gpt-image-1-mini"]["image_low"]
        images_generated = users * days
        image_cost = images_generated * image_cost_per_request

        # Генерация стиха (LLM)
        system_tokens = chars_to_tokens(FEATURE_DATA["ежедневный_стих"]["system_prompt_chars"])
        output_tokens = chars_to_tokens(FEATURE_DATA["ежедневный_стих"]["output_chars"])

        llm_cost_per_request = (
            system_tokens / 1_000_000 * PRICING["gpt-5-mini"]["input"] +
            output_tokens / 1_000_000 * PRICING["gpt-5-mini"]["output"]
        )
        llm_cost = llm_cost_per_request * images_generated

        week_cost = image_cost + llm_cost
        daily_poem_cost += week_cost

        print(f"Неделя {week+1}: {users} пользователей × 7 дней = {images_generated} запросов")
        print(f"  - Изображения: ${image_cost:.2f}")
        print(f"  - Текст (стих): ${llm_cost:.2f}")
        print(f"  - Итого за неделю: ${week_cost:.2f}")

    print(f"ИТОГО за 8 недель: ${daily_poem_cost:.2f}")
    details["ежедневный_стих"] = daily_poem_cost
    total_cost += daily_poem_cost

    # 2. Настроение по вечерам (LLM)
    print("\n=== 2. НАСТРОЕНИЕ ПО ВЕЧЕРАМ ===")
    print("Модель: gpt-5-mini (экономная модель для простых ответов)")

    evening_mood_cost = 0
    for week in range(WEEKS):
        users = calculate_weekly_users(week)
        days = 7
        requests = users * days

        system_tokens = chars_to_tokens(FEATURE_DATA["настроение_вечером"]["system_prompt_chars"])
        input_tokens = chars_to_tokens(FEATURE_DATA["настроение_вечером"]["input_chars"])
        output_tokens = chars_to_tokens(FEATURE_DATA["настроение_вечером"]["output_chars"])

        cost_per_request = (
            (system_tokens + input_tokens) / 1_000_000 * PRICING["gpt-5-mini"]["input"] +
            output_tokens / 1_000_000 * PRICING["gpt-5-mini"]["output"]
        )

        week_cost = cost_per_request * requests
        evening_mood_cost += week_cost

        print(f"Неделя {week+1}: {requests} запросов, стоимость: ${week_cost:.2f}")

    print(f"ИТОГО за 8 недель: ${evening_mood_cost:.2f}")
    details["настроение_вечером"] = evening_mood_cost
    total_cost += evening_mood_cost

    # 3. Еженедельный подкаст (анализ + TTS)
    print("\n=== 3. ЕЖЕНЕДЕЛЬНЫЙ ПОДКАСТ ===")
    print("Модель: gpt-5-mini для анализа + gpt-realtime-mini-audio для TTS")

    weekly_podcast_cost = 0
    for week in range(WEEKS):
        users = calculate_weekly_users(week)
        # 1 подкаст в неделю на пользователя

        # Анализ настроения (LLM)
        system_tokens = chars_to_tokens(FEATURE_DATA["анализ_недели"]["system_prompt_chars"])
        input_tokens = chars_to_tokens(FEATURE_DATA["анализ_недели"]["input_chars"])
        output_tokens = chars_to_tokens(FEATURE_DATA["анализ_недели"]["output_chars"])

        analysis_cost_per_request = (
            (system_tokens + input_tokens) / 1_000_000 * PRICING["gpt-5-mini"]["input"] +
            output_tokens / 1_000_000 * PRICING["gpt-5-mini"]["output"]
        )

        # TTS генерация (предполагаем, что 2000 символов текста -> аудио)
        # Используем аудио токены для TTS
        audio_output_tokens = chars_to_tokens(FEATURE_DATA["анализ_недели"]["output_chars"])
        tts_cost_per_request = (
            audio_output_tokens / 1_000_000 * PRICING["gpt-realtime-mini-audio"]["output"]
        )

        week_cost = (analysis_cost_per_request + tts_cost_per_request) * users
        weekly_podcast_cost += week_cost

        print(f"Неделя {week+1}: {users} пользователей")
        print(f"  - Анализ текста: ${analysis_cost_per_request * users:.2f}")
        print(f"  - TTS генерация: ${tts_cost_per_request * users:.2f}")
        print(f"  - Итого за неделю: ${week_cost:.2f}")

    print(f"ИТОГО за 8 недель: ${weekly_podcast_cost:.2f}")
    details["еженедельный_подкаст"] = weekly_podcast_cost
    total_cost += weekly_podcast_cost

    # 4. Оценка внешнего вида (VLM - Vision Language Model)
    print("\n=== 4. ОЦЕНКА ВНЕШНЕГО ВИДА ===")
    print("Модель: gpt-realtime-mini (image input + text output)")

    appearance_cost = 0
    for week in range(WEEKS):
        users = calculate_weekly_users(week)
        days = 7
        requests = users * days

        # Image input + system prompt
        system_tokens = chars_to_tokens(FEATURE_DATA["оценка_внешности"]["system_prompt_chars"])
        output_tokens = chars_to_tokens(FEATURE_DATA["оценка_внешности"]["output_chars"])

        cost_per_request = (
            IMAGE_TOKENS / 1_000_000 * PRICING["gpt-realtime-mini-image"]["input"] +
            system_tokens / 1_000_000 * PRICING["gpt-realtime-mini-text"]["input"] +
            output_tokens / 1_000_000 * PRICING["gpt-realtime-mini-text"]["output"]
        )

        week_cost = cost_per_request * requests
        appearance_cost += week_cost

        print(f"Неделя {week+1}: {requests} запросов, стоимость: ${week_cost:.2f}")

    print(f"ИТОГО за 8 недель: ${appearance_cost:.2f}")
    details["оценка_внешности"] = appearance_cost
    total_cost += appearance_cost

    # 5. Регистрация (аватар + заголовок)
    print("\n=== 5. РЕГИСТРАЦИЯ (аватар + заголовок) ===")
    print("Модель: gpt-image-1-mini для аватара + gpt-5-mini для заголовка")
    print("Выполняется только 1 раз при регистрации новых пользователей")

    registration_cost = 0
    # Только новые пользователи на каждой неделе
    for week in range(WEEKS):
        new_users = WEEKLY_GROWTH  # +100 пользователей каждую неделю

        # Генерация аватара
        image_cost = new_users * PRICING["gpt-image-1-mini"]["image_low"]

        # Генерация заголовка
        system_tokens = chars_to_tokens(FEATURE_DATA["регистрация"]["system_prompt_chars"])
        output_tokens = chars_to_tokens(FEATURE_DATA["регистрация"]["output_chars"])

        llm_cost_per_request = (
            system_tokens / 1_000_000 * PRICING["gpt-5-mini"]["input"] +
            output_tokens / 1_000_000 * PRICING["gpt-5-mini"]["output"]
        )
        llm_cost = llm_cost_per_request * new_users

        week_cost = image_cost + llm_cost
        registration_cost += week_cost

        print(f"Неделя {week+1}: {new_users} новых пользователей, стоимость: ${week_cost:.2f}")

    # Добавляем начальных 1000 пользователей
    initial_registration = (
        INITIAL_USERS * PRICING["gpt-image-1-mini"]["image_low"] +
        INITIAL_USERS * (
            chars_to_tokens(5000) / 1_000_000 * PRICING["gpt-5-mini"]["input"] +
            chars_to_tokens(100) / 1_000_000 * PRICING["gpt-5-mini"]["output"]
        )
    )
    registration_cost += initial_registration
    print(f"Начальные 1000 пользователей: ${initial_registration:.2f}")

    print(f"ИТОГО за 8 недель: ${registration_cost:.2f}")
    details["регистрация"] = registration_cost
    total_cost += registration_cost

    # Итоговая сводка
    print("\n" + "="*60)
    print("ИТОГОВАЯ СВОДКА")
    print("="*60)

    for feature, cost in details.items():
        percentage = (cost / total_cost) * 100
        print(f"{feature:30s}: ${cost:10.2f} ({percentage:5.1f}%)")

    print("-" * 60)
    print(f"{'ОБЩАЯ СТОИМОСТЬ':30s}: ${total_cost:10.2f}")
    print("="*60)

    # Дополнительная аналитика
    total_users_final = calculate_weekly_users(WEEKS - 1)
    total_users_registered = INITIAL_USERS + WEEKLY_GROWTH * WEEKS

    print(f"\nПользователи к концу периода: {total_users_final}")
    print(f"Всего зарегистрировано за период: {total_users_registered}")
    print(f"Средняя стоимость на пользователя: ${total_cost / total_users_registered:.2f}")

    return total_cost, details


if __name__ == "__main__":
    print("РАСЧЕТ СТОИМОСТИ AI-ПРИЛОЖЕНИЯ")
    print("Период: 8 недель (2 месяца)")
    print(f"Начальное количество пользователей: {INITIAL_USERS}")
    print(f"Прирост: +{WEEKLY_GROWTH} пользователей/неделю")
    print()

    total, details = calculate_costs()

    print("\n\nАРГУМЕНТАЦИЯ ВЫБОРА МОДЕЛЕЙ:")
    print("="*60)
    print("""
1. gpt-5-mini ($0.25/1M input, $2.00/1M output):
   - Используется для всех текстовых задач
   - В 7 раз дешевле чем gpt-5.2
   - Достаточно для генерации стихов, анализа настроения
   - Хорошее соотношение цена/качество

2. gpt-image-1-mini (low quality ~$0.01/image):
   - Генерация изображений для стихов и аватаров
   - Низкое качество ($0.01) вместо высокого ($0.17) = экономия 94%
   - Для утренних приветствий достаточно простых картинок

3. gpt-realtime-mini-audio ($10/1M input, $20/1M output):
   - TTS для еженедельных подкастов
   - Единственная доступная опция для синтеза речи

4. gpt-realtime-mini (image: $0.80/1M, text: $0.60 in/$2.40 out):
   - Vision-модель для анализа фотографий
   - Mini версия дешевле полной gpt-realtime в 4-5 раз
   - Достаточно для оценки внешности

ОСНОВНАЯ СТРАТЕГИЯ ЭКОНОМИИ:
- Везде используем mini-версии моделей
- Для изображений - минимальное качество
- Никаких premium-моделей (gpt-5.2, gpt-5.2 pro)
""")
