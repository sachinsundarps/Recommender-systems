from __future__ import division
from IMDBdatabase import *
import sys


def print_actor_vector(actorid, model):
    cursor.execute("select * from [movie-actor] where actorid=" + str(actorid))
    movie_actor = {}

    for row in cursor.fetchall():
        movie_actor[row[0]] = 1 / row[2]

    tags = create_tags(movie_actor.keys())
    tags = tf_idf(tags)

    tagGroup = tagWeight(tags, movie_actor)
    result = {}

    # Based on the required model, get the correct weight
    # result{}
    #   key     -> tagid
    #   value   -> tf or tf-idf weight based on input model
    for key,value in tagGroup.iteritems():
        if model == "TF":
            result[key] = value[1]
        elif model == "TF-IDF":
            result[key] = value[2]

    # sort the tags using their weights
    result = sorted(result.items(), key=operator.itemgetter(1), reverse=True)

    # Retrieve tag for tagid and print the result
    for value in result:
        cursor.execute("select tag from [genome-tags] where tagid=" + str(value[0]))
        for t in cursor.fetchall():
            print "<",t[0].replace("\"", ""), ", ", value[1],">"


actorid = sys.argv[1]
model = sys.argv[2]
print_actor_vector(actorid, model)
