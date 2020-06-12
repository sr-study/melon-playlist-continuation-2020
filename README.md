# melon-playlist-continuation

## 실행법(test용) :
python nns_ensemble_with_artist_with_filter.py run --song_meta_fname=res/song_meta.json --train_fname=arena_data/orig/train.json --question_fname=arena_data/questions/val.json 

## 확인 :
python evaluate.py evaluate --gt_fname=arena_data/answers/val.json --rec_fname=arena_data/results/results.json 


## 제출용(실제 제출) : 
python nns_ensemble_with_artist_with_filter.py run --song_meta_fname=res/song_meta.json --train_fname=res/train.json --question_fname=res/val.json