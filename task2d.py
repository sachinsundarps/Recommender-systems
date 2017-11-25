#!usr/bin/python

from __future__ import division
import math
from task1d import PPR
import numpy as np

userid = '109'

ppr = PPR()

movie_movie = ppr.movie_movie_similarity(userid)
top_movies = ppr.calculate_pagerank(movie_movie)
print "Top 5 movies:"
print top_movies

relevant = []
irrelevant = []
movies = top_movies['movienames']
print
for movie in movies:
    data = input("Liked movie " + movie + "?")
    if data == 1:
        relevant.append(movie)
    else:
        irrelevant.append(movie)

genres_str = top_movies['genres']
genres = {}
for genre in genres_str:
    genre = genre.split("|")
    for g in genre:
        if g not in genres.keys():
            genres[g] = 1

# Total number of relevant movies
R = len(relevant)
# Total number of movies
N = 5
# Total number of relevant movies with genres in relevant movies
r_i = {}
for movie in relevant:
    index = top_movies.movienames[top_movies.movienames == movie].index.tolist()
    genre = ppr.movie_genre[top_movies.loc[index[0], 'movies']]
    genre = genre.split("|")
    for g in genre:
        if g not in r_i.keys():
            r_i[g] = 0
        r_i[g] += 1

# Total number of movies with genres in relevant movies
n_i = r_i.copy()
for movie in irrelevant:
    index = top_movies.movienames[top_movies.movienames == movie].index.tolist()
    genre = ppr.movie_genre[top_movies.loc[index[0], 'movies']]
    genre = genre.split("|")
    for g in genre:
        if g in n_i.keys():
            n_i[g] += 1

# Weight of genres in the top movies
w_i = {}
for genre in genres:
    ri = 0
    ni = 0
    if genre in r_i.keys():
        ri = r_i[genre]
    if genre in n_i.keys():
        ni = n_i[genre]
    first_term = (ri + 0.5) / (R - ri + 1)
    second_term = (ni - ri + 0.5) / (N - R - ni + ri + 1)
    w_i[genre] = math.log(first_term / second_term, 10)

# Update the movie-genre matrix with the probabilistic relevant feedback weights
movie_index = {n: movie for movie, n in enumerate(ppr.movie_genre.keys())}
for genre in w_i:
    for movie in ppr.movie_genre.keys():
        if ppr.movies_genres_matrix[movie_index[movie]][ppr.genres[genre]] != 0:
            ppr.movies_genres_matrix[movie_index[movie]][ppr.genres[genre]] += w_i[genre]

# Recreate movie-movie matrix with updated probabilistic relevance feedback
D = np.array(ppr.movies_genres_matrix)
D_T = np.transpose(D)
movie_movie = np.dot(D, D_T)

top_movies = ppr.calculate_pagerank(movie_movie)
print "Top 5 movies based on feedback:"
print top_movies
