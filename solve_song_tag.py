from collections import Counter


def _get_song_recommends(song_sets, my_songs, sorted_list, my_artists_counter, my_genres_counter, song_meta):
    rec_song_list = list()
    weight = []
    song_weights = Counter()

    for i in range(40):
        weight.append(sorted_list[i][0])

    for i in range(40):
        if sorted_list[i][0] == 0:
            break
        cur_playlist = song_sets[sorted_list[i][1]]
        for song in cur_playlist:
            if song not in my_songs:
                song_weights[song] += weight[i]
                cur_artists = song_meta[song]['artist_id_basket']

                for artist in cur_artists:
                    if artist in my_artists_counter:
                        song_weights[song] += weight[i]  * (my_artists_counter[artist])/(sum(my_artists_counter.values()))
                        break

                cur_genres = song_meta[song]['song_gn_dtl_gnr_basket']
                tot_num = len(cur_genres)
                matched_num = 0
                for genre in cur_genres:
                    if genre in my_genres_counter:
                        matched_num += my_genres_counter[genre]
                if matched_num:
                    #w = int((matched_num / tot_num)*(weight[i] // 2))
                    song_weights[song] +=  matched_num/ (sum(my_genres_counter.values()))*weight[i]

    song_weights_sorted = song_weights.most_common()

    for song_pair in song_weights_sorted:
        if len(rec_song_list) == 100:
            return rec_song_list
        song = song_pair[0]
        if (song not in my_songs) and (song not in rec_song_list):
            rec_song_list.append(song)

    for i in range(len(sorted_list)):
        cur_playlist = song_sets[sorted_list[i][1]]
        for song in cur_playlist:
            if len(rec_song_list) == 100:
                return rec_song_list
            if (song not in my_songs) and (song not in rec_song_list):
                rec_song_list.append(song)

    return rec_song_list


def _get_tag_recommends(tag_sets, my_tags, sorted_list):
    rec_tag_list = list()
    weight = []
    tag_weights = Counter()
    cnt = 0
    for i in range(30):
        weight.append(sorted_list[i][0])

    for i in range(30):
        if sorted_list[i][0] == 0:
            break
        cur_taglist = tag_sets[sorted_list[i][1]]
        for tag in cur_taglist:
            if tag not in my_tags:
                tag_weights[tag] += weight[i]

    tag_weights_sorted = tag_weights.most_common()

    for tag_pair in tag_weights_sorted:
        if len(rec_tag_list) == 10:
            return rec_tag_list
        tag = tag_pair[0]
        if (tag not in my_tags) and (tag not in rec_tag_list):
            rec_tag_list.append(tag)

    for i in range(len(sorted_list)):
        cur_playlist_tags = tag_sets[sorted_list[i][1]]
        for tag in cur_playlist_tags:
            if len(rec_tag_list) == 10:
                return rec_tag_list
            if (tag not in my_tags) and (tag not in rec_tag_list):
                rec_tag_list.append(tag)

    return rec_tag_list

def solve_song_tag(song_sets, tag_sets, title_lists, song_meta, my_songs, my_tags, my_title):
    tag_only = False

    my_artists_counter = Counter()
    my_genres_counter = Counter()
    for song in my_songs:
        cur_artists = song_meta[song]['artist_id_basket']
        my_artists_counter.update(cur_artists)

        cur_genres = song_meta[song]['song_gn_dtl_gnr_basket']
        my_genres_counter.update(cur_genres)

    sorted_list = []

    for idx, song_set in enumerate(song_sets):
        intersect_num = 0
        for song in my_songs:
            if song in song_set:
                intersect_num += 10

        for tag_q in my_tags:

            for tag_t in tag_sets[idx]:
                if tag_q in tag_t or tag_t in tag_q:
                    if tag_t == tag_q:
                        intersect_num += 6
                        if tag_only:
                            break
                    else:
                        if not tag_only:
                            intersect_num += 2

        for word in my_title:
            if word in title_lists[idx]:
                intersect_num += 3

        sorted_list.append([intersect_num, idx])

    sorted_list.sort(key=lambda x: x[0], reverse=True)
    rec_song_list = _get_song_recommends(song_sets, my_songs, sorted_list,
                                         my_artists_counter, my_genres_counter, song_meta)
    rec_tag_list = _get_tag_recommends(tag_sets, my_tags, sorted_list)

    if len(rec_song_list) != 100:
        print(f'song sz : {len(rec_song_list)}')
    if len(rec_tag_list) != 10:
        print(f'tag sz : {len(rec_tag_list)}')

    return rec_song_list, rec_tag_list
