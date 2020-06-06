

### weighted_grpah는 쓰레기로 판명났습니다.

### nns_enseble_with_artist.py에서 계속 이것 저것 바꿔 볼 예정 입니다.





# 실험 일지 (split 0.98로 되있을때 기준 )

## case 쪼개기

선홍님이 말씀하신대로 질의에 종류가 4개다.

case 1 : song + tag

case 2 : tag

case 3 : song

case 4 : x

점수를 case 별로 나눠서 하게 evaluate 함수를 고쳐놨다.

알고리즘의 변화가 어떤 case에서 잘먹고 어떤 case에서 안좋으면 

case 별로 모델을 다른걸 쓸수 있다.
 

## 6월 6일 기준 지수가 제출한 코드 (현재 5등)
### Total score
Music nDCG: 0.236434
Tag nDCG: 0.457622
Score: 0.269612
### song + tag
Music nDCG: 0.252359
Tag nDCG: 0.428683
### tag
Music nDCG: 0.0178572
Tag nDCG: 0.463362
### song
Music nDCG: 0.331558
Tag nDCG: 0.543893
### x
Music nDCG: 0.000511157
Tag nDCG: 0.063024



##  실험 1 
아티스트 점수 변경  
ex)

 song_list 1 = 아이유 곡 6, 황지수 곡 4, 김남웅 곡 2

기존 방법

질의에 아이유 곡이 있으면 가중치 1 

바꾼 방법

질의에 아이유 곡이 이있으면 가중치  6 / 6+4+2 = (train에 아이유 곡)/(전체 곡)

소장르도 비슷한 방법으로 바꿈

### Total score
Music nDCG: 0.233764
Tag nDCG: 0.457979
Score: 0.267396
### song + tag
Music nDCG: 0.253778
Tag nDCG: 0.428884
### tag
Music nDCG: 0.0178572
Tag nDCG: 0.464202
### song
Music nDCG: 0.323833
Tag nDCG: 0.544005
### x(title only)
Music nDCG: 0.000511157
Tag nDCG: 0.0648282



## 실험 2

태그 비교할때 == 에서 in 으로 바꿔 보자 
  
단어가 완전 똑같은게 아니라 유사하게 들어있으면 점수를 주겠다는 아이디어 


### Total score
Music nDCG: 0.234814
Tag nDCG: 0.445503
Score: 0.266417


#### song + tag
Music nDCG: 0.254614
Tag nDCG: 0.405034

#### tag
Music nDCG: 0.0231366
Tag nDCG: 0.442242

#### song
Music nDCG: 0.323833
Tag nDCG: 0.544667

#### x (title only)
Music nDCG: 0.000511157
Tag nDCG: 0.055223

오히려 태그가 떨어짐 , 아마 안 유사한 애들도 들어와서 그런듯


##  실험 3

실험 1 코드 위에 했다. 그러므로 실험 1 은 자동 반영

제목을 끼얹어 보자

가장 단순하게 질의 제목에 있는 단어가 train 제목에 있기라도 하면 가장 큰 유사도 점수를 줘보자. (10점)

### Total score
Music nDCG: 0.224655
Tag nDCG: 0.470986
Score: 0.261605

#### song + tag
Music nDCG: 0.240961
Tag nDCG: 0.473315

#### tag
Music nDCG: 0.0349665
Tag nDCG: 0.388536

#### song
Music nDCG: 0.295177
Tag nDCG: 0.530006

#### x (title only)
Music nDCG: 0.0823252
Tag nDCG: 0.255488


태그는 말도안되게높아졌는데 Music 은 박살남.  title only case에서 tag score가 인상적으로 높다. 





### 실험 5

music이 박살났다는건 안 유사한데 유사하다고 해서 그렇다. 