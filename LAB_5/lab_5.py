# -*- coding: utf-8 -*-
"""LAB_5.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1nleaVZMLGoUoOpVp7hVedjCL32V153xI

# Лабораторная работа №5

## Ансамбли моделей машинного обучения.

### Задание:

1. Выберите набор данных (датасет) для решения задачи классификации или регресии.
2. В случае необходимости проведите удаление или заполнение пропусков и кодирование категориальных признаков.
3. С использованием метода train_test_split разделите выборку на обучающую и тестовую.
4. Обучите следующие ансамблевые модели:
   * одну из моделей группы бэггинга (бэггинг или случайный лес или сверхслучайные деревья);
   * одну из моделей группы бустинга;
   * одну из моделей группы стекинга.
5. (+1 балл на экзамене) Дополнительно к указанным моделям обучите еще две модели:
   * Модель многослойного персептрона. По желанию, вместо библиотеки scikit-learn возможно использование библиотек TensorFlow, PyTorch или других аналогичных библиотек.
   * Модель МГУА с использованием библиотеки - https://github.com/kvoyager/GmdhPy (или аналогичных библиотек). Найдите такие параметры запуска модели, при которых она будет по крайней мере не хуже, чем одна из предыдущих ансамблевых моделей.
6. Оцените качество моделей с помощью одной из подходящих для задачи метрик. Сравните качество полученных моделей.
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib_inline
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
# %matplotlib inline
sns.set(style="ticks")
from io import StringIO
from IPython.display import Image
import graphviz
import pydotplus
from sklearn.metrics import mean_absolute_error

data = pd.read_csv('world_population.csv', sep=",")

# Размер набора данных
data.shape

# Типы колонок
data.dtypes

# Проверяем есть ли пропущенные значенияк
data.isnull().sum()

# Первые 5 строк датасета
data.head()

total_count = data.shape[0]
print('Всего строк: {}'.format(total_count))

"""### Кодирование категориальных признаков
Преобразуем названия стран, городов, ... в числовые зеачения (label encoding)
"""

from sklearn.preprocessing import LabelEncoder, OneHotEncoder

le = LabelEncoder()
    # "Continent"
le.fit(data.Continent.drop_duplicates())
data.Continent = le.transform(data.Continent)
    # "	Country/Territory"
le.fit(data["Country/Territory"].drop_duplicates())
data["Country/Territory"] = le.transform(data["Country/Territory"])

ig, ax = plt.subplots(figsize=(20,10))
sns.heatmap(data.corr(method='pearson'), ax=ax, annot=True, fmt='.3f')

"""### Предсказание целевого признака
Предскажем значение целевого признака "2022 Population" по "2010 Population", "2000 Population" и "1990 Population", поскольку их значения кореляции ближе всего к 1

Разбиение выборки на обучающую и тестовую
"""

X = data[["2010 Population", "2000 Population", "1990 Population"]]
Y = data["2022 Population"]
print('Входные данные:\n\n', X.head(), '\n\nВыходные данные:\n\n', Y.head())

# Разделим выборку на обучающую и тестовую
X_train,  X_test,  Y_train,  Y_test = train_test_split(X,  Y, random_state = 2022, test_size = 0.1)

# Входные параметры обучающей выборки
X_train.head()

# Входные параметры тестовой выборки
X_test.head()

# Выходные параметры обучающей выборки
Y_train.head()

# Выходные параметры тестовой выборки
Y_test.head()

from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import median_absolute_error, r2_score, precision_score

def test_model(model):
    print('precision: {}'.format(round(precision_score(Y_test, model.predict(X_test)), 2)))

"""## Обучение моделей
### Случайный лес
"""

# Визуализация дерева
def get_png_tree(tree_model_param, feature_names_param):
    dot_data = StringIO()
    export_graphviz(tree_model_param, out_file=dot_data, feature_names=feature_names_param,
                    filled=True, rounded=True, special_characters=True)
    graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
    return graph.create_png()

# Обучим регрессор на 3 деревьях
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, export_graphviz

tree1 = RandomForestRegressor(n_estimators=5, oob_score=True, random_state=2022)
tree1.fit(X, Y)

# Посмотрим важность признаков в каждом из деревьев
from operator import itemgetter

def draw_feature_importances(tree_model, X_dataset, figsize=(10,5)):
    """
    Вывод важности признаков в виде графика
    """
    # Сортировка значений важности признаков по убыванию
    list_to_sort = list(zip(X_dataset.columns.values, tree_model.feature_importances_))
    sorted_list = sorted(list_to_sort, key=itemgetter(1), reverse = True)
    # Названия признаков
    labels = [x for x,_ in sorted_list]
    # Важности признаков
    data = [x for _,x in sorted_list]
    # Вывод графика
    fig, ax = plt.subplots(figsize=figsize)
    ind = np.arange(len(labels))
    plt.bar(ind, data)
    plt.xticks(ind, labels, rotation='vertical')
    # Вывод значений
    for a,b in zip(ind, data):
        plt.text(a-0.05, b+0.01, str(round(b,3)))
    plt.show()
    return labels, data

data_rf_reg = RandomForestRegressor(random_state=2022)
data_rf_reg.fit(X, Y)
_,_ = draw_feature_importances(data_rf_reg, X)

y_pred1 = tree1.predict(X_test)

print('Средняя абсолютная ошибка:',   mean_absolute_error(Y_test, y_pred1))

"""### Бустинг"""

from sklearn.ensemble import AdaBoostRegressor

# Обучим регрессор на 3 деревьях
ab1 = AdaBoostRegressor(n_estimators=3, random_state=2022)
ab1.fit(X, Y)

# Проверим важность признаков в модели
ab2 = AdaBoostRegressor(random_state=2022)
ab2.fit(X, Y)
_,_ = draw_feature_importances(ab2, X)

y_pred2 = ab1.predict(X_test)

print('Средняя абсолютная ошибка:',   mean_absolute_error(Y_test, y_pred2))

"""### Стекинг"""

from heamy.estimator import Regressor, Classifier
from heamy.pipeline import ModelsPipeline
from heamy.dataset import Dataset

# Качество отдельных моделей
def val_mae(model):
    model.fit(X_train, Y_train)
    y_pred = model.predict(X_test)
    result = mean_absolute_error(Y_test, y_pred)
    print(model)
    print('MAE={}'.format(result))

# Проверим точность на отдельных моделях
from sklearn.linear_model import LinearRegression

for model in [
    LinearRegression(),
    DecisionTreeRegressor(),
    RandomForestRegressor(n_estimators=50)
]:
    val_mae(model)
    print('==========================')
    print()
