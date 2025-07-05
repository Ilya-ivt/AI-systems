import random
import numpy as np
from deap import base, creator, tools, algorithms
import itertools
import matplotlib.pyplot as plt

# Инициализация данных (пример)
N = 5  # количество полей
k = 3  # количество культур

yield_matrix = np.array([
    [4, 2, 3],
    [5, 3, 4],
    [3, 4, 2],
    [2, 3, 5],
    [4, 5, 3]
])

costs = np.array([3, 2, 4])

#yield_matrix = np.random.randint(1, 11, size=(N, k))
#costs = np.random.randint(1, 6, size=k)
# Создание классов для приспособленности и особей
creator.create("FitnessMax", base.Fitness, weights=(1.0,))  # Максимизация
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Генерация случайного индивидуума (решение)
toolbox.register("attr_int", random.randint, 0, k-1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, N)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Фитнес-функция для расчёта разницы между урожайностью и затратами
def fitness(individual):
    total_yield = sum(yield_matrix[i, individual[i]] for i in range(N))
    total_cost = sum(costs[individual[i]] for i in range(N))
    return total_yield - total_cost,

toolbox.register("evaluate", fitness)


# Одноточечное скрещивание (One-point crossover)
def one_point_crossover(ind1, ind2):
    point = random.randint(1, len(ind1) - 1)
    ind1[point:], ind2[point:] = ind2[point:], ind1[point:]
    return ind1, ind2

# Однородное скрещивание (Uniform crossover)
def uniform_crossover(ind1, ind2, prob=0.5):
    for i in range(len(ind1)):
        if random.random() < prob:
            ind1[i], ind2[i] = ind2[i], ind1[i]
    return ind1, ind2

# Регистрируем новые операторы скрещивания в toolbox
toolbox.register("mate_one_point", one_point_crossover)
toolbox.register("mate_uniform", uniform_crossover)

# Инверсия (Inversion mutation)
def inversion_mutation(individual):
    start, end = sorted([random.randint(0, len(individual) - 1) for _ in range(2)])
    individual[start:end+1] = reversed(individual[start:end+1])
    return individual,

# Замена случайного гена (Random replacement mutation)
def random_replacement_mutation(individual):
    index = random.randint(0, len(individual) - 1)
    individual[index] = random.randint(0, k-1)
    return individual,

# Регистрируем новые операторы мутации в toolbox
toolbox.register("mutate_inversion", inversion_mutation)
toolbox.register("mutate_random", random_replacement_mutation)




# Операторы скрещивания, мутации и отбора
toolbox.register("mate", tools.cxTwoPoint)  # Скрещивание
toolbox.register("mutate", tools.mutUniformInt, low=0, up=k-1, indpb=0.2)  # Мутация
toolbox.register("select", tools.selTournament, tournsize=3)  # Турнирный отбор

# Основной цикл генетического алгоритма
def genetic_algorithm(pop_size=10, generations=50, cxpb=0.8, mutpb=0.2, cross_type='one_point', mutate_type='inversion'):
    population = toolbox.population(n=pop_size)

    # Определяем операторы скрещивания и мутации в зависимости от переданных параметров
    if cross_type == 'two_point':
        toolbox.register("mate", tools.cxTwoPoint)
    elif cross_type == 'one_point':
        toolbox.register("mate", toolbox.mate_one_point)
    elif cross_type == 'uniform':
        toolbox.register("mate", toolbox.mate_uniform)

    if mutate_type == 'uniform':
        toolbox.register("mutate", tools.mutUniformInt, low=0, up=k-1, indpb=0.2)
    elif mutate_type == 'inversion':
        toolbox.register("mutate", toolbox.mutate_inversion)
    elif mutate_type == 'random_replacement':
        toolbox.register("mutate", toolbox.mutate_random)

    # Статистика для анализа
    stats = tools.Statistics(key=lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("max", np.max)
    stats.register("vals", np.array)

    population, logbook = algorithms.eaSimple(population, toolbox, cxpb=cxpb, mutpb=mutpb,
                                              ngen=generations, stats=stats, verbose=False)

    best_individual = tools.selBest(population, k=1)[0]
    return best_individual, best_individual.fitness.values[0], logbook

# Запуск генетического алгоритма с разными типами скрещивания и мутации
best_solution, best_fitness, logbook = genetic_algorithm(cross_type='one_point', mutate_type='inversion')


# Запуск генетического алгоритма
best_solution, best_fitness, logbook = genetic_algorithm()

# Вывод лучшего решения
print("Лучшее решение (генетический алгоритм):", best_solution)
print("Фитнес (генетический алгоритм):", best_fitness)

# Упрощённый вывод логов по поколениям
print("\nЛог по поколениям:")
for gen in logbook:
    print(f"Поколение {gen['gen']}: Макс: {gen['max']}, Средн.: {gen['avg']}")

# Функция для полного перебора
def brute_force():
    # Перебираем все возможные комбинации культур для каждого поля
    best_solution = None
    best_fitness = 0  # Начальное значение для максимизации

    # Генерация всех возможных комбинаций культур для N полей (k культур для каждого поля)
    for solution in itertools.product(range(k), repeat=N):
        # Вычисляем фитнес для текущего решения
        total_yield = sum(yield_matrix[i, solution[i]] for i in range(N))
        total_cost = sum(costs[solution[i]] for i in range(N))
        fitness_value = total_yield - total_cost
        #fitness_value = fitness(solution)

        # Обновляем лучшее решение, если текущее лучше
        if fitness_value > best_fitness:
            best_fitness = fitness_value
            best_solution = solution

    return best_solution, best_fitness



maxFitnessValues, meanFitnessValues, vals = logbook.select("max", "avg", "vals")

plt.plot(maxFitnessValues, color= 'red')
plt.plot(meanFitnessValues, color= 'green')
plt.xlabel('Поколение')
plt.ylabel('Макс/Сред приспособленность')
plt.title('Зависимость максимальной и средней приспособленности от поколений')
plt.show()
