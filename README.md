# Melon Playlist Continuation
카카오 아레나 Melon Playlist Continuation 대회 제출용 코드입니다.

**CF 모델**, **Graph 모델** 두개를 각각 결과를 내어, 최종적으로 앙상블 합니다.


## 수행 방법

인자로, song_meta.json의 위치, train.json의 위치, question파일(val.json, test.json)의 위치, 장르 파일 위치(genre_gn_all.json)을 넘겨줍니다.
	
	```bash
	$> python run.py run \
		--song_meta_fname=res/song_meta.json \
		--train_fname=arena_data/orig/train.json \
		--question_fname=arena_data/questions/val.json \
		--genre_fname=res/genre_gn_all.json
	```


## 실행 결과	
각각의 각 두 모델에 대한 결과는 `/cf/results/results.json`, `/graph/results/results.json` 에 저장되며, 

앙상블 된 최종 추천 결과는 `/results/results.json` 에 저장됩니다. 


## Contact
그 외 문의사항은 아래 이메일로 연락 부탁드립니다.

pica4500@gmail.com

h0h6h2h5@gmail.com

goo1514@naver.com

kimnamwoong12@gmail.com

