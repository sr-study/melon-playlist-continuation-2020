# test data 분포로 다시 시작 
### valid 크기는 train 0.98

# Music score
|실험 종류|실험 1|실험 2|실험 3|
|:---|---|---|---|
|'Total'|0.262636| 0.261536|0.234777|
|'song only'|0.292449| 0.292449| 0.276454|
|'song tag' | 0.319215 | 0.319215|0.312748|
|'tag title'| 0.100205 | 0.0911516|0.00327498|
|'title only'|0.0883235  | 0.0883235|0.00302212|

# tag score

|실험 종류|실험 1|실험 2|실험 3|
|:---|---|---|---|
|'Total'|0.484903|0.476119|0.396213|
|'song only'|0.514966|0.515175|0.547337|
|'song tag' |0.47373  |0.474522|0.375157|
|'tag title'| 0.517693 |0.438308|0.142626|
|'title only'|0.324417 |0.330453| 0.0643964|



# 실험 1 (6월 12일 제출)
### 카카오 실제 점수 
0.265090	0.465693

### 우리 valid 점수
0.262636  0.484903

## 실험 2

모든 word in 으로 비교

## 실험 3

모두 코싸인 유사도로 변경
tag title artist genrle 유사도 제거 
순수 song으로만 해봄


##실험 4

tag title artist genrle 유사도 추가 

##실험 5
title only 추가

### 우리 valid 점수
Total score
Music nDCG: 0.264713
Tag nDCG: 0.476756
Score: 0.296519



#### song only
Music nDCG: 0.291868
Tag nDCG: 0.514128

#### song tag
Music nDCG: 0.315392
Tag nDCG: 0.455831
#### tag title
Music nDCG: 0.108201
Tag nDCG: 0.511789
#### title only
Music nDCG: 0.122921
Tag nDCG: 0.3184

