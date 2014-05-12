"""This file provides abstraction over the tasks of computing the ranking"""
import numpy as np
import time

from devmine.app.models.feature import Feature
from devmine.app.models.score import Score


__scores_matrix = None
__users_list = None


def __construct_weight_vector(db, query):
    """
    Construct a weight vector, taking default weight from features from the
    database and adapt weights according to the query, which is in the form
    {'python': 5, 'java': 3}.
    Return the weight vector as a dictionnary of feature names and their
    weight.
    """

    features = db.query(Feature).order_by(Feature.name).all()

    weight_vector = []
    for f in features:
        if f.name in query:
            weight_vector.append(query[f.name])
        else:
            weight_vector.append(f.default_weight)

    return weight_vector


def __compute_ranks(A, b, u):
    """
    Compute the ranks vector using a weighted sum.

    Parameter
    ---------
    A:  m x n matrix that contains m users and their n corresponding
        features. The values of each feature must be normalized between
        0 and 1.
    b:  Weights vector of size n
    u:  List of dictionnaries of size n that contains the ulogin and the
        did (developer ID). It must match the rows of the vector b.

    Return
    ------
    retval:  Dictionnary of the form {'username1': rank1, ...}
    """

    ranks = np.dot(A, b)

    retval = []
    it = np.nditer(ranks, flags=['f_index'])
    while not it.finished:
        retval.append({
            'ulogin': u[it.index]['ulogin'],
            'rank': it[0].tolist(),
            'did': u[it.index]['did']
        })
        it.iternext()

    return retval


def get_scores_matrix(db):
    """
    Returns the scores matrix and the list of associated users.
    Data is computed/accessed once and is cached in memory for later calls.
    """
    global __scores_matrix
    global __users_list

    if __scores_matrix is None:
        scores = db.query(Score).order_by(Score.fname).values(Score.ulogin,
                                                              Score.score,
                                                              Score.did)
        d = {}
        u = {}
        for (ulogin, score, did) in scores:
            if ulogin not in d:
                d[ulogin] = []
            d[ulogin].append(score)
            u[ulogin] = did

        __scores_matrix = np.matrix(list(d.values()))
        __users_list = [{'ulogin': v, 'did': u[v]} for v in u]

    return __scores_matrix, __users_list


def rank(db, query):
    """
    Compute the ranking for the developers.
    The weight vector is determined from the user query.
    """
    start_time = time.time()

    w = __construct_weight_vector(db, query)

    A, u = get_scores_matrix(db)
    b = np.matrix(w).transpose()

    end_time = time.time()
    elapsed_time = (end_time-start_time)

    return __compute_ranks(A, b, u), elapsed_time
