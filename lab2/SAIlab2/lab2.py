import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Генерация данных
n = 400
x1_values = np.linspace(1, 10, n)
x2_values = np.linspace(1, 10, n)
x1, x2 = np.meshgrid(x1_values, x2_values)
y_values = 5 * np.log(x1_values) * np.log(2 * x2_values)
y = 5 * np.log(x1) * np.log(2 * x2)
# Создание DataFrame
data = pd.DataFrame({'x1': x1_values, 'x2': x2_values, 'y': y_values})

# Сохранение данных в CSV файл
data.to_csv('data.csv', index=False)

# Чтение данных из файла
data = pd.read_csv('data.csv')

# Построение графика y(x1) (x2 - константа)
plt.figure(figsize=(8, 6))
plt.plot(data['x1'], data['y'], 'bo', label='y(x1)')
plt.xlabel('x1')
plt.ylabel('y')
plt.title('y(x1)')
plt.legend()
plt.show()

# Построение графика y(x2) (x1 - константа)
plt.figure(figsize=(8, 6))
plt.plot(data['x2'], data['y'], 'ro', label='y(x2)')
plt.xlabel('x2')
plt.ylabel('y')
plt.title('y(x2)')
plt.legend()
plt.show()

# Вывод статистики
print('Средние значения:')
print(data.mean())
print('\nМинимальные значения:')
print(data.min())
print('\nМаксимальные значения:')
print(data.max())

# Сохранение строк, удовлетворяющих условию, в новый CSV файл
new_data = data[(data['x1'] < data['x1'].mean()) | (data['x2'] < data['x2'].mean())]
new_data.to_csv('filtered_data.csv', index=False)

# Построение 3D графика функции

'''
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(data['x1'], data['x2'], data['y'], c='b', marker='o')
ax.set_xlabel('x1')
ax.set_ylabel('x2')
ax.set_zlabel('y')
ax.set_title('3D график функции')
plt.show()
'''
# Создаем фигуру и оси 3D
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Построение поверхности
surf = ax.plot_surface(x1, x2, y, cmap='viridis')

# Настройка меток осей и заголовка
ax.set_xlabel('x1')
ax.set_ylabel('x2')
ax.set_zlabel('y')
ax.set_title('3D график функции')

# Добавление цветовой шкалы
fig.colorbar(surf)

plt.show()