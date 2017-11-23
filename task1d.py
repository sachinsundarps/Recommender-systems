#!usr/bin/python

from __future__ import division
import numpy as np
import operator
from base import base

base = base()

# Movies watched by the user and date watched
seeds = base.user_movie('20')
seeds = sorted(seeds.items(), key=operator.itemgetter(1), reverse=True)
seeds_weight = {}
count = len(seeds)
for seed in seeds:
    seeds_weight[seed[0]] = count
    count -= 1

movie_genre, movie_year, genres, movie_name = base.movie_genre()

movies_genres_matrix = np.zeros(shape=(len(movie_year), len(genres)), dtype=float)

movies_keys = movie_genre.keys()
movie_index = {n: movie for movie, n in enumerate(movies_keys)}
index_movie = {movie: n for movie, n in enumerate(movies_keys)}

'''
# Create movie-genre matrix using tf-idf values -> not working correctly. genre don't match at last
for movie, genre in movie_genre.iteritems():
    for g in genres:
        if g in genre:
            tf = 1.0 / len(genre)
            idf = base.idf(movie_genre, g)
            tfidf = tf * idf
            movies_genres_matrix[movie_index[movie]][genres[g]] = tfidf
'''

# Create movie-genre matrix using count
for movie, genre in movie_genre.iteritems():
    for g in genres:
        if g in genre:
            movies_genres_matrix[movie_index[movie]][genres[g]] = 1

# Create movie-movie matrix ie., transition matrix
D = np.array(movies_genres_matrix)
D_T = np.transpose(D)
movie_movie = np.dot(D, D_T)

# Create teleportation matrix
teleport = np.zeros(shape=(len(movie_index), 1), dtype=float)
for seed in seeds_weight.keys():
    teleport[movie_index[seed]] = seeds_weight[seed]

alpha = 0.85
err = 0.001

# Column normalize the transition matrix
movie_movie_norm = movie_movie / movie_movie.sum(axis=0)

size = movie_movie_norm.shape[0]
t = np.array(teleport)
pagerank = np.ones(size)
prev = np.zeros(size)

# Calculate pagerank
while np.sum(np.abs(pagerank - prev)) > err:
    prev = pagerank
    pagerank = ((1 - alpha) * np.dot(movie_movie_norm, pagerank)) + (alpha * t)

index_pagerank = {rank: n for rank, n in enumerate(pagerank[-1])}

# Get the top 5 movies
print "Top 5 movies:"
pagerank = sorted(index_pagerank.items(), key=operator.itemgetter(1), reverse=True)
i = 0
while i < 5:
    movie = index_movie[pagerank[i][0]]
    if movie in seeds_weight.keys():
        continue
    print movie, movie_name[movie], "\t", movie_genre[movie], "\t", pagerank[i][1]
    i += 1
