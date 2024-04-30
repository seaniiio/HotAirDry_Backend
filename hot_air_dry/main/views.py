import json
from django.http import JsonResponse, HttpResponse

from .models import *


def main(request):
    return HttpResponse("main server ok!")

# 로트 데이터 생성 api
def create_lot(request, lot_id):
    if request.method == 'POST':
        
        data = json.loads(request.body)

        # 이미 해당 lot가 존재하는 경우 -> 덮어씌우기
        if Lot.objects.filter(lot_id = lot_id).exists():
            lot = Lot.objects.get(lot_id=lot_id)
            lot.normal_prob = data['normal_prob']
            lot.abnormal_type = data['abnormal_type']
            lot.temp_normal_prob = data['temp_normal_prob']
            lot.current_normal_prob = data['current_normal_prob']
            lot.save()  # 변경 사항을 데이터베이스에 저장
            return HttpResponse('Lot updated successfully.', status=200)
        
        else:
            lot = Lot(
                lot_id = lot_id,
                normal_prob = data['normal_prob'],
                abnormal_type = data['abnormal_type'],
                temp_normal_prob = data['temp_normal_prob'],
                current_normal_prob = data['current_normal_prob']
            )
            lot.save()
        return HttpResponse('Lot created successfully.', status=200)
