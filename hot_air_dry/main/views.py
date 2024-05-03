import json
from django.http import JsonResponse, HttpResponse

from .models import *


def main(request):
    return HttpResponse("main server ok!")

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


# JSON 입력 형식
# {
# 	"lot_id" : 2,
# 	"normal_type" : 0,
# 	"temperature_contribution" : 0.6,
# 	"current_contribution" : 0.4,
# 	"temperature_tendency" : 1,
# 	"current_tendency" : 0
# }
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
