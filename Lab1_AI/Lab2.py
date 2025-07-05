import numpy as np
import matplotlib.pyplot as plt


# Функция для треугольной функции принадлежности
def triangular_membership(x, a, b, c):
    # Если все три параметра одинаковы, то принадлежность равна 1 только в этой точке
    if a == b == c:
        return np.where(x == a, 1, 0)

    # Инициализируем left_slope и right_slope для всех случаев
    left_slope = np.zeros_like(x)
    right_slope = np.zeros_like(x)

    # Рассчитываем левую и правую части треугольника
    if a != b:
        left_slope = np.maximum((x - a) / (b - a), 0)
    else:
        left_slope = np.where(x <= b, 1, 0)  # Если a == b, левая сторона вертикальная

    if b != c:
        right_slope = np.maximum((c - x) / (c - b), 0)
    else:
        right_slope = np.where(x >= b, 1, 0)  # Если b == c, правая сторона вертикальная

    # Вычисляем минимальное значение между левым и правым склонами
    return np.minimum(left_slope, right_slope)


# Функция для объединения двух нечетких множеств
def union_membership(x, membership_A, membership_B):
    return np.maximum(membership_A, membership_B)


# Пример данных:
# Нечеткие множества для "Успеваемость студентов" и "Время на изучение"
performance_labels = {
    'низкая': (0, 0, 50),
    'удовлетворительная': (30, 50, 70),
    'хорошая': (60, 75, 90),
    'отличная': (80, 90, 100)
}

study_time_labels = {
    'мало': (0, 0, 30),
    'умеренно': (20, 50, 80),
    'много': (70, 85, 100)
}

# Задаем четкие значения (например, оценка 65 баллов, время 40 часов)
performance_value = 88
study_time_value = 90

# Готовим диапазон значений для расчета функций принадлежности
x = np.linspace(0, 100, 100)

# Вычисляем функции принадлежности для всех множеств
performance_membership = {label: triangular_membership(x, *params) for label, params in performance_labels.items()}
study_time_membership = {label: triangular_membership(x, *params) for label, params in study_time_labels.items()}

# Вычисляем значения функций принадлежности для четких объектов
performance_membership_value = {label: triangular_membership(performance_value, *params) for label, params in
                                performance_labels.items()}
study_time_membership_value = {label: triangular_membership(study_time_value, *params) for label, params in
                               study_time_labels.items()}

# Пример объединения двух конкретных множеств: "хорошая успеваемость" и "умеренное время"
union_result = union_membership(x, performance_membership['отличная'], study_time_membership['много'])

# Визуализация
plt.plot(x, performance_membership['отличная'], label='Хорошая успеваемость')
plt.plot(x, study_time_membership['много'], label='Умеренное время')
plt.plot(x, union_result, label='Объединение')
plt.title("Объединение нечетких множеств")
plt.legend()
plt.show()

# Результат для четких значений:
print("Функция принадлежности для четкого значения успеваемости (65):", performance_membership_value)
print("Функция принадлежности для четкого значения времени на изучение (40):", study_time_membership_value)
