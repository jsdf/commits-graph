#-*- coding: utf-8 -*-
"""
Generate preformatted data of commits graph.

https://github.com/tclh123/commits-graph

Copyright (c) 2014
MIT License
"""

import json


def generate_graph_data(commits):
    """Generate graph data.

    :param commits: a list of commit, which should have
        `sha`, `parents` properties.
    :returns: data nodes, a json list of
        [
          sha,
          [offset, branch], //dot
          [
            [from, to, branch],  // route 1
            [from, to, branch],  // route 2
            [from, to, branch],
          ]  // routes
        ],  // node
    """

    # cm = []
    # for commit in commits:
    #   cm.append({
    #     'sha': commit.sha,
    #     'parents': commit.parents,
    #   })

    # return fmt(cm)

    nodes = []
    branch_idx = [0]
    reserve = []
    branches = {}

    def get_branch(sha):
        if branches.get(sha) is None:
            branches[sha] = branch_idx[0]
            reserve.append(branch_idx[0])
            branch_idx[0] += 1
        return branches[sha]

    for commit in commits:
        branch = get_branch(commit.sha)
        n_parents = len(commit.parents)
        offset = reserve.index(branch)
        routes = []

        if n_parents == 1:
            # create branch
            if branches.get(commit.parents[0]) is not None:
                routes += [[i + offset + 1, i + offset + 1 - 1, b]
                           for i, b in enumerate(reserve[offset + 1:])]
                routes += [[i, i, b]
                           for i, b in enumerate(reserve[:offset])]
                reserve.remove(branch)
                routes.append([offset,
                               reserve.index(branches[commit.parents[0]]),
                               branch])
            # straight
            else:
                routes += [[i, i, b] for i, b in enumerate(reserve)]
                branches[commit.parents[0]] = branch
        # merge branch
        elif n_parents == 2:
            branches[commit.parents[0]] = branch
            routes += [[i, i, b] for i, b in enumerate(reserve)]
            other_branch = get_branch(commit.parents[1])
            routes.append([offset, reserve.index(other_branch),
                           other_branch])

        node = _make_node(commit.sha,
                          offset,
                          branch,
                          routes)
        nodes.append(node)

    return fmt(nodes)

def fmt(data):
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))


def _make_node(sha, offset, branch, routes):
    return [sha, [offset, branch], routes]
