# Проект CashMonitor

## Описание

Проект CashMonitor - приложение на Python для анализа транзакций,
которые находятся в Excel-файле. Приложение генерирует JSON-данные для веб-страниц,
формирует Excel-отчеты, а также предоставлять другие сервисы.

# Установка

1. Клонируйте репозиторий:
```commandline
git clone https://github.com/aleks-stellar/CashMonitor
```
2. Установите зависимости:
```commandline
poetry install
```

## использование

1. Запустите модуль main в корневой директории.
2. Следуйте инструкциям.

## Для разработки

1. Для тестирования проекта введите команду:
```commandline
pytest --cov src
```
2. Для проверки проекта линтерами введите команду:
```commandline
flake8 src
mypy src
isort src

flake8 tests
mypy tests
isort tests
```
