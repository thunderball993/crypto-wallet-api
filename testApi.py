import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def setup_function():
    """Перед каждым тестом очищаем данные (тесты не должны влиять друг на друга)"""
    # Перезагружаем приложение с пустым BALANCE (для чистоты тестов)
    import main
    main.BALANCE.clear()
    # Если используешь storage, можно временно отключить сохранение
    # но для простоты оставим так.

def test_create_wallet():
    response = client.post("/wallets", json={
        "name": "test_wallet",
        "initial_balance": 100
    })
    assert response.status_code == 200
    assert response.json()["wallet"] == "test_wallet"
    assert response.json()["balance"] == 100

def test_create_duplicate_wallet():
    client.post("/wallets", json={"name": "dup", "initial_balance": 10})
    response = client.post("/wallets", json={"name": "dup", "initial_balance": 20})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_get_balance():
    client.post("/wallets", json={"name": "alice", "initial_balance": 50})
    response = client.get("/balance?wallet_name=alice")
    assert response.status_code == 200
    assert response.json()["balance"] == 50

def test_total_balance():
    client.post("/wallets", json={"name": "a", "initial_balance": 10})
    client.post("/wallets", json={"name": "b", "initial_balance": 20})
    response = client.get("/balance")
    assert response.status_code == 200
    assert response.json()["total_balance"] == 30

def test_add_income():
    client.post("/wallets", json={"name": "income_test", "initial_balance": 0})
    response = client.post("/operations/income", json={
        "wallet_name": "income_test",
        "amount": 75.5,
        "description": "salary"
    })
    assert response.status_code == 200
    assert response.json()["new_balance"] == 75.5

def test_add_expense_sufficient():
    client.post("/wallets", json={"name": "exp_test", "initial_balance": 100})
    response = client.post("/operations/expense", json={
        "wallet_name": "exp_test",
        "amount": 30,
        "description": "shopping"
    })
    assert response.status_code == 200
    assert response.json()["new_balance"] == 70

def test_add_expense_insufficient():
    client.post("/wallets", json={"name": "poor", "initial_balance": 10})
    response = client.post("/operations/expense", json={
        "wallet_name": "poor",
        "amount": 100,
        "description": "too much"
    })
    assert response.status_code == 400
    assert "Insufficient funds" in response.json()["detail"]

def test_negative_amount_income():
    client.post("/wallets", json={"name": "neg", "initial_balance": 0})
    response = client.post("/operations/income", json={
        "wallet_name": "neg",
        "amount": -50,
        "description": "negative"
    })
    # Ожидаем ошибку валидации 422 (Pydantic) или 400, но Pydantic вернёт 422
    assert response.status_code == 422

def test_wallet_not_found():
    response = client.get("/balance?wallet_name=nonexistent")
    assert response.status_code == 404