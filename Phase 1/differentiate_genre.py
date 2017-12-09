from __future__ import division
from IMDBdatabase import *
import sys


# For TF-IDF-DIFF, calculate the distance between two objects using Manhattan distance
# Manhattan distance d = sum(tag weight in genre1 - tag weight in genre2)
def manhattan_distance(vector1, vector2):
    tags1 = {}
    for value in vector1:
        tags1[value[0]] = value[1]
    tags2 = {}
    for value in vector2:
        tags2[value[0]] = value[1]
    keys = set(tags1.keys() + tags2.keys())
    distance = 0
    for key in keys:
        distance += abs(tags1.get(key, 0) - tags2.get(key, 0))
    return distance


# Calculate the TF-IDF value for the tags and order them. Find the distance between the tags.
def tf_idf_diff(tags1={}, tags2={}):
    tags1 = tf_idf(tags1)
    tags2 = tf_idf(tags2)
    tagGroup1 = tagWeight(tags1)
    tagGroup2 = tagWeight(tags2)
    result1 = {}
    for key, value in tagGroup1.iteritems():
        result1[key] = value[2]
    result1 = sorted(result1.items(), key=operator.itemgetter(1), reverse=True)
    print "Genre 1:"
    for value in result1:
        cursor.execute("select tag from [genome-tags] where tagid=" + str(value[0]))
        for t in cursor.fetchall():
            print "<", t[0].replace("\"", ""), ", ", value[1], ">"
    result2 = {}
    for key, value in tagGroup2.iteritems():
        result2[key] = value[2]
    result2 = sorted(result2.items(), key=operator.itemgetter(1), reverse=True)
    print
    print "Genre 2:"
    for value in result2:
        cursor.execute("select tag from [genome-tags] where tagid=" + str(value[0]))
        for t in cursor.fetchall():
            print "<", t[0].replace("\"", ""), ", ", value[1], ">"
    print
    print "Distance between the genres in tag space: ", manhattan_distance(result1, result2)
    return


# Use the given formula to find the weights of tags in genre 1
def p_diff1(R, M, movie_tags1={}, movie_tags2={}):
    for keys, values in movie_tags1.iteritems():
        for value in values:
            count = 0
            for k, v in movie_tags1.iteritems():
                for list in v:
                    if value[0] == list[0]:
                        count += 1
                        break
            value.append(count)
            for k, v in movie_tags2.iteritems():
                for list in v:
                    if value[0] == list[0]:
                        count += 1
                        break
            value.append(count)
    tagGroup = {}
    for key, values in movie_tags1.iteritems():
        for value in values:
            if not tagGroup.keys().__contains__(value[0]):
                tagGroup[value[0]] = [value[2], value[3]]
    result = {}
    # Calculate the weight of tags
    for key, value in tagGroup.iteritems():
        log_value = math.log10((value[0] / (R - value[0] + 0.5)) / ((value[1] - value[0] + 0.5) / (M - value[1] -
                                                                                                   R + value[0])))
        weight = log_value * abs((value[0] / R) - ((value[1] - value[0]) / (M - R + 05)))
        cursor.execute("select tag from [genome-tags] where tagid=" + str(key))
        for t in cursor.fetchall():
            result[t[0]] = weight
    result = sorted(result.items(), key=operator.itemgetter(1), reverse=True)
    for v in result:
        print "<", v[0], ", ", v[1], ">"


def p_diff2(R, M, movie_tags1={}, movie_tags2={}, ):
    for keys, values in movie_tags1.iteritems():
        for value in values:
            count = 0
            for k, v in movie_tags2.iteritems():
                present = 0
                for list in v:
                    if value[0] == list[0]:
                        present = 1
                        break
                if present == 0:
                    count += 1
            value.append(count)
            for k, v in movie_tags1.iteritems():
                present = 0
                for list in v:
                    if value[0] == list[0]:
                        present = 1
                        break
                if present == 0:
                    count += 1
            value.append(count)
    tagGroup = {}
    for key, values in movie_tags1.iteritems():
        for value in values:
            if not tagGroup.keys().__contains__(value[0]):
                tagGroup[value[0]] = [value[2], value[3]]
    result = {}
    # Calculate the weight of tags
    for key, value in tagGroup.iteritems():
        log_value = math.log10((value[0] / (R - value[0] + 0.5)) / ((value[1] - value[0] + 0.5) / (M - value[1] -
                                                                                                   R + value[0])))
        weight = log_value * abs((value[0] / R) - ((value[1] - value[0]) / (M - R)))
        cursor.execute("select tag from [genome-tags] where tagid=" + str(key))
        for t in cursor.fetchall():
            result[t[0]] = weight
    result = sorted(result.items(), key=operator.itemgetter(1), reverse=True)
    for v in result:
        print "<", v[0], ", ", v[1], ">"


# Use the given formula to find the weights of tags in genre 1
def differentiate_genre(genre1, genre2, model):
    cursor.execute("select [movieid],[moviename] from [mlmovies] where genres=\'" + genre1 + "\'")
    movies1 = {}
    for row in cursor.fetchall():
        movies1[row[0]] = row[1]

    cursor.execute("select [movieid],[moviename] from [mlmovies] where genres=\'" + genre2 + "\'")
    movies2 = {}
    for row in cursor.fetchall():
        movies2[row[0]] = row[1]

    movies = {}
    for key, value in movies1.iteritems():
        if not movies.keys().__contains__(key):
            movies[key] = value
    for key, value in movies2.iteritems():
        if not movies.keys().__contains__(key):
            movies[key] = value
    M = len(movies.keys())

    tags1 = create_tags(movies1)
    tags2 = create_tags(movies2)

    if model == "TF-IDF-DIFF":
        tf_idf_diff(tags1, tags2)
        return
    elif model == "P-DIFF1":
        p_diff1(len(movies1.keys()), M, tags1, tags2)
        return
    elif model == "P-DIFF2":
        p_diff2(len(movies2.keys()), M, tags1, tags2)
        return


genre1 = sys.argv[1]
genre2 = sys.argv[2]
model = sys.argv[3]
differentiate_genre(genre1, genre2, model)
