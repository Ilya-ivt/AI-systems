import psycopg2
from datetime import datetime
import random


# Подключение к БД
def connect_to_db():
    conn = psycopg2.connect(
        host="localhost",
        database="farm_management",
        user="postgres",
        password="admin",
        options="-c client_encoding=UTF8"  # Установка клиентской кодировки
    )
    return conn


# Генерация входных данных
def generate_random_inputs():
    # Случайное время
    time = random.choice(["06:30", "13:15", "20:00", "23:45"])
    # Случайный вес животного
    weight = random.uniform(50, 300)
    # Случайная температура
    temperature = random.uniform(-5, 35)
    return time, weight, temperature


# Определение временного интервала
def determine_time_period(time):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = """
    SELECT period_name FROM time_periods
    WHERE %s::time BETWEEN start_time AND end_time;
    """
    cursor.execute(query, (time,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def fuzzify_weight(weight):
    if weight <= 100:
        return {"легкий": 1, "средний": 0, "тяжёлый": 0}
    elif 100 < weight <= 200:
        return {
            "легкий": (200 - weight) / 100,
            "средний": (weight - 100) / 100,
            "тяжёлый": 0
        }
    elif weight > 200:
        return {"легкий": 0, "средний": (300 - weight) / 100, "тяжёлый": (weight - 200) / 100}


# Фаззификация данных
def fuzzify_temperature(temp):
    if temp <= 10:
        return {"холодно": 1, "нормально": 0, "жарко": 0}
    elif 10 < temp <= 25:
        return {
            "хородно": (25 - temp) / 15,
            "нормально": (temp - 10) / 15,
            "жарко": 0
        }
    elif temp > 25:
        return {"холодно": 0, "нормально": (40 - temp) / 15, "жарко": (temp - 25) / 15}


# Применение правил
def apply_rules(time_period, weight_fuzzy, temp_fuzzy):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = """
    SELECT fr.feed_amount, tp.period_name, w.weight_category, t.temperature_category, fr.priority
    FROM feeding_rules fr
    JOIN time_periods tp ON fr.time_period_id = tp.id
    JOIN weights w ON fr.weight_id = w.id
    JOIN temperatures t ON fr.temperature_id = t.id
    WHERE tp.period_name = %s;
    """
    cursor.execute(query, (time_period,))
    rules = cursor.fetchall()
    conn.close()

    applicable_rules = []
    for rule in rules:
        weight_degree = weight_fuzzy.get(rule[2], 0)
        temp_degree = temp_fuzzy.get(rule[3], 0)
        degree = min(weight_degree, temp_degree)
        # print(f"Категория веса: {rule[2]}, степень: {weight_degree}")
        # print(f"Категория температуры: {rule[3]}, степень: {temp_degree}")
        # print(f"Правило: {rule}, степень соответствия: {min(weight_degree, temp_degree)}")

        if degree > 0:
            applicable_rules.append({"feed_amount": rule[0], "degree": degree, "priority": rule[4]})

    return applicable_rules


# Разрешение крнфликтов
def resolve_conflicts(applicable_rules):
    if not applicable_rules:
        return 0  # Нет подходящих правил
    applicable_rules.sort(key=lambda x: (-x["priority"], -x["degree"]))
    best_rule = applicable_rules[0]
    return best_rule["feed_amount"]


# Заносим результат в БД
def log_results(time, weight, temp, feed_amount):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = """
    INSERT INTO feeding_logs (input_time, input_weight, input_temperature, feed_amount)
    VALUES (%s, %s, %s, %s);
    """
    cursor.execute(query, (time, weight, temp, feed_amount))
    conn.commit()
    conn.close()


# Симуляция работы
def simulate():
    time, weight, temp = generate_random_inputs()
    time_period = determine_time_period(time)
    if not time_period:
        print("Не удалось определить временной период.")
        return

    weight_fuzzy = fuzzify_weight(weight)
    temp_fuzzy = fuzzify_temperature(temp)

    applicable_rules = apply_rules(time_period, weight_fuzzy, temp_fuzzy)
    feed_amount = resolve_conflicts(applicable_rules)

    print(f"Входные данные: время={time}, вес={weight:.2f}, температура={temp:.2f}")
    print(f"Временной период: {time_period}")
    print(f"Рекомендуемое количество корма: {feed_amount} кг")
    log_results(time, weight, temp, feed_amount)


# Функция для вставки правил в таблицу feeding_rules
def insert_rules_into_db(rules):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        for rule in rules:
            query = """
            INSERT INTO feeding_rules (id, time_period_id, weight_id, temperature_id, feed_amount, priority)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (
                rule['rule_id'],
                rule['time_period'],
                rule['weight'],
                rule['temperature'],
                rule['feed_amount'],
                rule['priority']
            ))
        conn.commit()
        print("Все правила успешно добавлены в базу данных.")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при добавлении правил: {e}")
    finally:
        cursor.close()
        conn.close()


# Генерация всех правил
def generate_unique_rules():
    time_periods = [1, 2, 3]  # ID временных периодов
    weights = [1, 2, 3]  # ID категорий веса
    temperatures = [1, 2, 3]  # ID категорий температуры
    rules = []
    rule_id = 1

    # Определение фиксированных значений корма и приоритета
    feed_amount_map = {
        (1, 1): 1.0,  # Пример: light + cold → 1.0 кг
        (1, 2): 1.5,  # light + normal
        (1, 3): 2.0,  # light + hot
        (2, 1): 2.5,  # medium + cold
        (2, 2): 3.0,  # medium + normal
        (2, 3): 3.5,  # medium + hot
        (3, 1): 3.0,  # heavy + cold
        (3, 2): 4.0,  # heavy + normal
        (3, 3): 4.5,  # heavy + hot
    }

    priority_map = {
        (1, 1): 3,  # Пример: light + cold → высокий приоритет
        (1, 2): 2,  # light + normal
        (1, 3): 1,  # light + hot
        (2, 1): 3,  # medium + cold
        (2, 2): 2,  # medium + normal
        (2, 3): 1,  # medium + hot
        (3, 1): 3,  # heavy + cold
        (3, 2): 2,  # heavy + normal
        (3, 3): 1,  # heavy + hot
    }

    for time_period in time_periods:
        for weight in weights:
            for temp in temperatures:
                feed_amount = feed_amount_map[(weight, temp)]
                priority = priority_map[(weight, temp)]
                rules.append({
                    "rule_id": rule_id,
                    "time_period": time_period,
                    "weight": weight,
                    "temperature": temp,
                    "feed_amount": feed_amount,
                    "priority": priority
                })
                rule_id += 1
    return rules


for i in range(5):
    simulate()
# rules = generate_unique_rules()
# insert_rules_into_db(rules)