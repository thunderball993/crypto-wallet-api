from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator, Field
from storage import save_balance, load_balance
from fastapi.staticfiles import StaticFiles

# Создаем экземпляр приложения FastAPI
app = FastAPI()

# Подключаем папку со статикой (фронтенд)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Словарь для хранения балансов кошельков
# Ключ - название кошелька, значение - баланс
BALANCE = load_balance()


# Модель для описания операции с деньгами
# BaseModel из Pydantic автоматически валидирует данные
class OperationRequest(BaseModel):
    # Название кошелька (обязательное поле, максимум 127 символов)
    wallet_name: str = Field(..., max_length=127)
    # Сумма операции (обязательное поле, должна быть положительной)
    amount: float
    # Описание операции (необязательное поле, максимум 255 символов)
    description: str | None = Field(None, max_length=255)

    # Валидатор для проверки что сумма положительная
    @field_validator('amount')
    def amount_must_be_positive(cls, v: float) -> float:
        # Проверяем что значение больше нуля
        if v <= 0:
            # Если нет - выбрасываем ошибку валидации
            raise ValueError('Amount must be positive')
        # Возвращаем значение если все ок
        return v

    # Валидатор для проверки что имя кошелька не пустое
    @field_validator('wallet_name')
    def wallet_name_not_empty(cls, v: str) -> str:
        # Убираем пробелы по краям
        v = v.strip()
        # Проверяем что строка не пустая
        if not v:
            # Если пустая - выбрасываем ошибку валидации
            raise ValueError('Wallet name cannot be empty')
        # Возвращаем очищенное значение
        return v


# Модель для создания кошелька
class CreateWalletRequest(BaseModel):
    # Название кошелька (обязательное поле, максимум 127 символов)
    name: str = Field(..., max_length=127)
    # Начальный баланс (необязательное поле, по умолчанию 0)
    initial_balance: float = 0

    # Валидатор для проверки что имя кошелька не пустое
    @field_validator('name')
    def name_not_empty(cls, v: str) -> str:
        # Убираем пробелы по краям
        v = v.strip()
        # Проверяем что строка не пустая
        if not v:
            # Если пустая - выбрасываем ошибку валидации
            raise ValueError('Wallet name cannot be empty')
        # Возвращаем очищенное значение
        return v

    # Валидатор для проверки что начальный баланс не отрицательный
    @field_validator('initial_balance')
    def balance_not_negative(cls, v: float) -> float:
        # Проверяем что значение не отрицательное
        if v < 0:
            # Если отрицательное - выбрасываем ошибку валидации
            raise ValueError('Initial balance cannot be negative')
        # Возвращаем значение если все ок
        return v


@app.get("/balance")
def get_balance(wallet_name: str | None = None):
    # Если имя кошелька не указано - считаем общий баланс
    if wallet_name is None:
        # Суммируем все значения из словаря BALANCE
        return {"total_balance": sum(BALANCE.values())}

    # Проверяем существует ли запрашиваемый кошелек
    if wallet_name not in BALANCE:
        # Если кошелька нет - возвращаем ошибку 404
        raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' not found")

    # Возвращаем баланс конкретного кошелька
    return {"wallet": wallet_name, "balance": BALANCE[wallet_name]}


@app.post("/wallets")
def create_wallet(wallet: CreateWalletRequest):
    # Проверяем не существует ли уже такой кошелек
    if wallet.name in BALANCE:
        # Если кошелек уже есть - возвращаем ошибку 400
        raise HTTPException(status_code=400, detail=f"Wallet '{wallet.name}' already exists")

    # Валидация name и initial_balance теперь в модели CreateWalletRequest!
    # Создаем новый кошелек с начальным балансом
    BALANCE[wallet.name] = wallet.initial_balance
    save_balance(BALANCE)

    # Возвращаем информацию о созданном кошельке
    return {
        "message": f"Wallet '{wallet.name}' created",
        "wallet": wallet.name,
        "balance": BALANCE[wallet.name]
    }


@app.post("/operations/income")
def add_income(operation: OperationRequest):
    # Проверяем существует ли кошелек
    if operation.wallet_name not in BALANCE:
        # Если кошелька нет - возвращаем ошибку 404
        raise HTTPException(
            status_code=404,
            detail=f"Wallet '{operation.wallet_name}' not found"
        )

    # Валидация amount > 0 теперь в модели OperationRequest!
    # Добавляем доход к балансу кошелька
    BALANCE[operation.wallet_name] += operation.amount
    save_balance(BALANCE)

    # Возвращаем информацию об операции
    return {
        "message": "Income added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "description": operation.description,
        "new_balance": BALANCE[operation.wallet_name]
    }


@app.post("/operations/expense")
def add_expense(operation: OperationRequest):
    # Проверяем существует ли кошелек
    if operation.wallet_name not in BALANCE:
        # Если кошелька нет - возвращаем ошибку 404
        raise HTTPException(
            status_code=404,
            detail=f"Wallet '{operation.wallet_name}' not found"
        )

    # Валидация amount > 0 теперь в модели OperationRequest!

    # Проверяем достаточно ли средств в кошельке (это бизнес-логика, не валидация!)
    if BALANCE[operation.wallet_name] < operation.amount:
        # Если денег недостаточно - возвращаем ошибку 400
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: {BALANCE[operation.wallet_name]}"
        )

    # Вычитаем расход из баланса кошелька
    BALANCE[operation.wallet_name] -= operation.amount
    save_balance(BALANCE)
    # Возвращаем информацию об операции
    return {
        "message": "Expense added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "description": operation.description,
        "new_balance": BALANCE[operation.wallet_name]
    }