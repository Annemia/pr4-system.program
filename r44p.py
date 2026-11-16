import aiohttp
import asyncio
import json
from datetime import datetime

CAR_API_URL_1 = "https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json"
CAR_API_URL_2 = "https://vpic.nhtsa.dot.gov/api/vehicles/GetVehicleTypesForMake/audi?format=json"

semaphore = asyncio.Semaphore(3)

async def fetch_data(url, session):
    async with semaphore:
        try:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    print(f"Ошибка {response.status} при запросе к {url}")
        except asyncio.TimeoutError:
            print(f"Таймаут (превышено 5 секунд) при запросе к {url}")
        except Exception as e:
            print(f"Произошла ошибка '{e}' при запросе к {url}")
        return None

async def get_car_data():
    async with aiohttp.ClientSession() as session:
        task1 = fetch_data(CAR_API_URL_1, session)
        task2 = fetch_data(CAR_API_URL_2, session)

        car_makes, car_types = await asyncio.gather(task1, task2)

        return {
            "car_makes": car_makes,
            "car_types": car_types,
            "timestamp": datetime.now().isoformat()
        }

def save_data(data, filename="cars_data.json"):
    with open(filename, "a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")

async def main():
    while True:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S R')}] Запуск сбора данных...")
        data = await get_car_data()

        if data["car_makes"] or data["car_types"]:
            save_data(data)
            print("Данные успешно получены и сохранены в cars_data.json")
        else:
            print("Не удалось получить данные во время текущей итерации.")

        print("Ожидание следующего сеанса связи (10 минут)...\n")
        await asyncio.sleep(600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Программа принудительно остановлена пользователем.")