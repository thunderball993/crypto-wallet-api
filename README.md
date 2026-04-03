```markdown
# Crypto Wallet API

REST API для управления кошельками с веб-интерфейсом.  
Позволяет создавать кошельки, пополнять/списывать средства, получать баланс.  
Данные сохраняются в JSON, проект покрыт тестами.

## Технологии
- Python 3.11
- FastAPI
- Pydantic (валидация)
- Uvicorn (ASGI сервер)
- pytest (тестирование)
- HTML/CSS/JS (фронтенд)

## Запуск проекта

1. Клонировать репозиторий:
```bash
git clone https://github.com/thunderball993/crypto-wallet-api.git
cd crypto-wallet-api
```

2. Создать виртуальное окружение и активировать:
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Запустить сервер:
```bash
uvicorn main:app --reload
```

5. Открыть в браузере:
- Веб-интерфейс: http://127.0.0.1:8000
- Swagger документация: http://127.0.0.1:8000/docs

## API эндпоинты

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/wallets` | Создать кошелёк (JSON: `{"name": "...", "initial_balance": 100}`) |
| GET | `/balance?wallet_name=...` | Получить баланс кошелька |
| GET | `/balance` | Получить общий баланс |
| POST | `/operations/income` | Добавить доход |
| POST | `/operations/expense` | Добавить расход |

## Тестирование

```bash
pytest -v
```

## Планы по улучшению

- [ ] Подключить PostgreSQL вместо JSON
- [ ] Добавить аутентификацию (JWT)
- [ ] Интеграция с реальным Binance API

## Автор

[thunderball993](https://github.com/thunderball993)


   `

