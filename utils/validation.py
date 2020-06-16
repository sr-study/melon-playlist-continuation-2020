from constants import NUM_OF_RECOMMENDED_SONGS
from constants import NUM_OF_RECOMMENDED_TAGS


def validate_answer(answer):
    if len(answer['songs']) != NUM_OF_RECOMMENDED_SONGS:
        raise Exception("추천 곡 결과의 개수가 맞지 않습니다.")

    if len(answer['tags']) != NUM_OF_RECOMMENDED_TAGS:
        raise Exception("추천 태그 결과의 개수가 맞지 않습니다.")

    if len(set(answer['songs'])) != NUM_OF_RECOMMENDED_SONGS:
        raise Exception("한 플레이리스트에 중복된 곡 추천은 허용되지 않습니다.")

    if len(set(answer['tags'])) != NUM_OF_RECOMMENDED_TAGS:
        raise Exception("한 플레이리스트에 중복된 태그 추천은 허용되지 않습니다.")

    return True


def validate_answers(answers, questions):
    gt_ids = set([g['id'] for g in questions])
    rec_ids = set([r['id'] for r in answers])

    if gt_ids != rec_ids:
        raise Exception("결과의 플레이리스트 수가 올바르지 않습니다.")

    rec_song_counts = [len(p['songs']) for p in answers]
    rec_tag_counts = [len(p['tags']) for p in answers]

    if set(rec_song_counts) != set([NUM_OF_RECOMMENDED_SONGS]):
        raise Exception("추천 곡 결과의 개수가 맞지 않습니다.")

    if set(rec_tag_counts) != set([NUM_OF_RECOMMENDED_TAGS]):
        raise Exception("추천 태그 결과의 개수가 맞지 않습니다.")

    rec_unique_song_counts = [len(set(p['songs'])) for p in answers]
    rec_unique_tag_counts = [len(set(p['tags'])) for p in answers]

    if set(rec_unique_song_counts) != set([NUM_OF_RECOMMENDED_SONGS]):
        raise Exception("한 플레이리스트에 중복된 곡 추천은 허용되지 않습니다.")

    if set(rec_unique_tag_counts) != set([NUM_OF_RECOMMENDED_TAGS]):
        raise Exception("한 플레이리스트에 중복된 태그 추천은 허용되지 않습니다.")

    return True
