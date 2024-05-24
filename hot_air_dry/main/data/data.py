import pandas as pd

ng_df = pd.read_csv('./tNC_ng_train.csv')
ok_df = pd.read_csv('./tNC_ok_train.csv')

print("ng dataframe의 temperature min, max : ", min(ng_df['Temp']), max(ng_df['Temp']))
print("ng dataframe의 current min, max : ", min(ng_df['Current']), max(ng_df['Current']))

print("ok dataframe의 temperature min, max : ", min(ok_df['Temp']), max(ok_df['Temp']))
print("ok dataframe의 current min, max : ", min(ok_df['Current']), max(ok_df['Current']))

# Temp : 64.0 ~ 134.2
# Current : 0.8 ~ 1.0

# 구간 정의
bins = [50, 55, 60, 65, 70, 75, 80, 85]  # 구간을 나눌 경계값

# 구간에 따라 행을 분류하고 카운트
counts = pd.cut(ok_df['Temp'], bins=bins).value_counts()

# 결과 출력
print("정상 데이터의 Temp 구간별 분석:")
print(counts)

# 구간 정의
bins2 = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]  # 구간을 나눌 경계값

# 구간에 따라 행을 분류하고 카운트
counts = pd.cut(ok_df['Current'], bins=bins2).value_counts()

# 결과 출력
print("정상 데이터의 Current 구간별 분석:")
print(counts)