from __future__ import division
import pymssql
from datetime import datetime as dt
import datetime
import math
import operator


# SQL SERVER connection
con = pymssql.connect("SASHA", "sa", "s", "IMDBdatabase")
cursor = con.cursor()


# Create a tag dictionary for the movies
# tags{}
#   key     -> movieid
#   value   -> list of tagid and timestamp weight
def create_tags(movies):
    tags = {}
    for id in movies:
        cursor.execute(
            "select [movieid],[tagid],[timestamp] from mltags where movieid=" + str(id) + "order by timestamp")
        result = cursor.fetchall()
        tags[id] = []
        epoch = datetime.datetime.utcfromtimestamp(0)
        time_sum = 0
        # Calculate timestamp weight for each tag - timestamp of the tag / sum of timestamps of tags in that movie
        # This is the time-weight
        for t in result:
            date = dt.strptime(t[2].replace("\"", ""), '%Y-%m-%d %X')
            time_sum += (date - epoch).total_seconds()
        for t in result:
            date = dt.strptime(t[2].replace("\"", ""), '%Y-%m-%d %X')
            tags[id].append([t[1], (date - epoch).total_seconds() / time_sum])
    return tags


# Calculate tf and tf-idf value for all the tags
# tags{}
#   keys    -> movieid
#   value   -> list of tagid, timestamp weight, tf, tf-idf
def tf_idf(tags={}):
    for movie, tag in tags.iteritems():
        for t in tag:
            # Calculate the tf of a tag - no. of occurrence of tag in the movie / total no. of tags in the movie
            # Since the tags are time-weighted, add the timestamp weight to tf - tf + timestamp weight
            t.append((sum(tag[n].count(t[0]) for n in range(0, len(tag))) / len(tag)) + t[1])
            count = 0
            # Calculate the idf of a tag - log(total no. of movies / no. of movies that contains the tag)
            # Calculate tf-idf - time-weighted tf * idf
            for key, value in tags.iteritems():
                if sum([value[n].count(t[0]) for n in range(0, len(value))]) > 0:
                    count += 1
            t.append(t[2] * math.log10(len(tags) / count))
    return tags


# Combine the tags and calculate the total weight of each tag. Add additional weight is given
# tagGroup{}
#   keys    -> tagid
#   values  -> list of time-weighted tf and tf-idf
def tagWeight(tags={}, movie_actor=[]):
    tagGroup = {}
    for key, values in tags.iteritems():
        for value in values:
            # Add movie-actor rank weight to the tf (or) tf-idf weights
            if tagGroup.keys().__contains__(value[0]):
                if len(movie_actor) == 0:
                    tagGroup[value[0]][1] += value[2]
                    tagGroup[value[0]][2] += value[3]
                else:
                    tagGroup[value[0]][1] += value[2] + movie_actor[key]
                    tagGroup[value[0]][2] += value[3] + movie_actor[key]
            else:
                if len(movie_actor) == 0:
                    tagGroup[value[0]] = [value[0], value[2], value[3]]
                else:
                    tagGroup[value[0]] = [value[0], value[2] + movie_actor[key], value[3] + movie_actor[key]]

    return tagGroup
