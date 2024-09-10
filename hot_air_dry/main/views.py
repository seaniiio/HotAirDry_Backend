import json
from django.http import JsonResponse, HttpResponse
from apscheduler.schedulers.background import BackgroundScheduler
import time
import requests
from requests.exceptions import RequestException
import pandas as pd
import random
from .models import *
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from apscheduler.triggers.date import DateTrigger

BASE_DIR = Path(__file__).resolve().parent.parent

secret_file = BASE_DIR / 'secrets.json'

with open(secret_file) as file:
    secrets = json.loads(file.read())

def get_secret(setting,secrets_dict = secrets):
    try:
        return secrets_dict[setting]
    except KeyError:
        error_msg = f'Set the {setting} environment variable'
        raise ImproperlyConfigured(error_msg)


# 랜덤한 데이터 선택
def random_data():
    # print("random_data 실행")
    # df = pd.read_csv('./main/data/tNc_ng_train.csv')
    # random_row = df.sample(n=1)
    # # 선택한 행에서 특정 열만 선택하기
    # selected_columns = ['lot_id', 'Temp', 'Current']  # 열 이름을 변경합니다.
    # random_row_selected = random_row[selected_columns]

    # # 열 이름을 변경합니다.
    # random_row_selected.columns = ['lot_id', 'temperature', 'current']

    # # 선택한 열을 JSON 형식으로 변환하여 객체 하나로 만듭니다.
    # random_row_json = random_row_selected.to_dict(orient='records')[0]

    lot_id = f"Lot{random.randint(0, 12)}"
    temp = round(random.uniform(65.0, 75.0), 2)
    current = round(random.uniform(1.2, 1.75), 2)
    
    # JSON 객체 생성
    data = {
        "lot_id": lot_id,
        "temperature": temp,
        "current": current
    }

    try:
        print("input data:", data)
        response = requests.post(get_secret("DL_URL") + 'predict', json=data)

        if response.status_code == 200:
            print('Data successfully posted')
            response_data = response.json()
            print(response_data)

            try: # create lot
                if len(response_data["lot_id"]) == 4:
                    response_data['lot_id'] = int(response_data['lot_id'][3])
                elif len(response_data["lot_id"]) == 5:
                    response_data['lot_id'] =response_data['lot_id'][3] + response_data['lot_id'][4]
                response = requests.post(get_secret("BACKEND_URL") + 'main/lot/', json=response_data)
                print("Transformer output data:", response)

            except RequestException as e:
                return JsonResponse({'error': str(e)}, status=500)
            
            return response
        else:
            print('Failed to post data:', response.status_code)
    except RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_data(request):
    if request.method == 'GET':
        try:
            scheduler = BackgroundScheduler()
            scheduler.add_job(random_data, 'interval', seconds=1)  # 1초마다 generate_data 함수 실행
            scheduler.start()
        except Exception as e:
            # 로그에 에러 메시지 기록
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            return JsonResponse({'message': error_message}, status=500)
        return JsonResponse({'message': 'Scheduler started.'})
    return JsonResponse({'message':'GET 요청만 허용됩니다.'})

# 상태 보고 솔루션 return하는 메서드
def solution(temperature_contribution, current_contribution, temperature_tendency, current_tendency): # 기여도, 경향성을 바탕으로 판단
    if temperature_contribution > current_contribution: # 온도 기여도 높은경우
        if temperature_tendency == 1: # 온도가 기준보다 높은 경우
            return "온도를 낮춰주세요."
        return "온도를 올려주세요." # 온도가 기준보다 낮은 경우
    else: # 전류 기여도 높은경우
        if current_tendency == 1: # 전류가 기준보다 높은 경우
            return "전류를 낮춰주세요."
        return "전류를 높여주세요." # 전류가 기준보다 낮은 경우

