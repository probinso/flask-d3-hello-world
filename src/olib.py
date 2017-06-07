#!/usr/bin/env python3

import csv
import json
import sys

from operator  import itemgetter
from functools import partial

import numpy as np
#from sklearn.cluster import KMeans
#from scipy.spatial.distance import cdist


def selector(D, show=3):
    while True:

        cl_idx = D.cluster()
        clstrs = {k: D[v, :] for k, v in cl_idx.items()}
        ranked = {k: v[v.rank(), :] for k, v in clstrs.items()}

        yield {k: v[0:show, :] for k, v in ranked.items()}
        select = (yield)

        if select == -1:
            break
        D = ranked[select]
    return clstrs


class Organizer(np.ndarray):
    """
      DATA : np.array where each index represents a document vector
    """
    def relivance(self, *args, **kwargs):
        raise NotImplemented

    def cluster(self, *args, **kwargs):
        raise NotImplemented

    def rank(self, *args, **kwargs):
        raise NotImplemented

    def select(self, idx):
        return self.__class__(self[idx])

    @property
    def _count(self):
        return np.size(self, 0)

    @property
    def _all_idx(self):
        return np.arange(0, self._count)

    def process(self):
        pass


class IRelivance(Organizer):
    def relivance(self):
        """
          this returns the indicies of all documents
        """
        return self._all_idx


class ICluster(Organizer):
    def cluster(self, number=3):
        """
          Given a count of clusters, return indicies as a dictionary
          that indicate documents in each cluster
        """
        def split_padded(a,n):
            padding = (-len(a))%n
            return np.split(np.concatenate((a,np.zeros(padding))),n)

        clusters = split_padded(self._all_idx, number)
        return {k: v.astype('int') for k, v in enumerate(clusters)}


class IRank(Organizer):
    def rank(self):
        """
          Idenity rank sorts on index, then returns a subset of the indicies
        """
        return np.sort(self._all_idx)


class IOrganizer(IRank, ICluster, IRelivance):
    pass


def tojson(groups):
    return json.dumps({str(k):v.tolist() for k, v in groups.items()})


def interface(inpath):
    with open(inpath, 'rb') as fd:
        data = np.loadtxt(fd, delimiter=',', skiprows=1).astype('float')

    io = data[:, 0:2].view(IOrganizer)
    for result in selector(io):
        print(tojson(result))


def cli_interface():
    """
    by convention it is helpful to have a wrapper_cli method that interfaces
    from commandline to function space.
    """
    try:
        inpath = sys.argv[1]
    except:
        print("usage: {}  <inpath>".format(sys.argv[0]))
        sys.exit(1)
    interface(inpath)


if __name__ == '__main__':
    cli_interface()
