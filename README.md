# axaxax

Python-проект для запуска и анализа agent-based model.

## Описание

Репозиторий содержит код для моделирования, проведения экспериментов и визуализации результатов.  

Основной язык проекта — Python.

## Структура проекта

```text

axaxax/

├── AgentBasedModel/      # Основная логика agent-based model

├── figures/              # Сгенерированные графики и изображения

├── tables/               # Таблицы с результатами

├── experiments.py        # Скрипт для запуска экспериментов

├── main.py               # Основной файл запуска

├── main_2d.py            # Запуск 2D-версии модели

├── plot_results.py       # Построение графиков по результатам

├── requirements.txt      # Зависимости проекта

└── .gitignore

```

## Установка

### 1. Склонируйте репозиторий

```bash

git clone https://github.com/escyd/axaxax.git

cd axaxax

```

### 2. Создайте виртуальное окружение

```bash

python -m venv venv

```

### 3. Активируйте виртуальное окружение

Для Windows:

```bash

venv\Scripts\activate

```

Для macOS/Linux:

```bash

source venv/bin/activate

```

### 4. Установите зависимости

```bash

pip install -r requirements.txt

```

### 5. Проверьте установку

```bash

python --version

pip list

```

Если зависимости установились без ошибок, проект готов к запуску.

## Запуск проекта

Для запуска основной версии:

```bash

python main.py

```

Для запуска 2D-версии:

```bash

python main_2d.py

```

Для запуска экспериментов:

```bash

python experiments.py

```

Для построения графиков:

```bash

python plot_results.py

```

## Результаты

Результаты работы проекта могут сохраняться в папках:

- `figures/` — графики и изображения;

- `tables/` — таблицы с результатами.
