import json
import requests
from collections import defaultdict

# Параметры для фильтрации
min_ton = 1
max_ton = 1000
max_total_ton = 1000  # Максимальная сумма
account_id = "UQBadGpOrYtPLbcefWC_9CZU2IbDfa5SaWkcbXYX0EMeuwRs"


# Функция для фильтрации транзакций
def is_valid_transaction(transaction):
    # Исключаем транзакции с NFT и другими токенами
    in_msg = transaction.get('in_msg', {})
    if in_msg.get('decoded_op_name') == 'nft_ownership_assigned':
        return False
    return True


# Функция для получения транзакций с API
def fetch_transactions(account_id, limit=500):
    url = f"https://tonapi.io/v2/blockchain/accounts/{account_id}/transactions"
    params = {
        'limit': limit
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        transactions = response.json().get('transactions', [])
        transactions.reverse()  # Переворачиваем список транзакций
        return transactions
    else:
        print(f"Error fetching data: {response.status_code}")
        return []


# Получение данных с API
transactions = fetch_transactions(account_id)

# Словарь для хранения сумм по адресам
address_sums = defaultdict(int)
# Словарь для хранения исключенных сумм по адресам
excluded_sums = defaultdict(int)
# Переменная для отслеживания общей суммы TON
total_ton = 0

# Обработка транзакций
for transaction in transactions:
    if is_valid_transaction(transaction):
        in_msg = transaction.get('in_msg', {})
        source = in_msg.get('source', {}).get('address')
        value = in_msg.get('value')
        if source and value:
            ton_value = value / 1e9  # Преобразование в TON
            if min_ton <= ton_value <= max_ton:
                if total_ton + ton_value <= max_total_ton:
                    address_sums[source] += ton_value
                    total_ton += ton_value
                else:
                    excluded_sums[source] += ton_value
            else:
                excluded_sums[source] += ton_value

# Формирование списка в нужном формате
result = [[address, value] for address, value in address_sums.items()]
excluded_result = [[address, value] for address, value in excluded_sums.items()]

# Запись результата в файл
with open('result.json', 'w', encoding='utf-8') as outfile:
    json.dump(result, outfile, ensure_ascii=False, indent=4)

# Запись исключенных транзакций в файл
with open('excluded_transactions.json', 'w', encoding='utf-8') as exfile:
    json.dump(excluded_result, exfile, ensure_ascii=False, indent=4)

# Вывод информации в консоль
total_wallets = len(address_sums)

print(f"Всего кошельков прислало: {total_wallets}")
print(f"Всего средств было прислано: {total_ton:.6f} TON")

print("Результат успешно записан в файл result.json")
print("Исключенные транзакции записаны в файл excluded_transactions.json")
