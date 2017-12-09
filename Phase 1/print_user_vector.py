from __future__ import division
from IMDBdatabase import *
import sys


def print_user_vector(userid, model):
    cursor.execute("select [movieid],[rating] from [mlratings] where userid=" + str(userid))
    movies = {}
    for row in cursor.fetchall():
        movies[row[0]] = row[1]

    cursor.execute("select [movieid], [tagid] from [mltags] where userid=" + str(userid))
    for row in cursor.fetchall():
        if not row[0] in movies.keys():
            movies[row[0]] = row[1]

    tags = create_tags(movies.keys())
    tags = tf_idf(tags)

    tagGroup = tagWeight(tags)
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
            print "<",t[0], ", ", value[1],">"


userid = sys.argv[1]
model = sys.argv[2]
print_user_vector(userid, model)
