# -*- coding: utf-8 -*-
"""LAB_6.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1T_2ZTbArhonSQoh2KK9M9w6a1rYUv2X8

# Лабораторная работа №6

## Анализ и прогнозирование временного ряда.

### Задание:

1. Выберите набор данных (датасет) для решения задачи прогнозирования временного ряда.
2. Визуализируйте временной ряд и его основные характеристики.
3. Разделите временной ряд на обучающую и тестовую выборку.
4. Произведите прогнозирование временного ряда с использованием как минимум двух методов.
5. Визуализируйте тестовую выборку и каждый из прогнозов.
6. Оцените качество прогноза в каждом случае с помощью метрик.

Для работы используется набор данных, содержащий ежемесячные данные о количестве пассажиров, перевезенных одной американской авиакомпанией с 1949 по 1960 годы.
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from statsmodels.tsa.arima.model import ARIMA
from sklearn.model_selection import GridSearchCV
from gplearn.genetic import SymbolicRegressor
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# загрузка данных
df = pd.read_csv('passengers.csv')

"""### Основные характеристики датасета"""

# Выведем первые 5 строк из выбранного датасета.
df.head()

# превратим дату в индекс и сделаем изменение постоянным
df.set_index('Month', inplace = True)
df.head()

# превратим дату (наш индекс) в объект datetime
df.index = pd.to_datetime(df.index)

# посмотрим на первые пять дат и на тип данных
df.index[:5]

df.describe()

"""### Визуализация временного ряда"""

ax = df.plot(figsize = (12,6), legend = None)
ax.set(title = 'Минимальные суточные с 1949 по 1960 год', xlabel = 'Месяцы', ylabel = 'Количество пассажиров')

for i in range(1, 5):
    fig, ax = pyplot.subplots(1, 1, sharex='col', sharey='row', figsize=(5,4))
    fig.suptitle(f'Лаг порядка {i}')
    pd.plotting.lag_plot(df, lag=i, ax=ax)
    pyplot.show()

fig, ax = pyplot.subplots(1, 1, sharex='col', sharey='row', figsize=(10,5))
fig.suptitle('Автокорреляционная диаграмма')
pd.plotting.autocorrelation_plot(df, ax=ax)
pyplot.show()

"""### Автокорреляционная функция"""

plot_acf(df, lags=100)
plt.tight_layout()

"""### Частичная автокорреляционная функция"""

plot_pacf(df, lags=30, method='ywm')
plt.tight_layout()

"""### Декомпозиция временного ряда"""

decomposed = seasonal_decompose(df['#Passengers'], model = 'add')
fig = decomposed.plot()
fig.set_size_inches((10, 8))
fig.tight_layout()
plt.show()

"""### Разделение временного ряда на обучающую и тестовую выборку"""

data_2 = df.copy()

# Целочисленная метка шкалы времени
xnum = list(range(data_2.shape[0]))
# Разделение выборки на обучающую и тестовую
Y = data_2['#Passengers'].values
train_size = int(len(Y) * 0.7)
xnum_train, xnum_test = xnum[0:train_size], xnum[train_size:]
train, test = Y[0:train_size], Y[train_size:]
history_arima = [x for x in train]

"""### Прогнозирование временного ряда авторегрессионным методом (ARIMA)"""

# Параметры модели (p,d,q)
arima_order = (2,1,0)
# Формирование предсказаний
predictions_arima = list()
for t in range(len(test)):
    model_arima = ARIMA(history_arima, order=arima_order)
    model_arima_fit = model_arima.fit()
    yhat_arima = model_arima_fit.forecast()[0]
    predictions_arima.append(yhat_arima)
    history_arima.append(test[t])
# Вычисление метрики RMSE
error_arima = mean_squared_error(test, predictions_arima, squared=False)

# Ошибка прогноза
np.mean(Y), error_arima

# Записываем предсказания в DataFrame
data_2['predictions_ARIMA'] = (train_size * [np.NAN]) + list(predictions_arima)

fig, ax = pyplot.subplots(1, 1, sharex='col', sharey='row', figsize=(10,5))
fig.suptitle('Предсказания временного ряда')
data_2.plot(ax=ax, legend=True)
pyplot.show()

fig, ax = pyplot.subplots(1, 1, sharex='col', sharey='row', figsize=(10,5))
fig.suptitle('Предсказания временного ряда (тестовая выборка)')
data_2[train_size:].plot(ax=ax, legend=True)
pyplot.show()

"""### Прогнозирование временного ряда методом символьной регресии"""

function_set = ['add', 'sub', 'mul', 'div', 'sin']
SR = SymbolicRegressor(population_size=500, metric='mse',
                               generations=70, stopping_criteria=0.01,
                               init_depth=(4, 10), verbose=1, function_set=function_set,
                               const_range=(-100, 100), random_state=0)

SR.fit(np.array(xnum_train).reshape(-1, 1), train.reshape(-1, 1))

# Предсказания
y_sr = SR.predict(np.array(xnum_test).reshape(-1, 1))
y_sr[:10]

# Записываем предсказания в DataFrame
data_2['predictions_GPLEARN'] = (train_size * [np.NAN]) + list(y_sr)

fig, ax = pyplot.subplots(1, 1, sharex='col', sharey='row', figsize=(10,5))
fig.suptitle('Предсказания временного ряда (тестовая выборка)')
data_2[train_size:].plot(ax=ax, legend=True)
pyplot.show()

error_SR = mean_squared_error(test, y_sr, squared=False)

# Ошибка прогноза
np.mean(Y), error_SR

"""### Качество прогноза моделей"""

def print_metrics(y_test, y_pred):
    print(f"R^2: {r2_score(y_test, y_pred)}")
    print(f"MSE: {mean_squared_error(y_test, y_pred, squared=False)}")
    print(f"MAE: {mean_absolute_error(y_test, y_pred)}")

print("ARIMA")
print_metrics(test, predictions_arima)

print("\nGPLEARN")
print_metrics(test, y_sr)

"""#### Вывод: лучше оказалась ARIMA."""
