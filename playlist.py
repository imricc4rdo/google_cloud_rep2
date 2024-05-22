import pandas as pd
import random
import re
from gensim.models import Doc2Vec
from scipy.spatial import distance
import ast


data = pd.read_csv('data_final.csv', index_col = 0)
d2v_titles = Doc2Vec.load("d2v_title_all.model")
d2v_lyrics = Doc2Vec.load("d2v_lyrics_all.model")


def random_playlist(n_songs):
    idx_songs = [random.randint(0, len(data)-1) for n in range(n_songs)]
    playlist = data.iloc[idx_songs]
    songs = []
    for index, row in playlist.iterrows():
        songs.append('"{}", by {}'.format(row['title_c'], row['artist_c']))
    return songs


def filter_title_artist(initial_songs, title, artist):
    title = title.lower()
    artist = artist.lower()
    singer_filter_df = pd.DataFrame(None)
    
    if title in initial_songs['title'].to_list():
        target_index = initial_songs[initial_songs['title'] == title]['idx'].iloc[0]
        similar_songs_idx = [int(i[0]) for i in d2v_lyrics.dv.most_similar(str(target_index), topn=100)]
        title_filter_df = initial_songs[initial_songs['idx'].isin(similar_songs_idx)]
    else: 
        new_title_vector = d2v_titles.infer_vector(title.split())
        similar_songs_idx = [int(i[0]) for i in d2v_lyrics.dv.most_similar([new_title_vector], topn=100)]
        title_filter_df = initial_songs[initial_songs['idx'].isin(similar_songs_idx)]
    
    if artist in initial_songs['artist'].to_list():
        df_singer = initial_songs[initial_songs['artist'] == artist]
        avg_singer_vector = d2v_lyrics.dv.vectors[df_singer.index].mean(axis=0)
        similar_singer_idx = [int(i[0]) for i in d2v_lyrics.dv.most_similar([avg_singer_vector], topn=100)]
        singer_filter_df = initial_songs[initial_songs['idx'].isin(similar_singer_idx)]

    if title_filter_df is not None:
        if singer_filter_df is not None:
            playlist = pd.concat([title_filter_df, singer_filter_df], axis=0)
            playlist.drop_duplicates(inplace=True)
        else:
            playlist = title_filter_df
    else:
        playlist = initial_songs
    return playlist


def calculate_similarity(song_emotions, user_emotions):
    # Ensure song_emotions is in the expected format
    if isinstance(song_emotions, str):
        song_emotions = ast.literal_eval(song_emotions)
    if isinstance(user_emotions, str):
        user_emotions = ast.literal_eval(user_emotions)

    user_emotion_dict = {emotion['label']: emotion['score'] for emotion in user_emotions}
    song_emotion_dict = {emotion['label']: emotion['score'] for emotion in list(song_emotions)}

    common_labels = set(song_emotion_dict.keys()) & set(user_emotion_dict.keys())
    song_vector = [song_emotion_dict[label] for label in common_labels]
    user_vector = [user_emotion_dict[label] for label in common_labels]

    if not song_vector or not user_vector:  # Prevent errors if no common labels
        return 0
    # Compute cosine similarity
    return 1 - distance.cosine(song_vector, user_vector)


def apply_similarity_to_df(df, user_emotions):
    # Iterate over DataFrame rows
    similarities = []
    for index, row in df.iterrows():
        song_emotions = row['processed_labels_scores']
        sim = calculate_similarity(song_emotions, user_emotions)
        similarities.append((row['title_c'], row['artist_c'], sim))
    return similarities


def recommend_songs(sentiments, songs, n):
    similarities = apply_similarity_to_df(songs, sentiments)
    similarities.sort(key=lambda x: x[2], reverse=True)
    output = []
    for song, artist, sim in similarities[:n]:
        output.append(f'"{song}", by {artist}')
    return output 


def adjust_scores(sentiments):
    emotion_scores = sentiments[0]
    top_10_scores = sorted(emotion_scores, key=lambda x: x['score'], reverse=True)[:10]

    # Remove 'neutral' if present
    filtered_scores = [score for score in top_10_scores if score['label'].lower() != 'neutral']

    # If 'neutral' was removed, normalize the remaining scores
    if len(filtered_scores) != len(top_10_scores):
        total_score = sum(score['score'] for score in filtered_scores)
        normalized_scores = [{'label': score['label'], 'score': score['score'] / total_score} for score in
                             filtered_scores]
        return normalized_scores

    # If 'neutral' was not removed, return the top 10 as is
    return top_10_scores


def model_playlist(song, artist, n_songs, sentiments):
    user_emotions = adjust_scores(sentiments)
    songs = filter_title_artist(data, song, artist)
    playlist = recommend_songs(user_emotions, songs, n_songs)
    return playlist
