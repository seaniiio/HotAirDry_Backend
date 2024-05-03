# main.py

import random
from apscheduler.schedulers.background import BackgroundScheduler
import time
import requests
import json

def generate_data():
    # 랜덤한 데이터 생성
    lot_id = random.randint(1, 11)
    normal_type = random.randint(0, 1)
    temperature_contribution = round(random.uniform(0.0, 1.0), 1)
    current_contribution = round(random.uniform(0.0, 1.0), 1)
    temperature_tendency = random.randint(0, 1)
    current_tendency = random.randint(0, 1)
    
    # 데이터 생성
    data = {
        "lot_id": lot_id,
        "normal_type": normal_type,
        "temperature_contribution": temperature_contribution,
        "current_contribution": current_contribution,
        "temperature_tendency": temperature_tendency,
        "current_tendency": current_tendency
    }
    
    # 백엔드 URL
    url = "http://localhost:8000/main/lot/"

    # 데이터를 JSON 형식으로 변환하여 POST 요청으로 보냄
    try:
        response = requests.post(url, json=data)
        print("Data sent successfully:", data)
    except Exception as e:
        print("Error:", e)

def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(generate_data, 'interval', seconds=1)  # 1초마다 generate_data 함수 실행
    scheduler.start()
    print("Data generation scheduler started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Data generation scheduler stopped.")
        scheduler.shutdown()

if __name__ == "__main__":
    main()