# 로트 데이터 생성 api
def create_lot(request):
    if request.method == 'POST':
        
        data = json.loads(request.body)
        lot_id = data["lot_id"]

        # 이미 해당 lot가 존재하는 경우 -> 덮어씌우기
        if Lot.objects.filter(lot_id = lot_id).exists():
            lot = Lot.objects.get(lot_id=lot_id)

            lot.normal_amount = lot.normal_amount + 1 if data["normal_type"] == 0 else lot.normal_amount
            lot.total_amount = lot.total_amount + 1
            lot.temperature_contribution = data["temperature_contribution"]
            lot.current_contribution = data["current_contribution"]
            lot.temperature_tendency = data["temperature_tendency"]
            lot.current_tendency = data["current_tendency"]
            lot.solution = solution(lot.temperature_contribution, lot.current_contribution, lot.temperature_tendency, lot.current_tendency)
            lot.save()  # 변경 사항을 데이터베이스에 저장

            return HttpResponse('Lot updated successfully.', status=200)
        
        # 해당 lot에 대한 데이터를 처음 받는 경우
        else:
            lot = Lot(
                lot_id = lot_id,
                normal_amount = 1 if data["normal_type"] == 0 else 0,
                total_amount = 1,
                temperature_contribution = data["temperature_contribution"],
                current_contribution = data["current_contribution"],
                temperature_tendency = data["temperature_tendency"],
                current_tendency = data["current_tendency"],
                solution = solution(data["temperature_contribution"], data["current_contribution"], data["temperature_tendency"], data["current_tendency"])
            )
            lot.save()
        
            return HttpResponse('Lot created successfully.', status=200)
        
    return JsonResponse({'message':'POST 요청만 허용됩니다.'})

# 모든 lot 정상 확률 조회 (정상 확률 = (정상 데이터 / 전체 데이터) * 100)
def get_normal_prob(request):
    if request.method == 'GET':
        
        normal_prob_list = []
        for id in range(1, 12):
            if Lot.objects.filter(lot_id = id).exists():
                lot = Lot.objects.get(lot_id = id)
                if lot.total_amount == 0:
                    normal_prob = 100
                else:
                    normal_prob = int((lot.normal_amount / lot.total_amount) * 100)
                normal_prob_list.append(normal_prob)
            else: # 해당 로트에 대한 데이터가 아직 없는 경우
                normal_prob_list.append(100)
            
        return JsonResponse(normal_prob_list, safe=False, status=200)

    return JsonResponse({'message':'GET 요청만 허용됩니다.'})

# 특정 lot 온도, 전류 기여도 조회
def get_contribution(request, lot_id):

    cont = [] # temp, curr 순서
    if request.method == 'GET':
        if Lot.objects.filter(lot_id = lot_id).exists():
            lot = Lot.objects.get(lot_id = lot_id)
            cont = [lot.temperature_contribution, lot.current_contribution]
        else: # 해당 로트에 대한 데이터가 아직 없는 경우
            cont = [0.0, 0.0]

        return JsonResponse(cont, safe=False, status=200)
    return JsonResponse({'message':'GET 요청만 허용됩니다.'})

# 특정 lot 솔루션 조회
def get_solution(request, lot_id):

    if request.method == 'GET':
        if Lot.objects.filter(lot_id = lot_id).exists():
            lot = Lot.objects.get(lot_id = lot_id)
            solution = lot.solution
        else: # 해당 로트에 대한 데이터가 아직 없는 경우
            solution = ""

        return JsonResponse(solution, safe=False, status=200)
    return JsonResponse({'message':'GET 요청만 허용됩니다.'})


# 모든 lot 데이터 초기화
def init_lots(request):

    if request.method == 'POST':
        for lot_id in range(1, 12):
            if Lot.objects.filter(lot_id = lot_id).exists():
                lot = Lot.objects.get(lot_id=lot_id)

                lot.normal_amount = 0
                lot.total_amount = 0
                lot.temperature_contribution = 0.0
                lot.current_contribution = 0.0
                lot.temperature_tendency = 0
                lot.current_tendency = 0
                lot.solution = solution(lot.temperature_contribution, lot.current_contribution, lot.temperature_tendency, lot.current_tendency)
                lot.save()  # 변경 사항을 데이터베이스에 저장
        
        return HttpResponse('Lots initialize successfully.', status=200)
    return JsonResponse({'message':'POST 요청만 허용됩니다.'})

def dummy():
    print(1)