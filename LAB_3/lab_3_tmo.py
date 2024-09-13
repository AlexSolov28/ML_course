# -*- coding: utf-8 -*-
"""Lab_3_TMO.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ACIHeB_05R1woLSVpTkU-l8tWisawYg4

# Лабораторная работа №3

## Подготовка обучающей и тестовой выборки, кросс-валидация и подбор гиперпараметров на примере метода ближайших соседей.

### Задание:

1. Выберите набор данных (датасет) для решения задачи классификации или регрессии.
2. С использованием метода train_test_split разделите выборку на обучающую и тестовую.
3. Обучите модель ближайших соседей для произвольно заданного гиперпараметра K. Оцените качество модели с помощью подходящих для задачи метрик.
4. Произведите подбор гиперпараметра K с использованием GridSearchCV и/или RandomizedSearchCV и кросс-валидации, оцените качество оптимальной модели. Желательно использование нескольких стратегий кросс-валидации.
5. Сравните метрики качества исходной и оптимальной моделей.
"""

# Commented out IPython magic to ensure Python compatibility.
import sys
sys.path
import pandas as pd
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
import seaborn as sns
import matplotlib.pyplot as plt
# %matplotlib inline
import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

df = pd.read_csv('world_population.csv')

"""### Основные характеристики датасета"""

# Выведем первые 5 строк из выбранного датасета.
df.head()

total_count = df.shape[0]
print('Всего строк: {}'.format(total_count))
total_count = df.shape[1]
print('Всего колонок: {}'.format(total_count))

# Выведем список колонок с типами данных.
df.dtypes

"""### Проверка на пустые значения в датасете"""

for col_empty in df.columns:
    empty_count = df[df[col_empty].isnull()].shape[0]
    print('{} - {}'.format(col_empty, empty_count))

# Проверка на пропущенные данные
df.isnull().sum()

"""### Диаграмма рассеяния"""

plt.scatter(df['2022 Population'],df['2020 Population'])

plt.scatter(df['2022 Population'],df['2015 Population'])

X = df[['2020 Population', '2015 Population']]
Y = df['2022 Population']

# Выведем по оси абсцисс.
X

# Выведем по оси ординат.
Y

"""### Разделение выборки на обучающую и тестовую"""

from sklearn.model_selection import train_test_split

X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=0.2)

# Вернет 80% от общего размера данных
len(X_train)

len(X_test)

X_train

X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=0.2, random_state=10)

X_train

# Используем нашу модель линейной регресии
from sklearn.linear_model import LinearRegression
clf = LinearRegression()

# Обучим нашу модель
clf.fit(X_train,Y_train)

clf.predict(X_test)

Y_test

# Означает, что точность составляет 99%
clf.score(X_test,Y_test)

from sklearn.preprocessing import MinMaxScaler, StandardScaler

scaler = MinMaxScaler().fit(X_train)
X_train = pd.DataFrame(scaler.transform(X_train), columns=X_train.columns)
X_test = pd.DataFrame(scaler.transform(X_test), columns=X_train.columns)
X_train.describe()

"""### Обучение KNN с произвольным k"""

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neighbors import KNeighborsRegressor

def print_metrics(Y_test, Y_pred):
    print(f"R^2: {r2_score(Y_test, Y_pred)}")
    print(f"MSE: {mean_squared_error(Y_test, Y_pred)}")
    print(f"MAE: {mean_absolute_error(Y_test, Y_pred)}")

def print_cv_result(cv_model, X_test, Y_test):
    print(f'Оптимизация метрики {cv_model.scoring}: {cv_model.best_score_}')
    print(f'Лучший параметр: {cv_model.best_params_}')
    print('Метрики на тестовом наборе')
    print_metrics(Y_test, cv_model.predict(X_test))
    print()

base_k = 7
base_knn = KNeighborsRegressor(n_neighbors=base_k)
base_knn.fit(X_train, Y_train)
Y_pred_base = base_knn.predict(X_test)
print(f'Test metrics for KNN with k={base_k}\n')
print_metrics(Y_test, Y_pred_base)

"""### Кросс-валидация"""

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

metrics = ['r2', 'neg_mean_squared_error', 'neg_mean_absolute_error']
cv_values = [5, 10]

for cv in cv_values:
    print(f'Результаты кросс-валидации при cv={cv}\n')
    for metric in metrics:
        params = {'n_neighbors': range(1, 30)}
        knn_cv = GridSearchCV(KNeighborsRegressor(), params, cv=cv, scoring=metric, n_jobs=-1)
        knn_cv.fit(X_train, Y_train)
        print_cv_result(knn_cv, X_test, Y_test)

best_k = 4
Y_pred_best = KNeighborsRegressor(n_neighbors=best_k).fit(X_train, Y_train).predict(X_test)

"""### Сравнение исходной и оптимальной модели"""

print('Basic model\n')
print_metrics(Y_test, Y_pred_base)
print('_______________________')
print('\nOptimal model\n')
print_metrics(Y_test, Y_pred_best)

"""### Визуализация оптимальной модели"""

res = pd.DataFrame({'Y_test': Y_test, 'Y_pred_best': Y_pred_best}).sort_values(by='Y_test')
res.head()
