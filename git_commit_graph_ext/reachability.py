# AUTOGENERATED! DO NOT EDIT! File to edit: ../08_reach.ipynb.

# %% auto 0
__all__ = ['generic_is_reachable', 'generic_is_reachable_dfs', 'reachable_positive_cut', 'reachable_negative_cut',
           'walk_spanning', 'generic_is_reachable_bfs']

# %% ../08_reach.ipynb 4
from collections import deque

# %% ../08_reach.ipynb 9
def generic_is_reachable(DG, u, v,
                         II=None, l=None,
                         stats=None, verbose=None):
    """Whether in graph DG $v$ is reachable from $u$, utilizing given indices
  
    Given (u, v) ∈ V², two vertices in the DAG given by the DG parameter,
    calculate r(u,v), that is whether vertex v is reachable from vertex u.
  
    This is based on the Algorithm 3 from FELINE paper, translated from pseudocode
    to Python (and NetworkX).
  
    NOTE: this is a straightforward recursive version of the function.
  
    Parameters
    ----------
    DG : NetworkX digraph
         Directed acyclic graph.
  
    u : node
        Source node.
  
    v : node
        Target node.
  
    II : dict or None, optional (default=None)
        A dictionary with nodes as keys and min-post interval index as values
        (2-element lists, representing intervals).
  
    l : dict or None, optional (default=None)
        A dictionary with nodes as keys and backward topological vertex level as values
        (vertex level is also known as generation number).
  
    stats : dict or None, optional (default=None)
        A dictionary gathering statistics about calls.  Currently supported
        are:
         * 'access' key, counting the number of intermediate vertices it
           checks / accesses
         * 'level' key, storing list of vertices where level index cut off
           further walk (further search)
         * 'walk' key, with list of all vertices walked, in order
         * 'min-post' key, storing the vertex at which positive-cut
           min-post interval cut-off the need for further search
  
    verbose : bool or None, optional (default=None)
        Whether to print debugging information.  If set to None (the default),
        it prints debugging information if stats parameter is set.
  
    Returns
    -------
    r(u,v) : bool
        Whether v is reachable from u
    """
    if isinstance(stats, dict):
        if verbose is None:
            verbose = True
        stats.setdefault('access', 0)
        stats.setdefault('level', [])
        stats.setdefault('walk', [])

        stats['walk'].append(u)

    if u == v:
        return True

    # II_v ⊆ II_u <=> π(v) ∈ II_u (positive cut)
    # II_v = [min_{w∈T_v}(π(w)),π(v)]
    if II and II[u][0] <= II[v][1] <= II[u][1]:
        if verbose:
            print('%s->%s min-post resolved %s ∈ %r ⊆ %r' %
                  (u, v, II[v][1], II[v], II[u]))
        if isinstance(stats, dict):
            stats['min-post'] = u
        return True

    # debugging
    if verbose:
        if l and not l[v] < l[u]:
            print('%s->%s level cut ¬%d < %d' %
                  (u, v, l[v], l[u]))

    # l_v < l_u (no negative cut)
    if (l and l[v] < l[u]) or (not l):
        # debugging
        if verbose:
            print('%s->%r' % (u, list(DG.successors(u))))
        # worst case analysis, no short-circuit
        result = False
        for w in DG.successors(u):
            if isinstance(stats, dict):
                stats['access'] += 1

            # recursion
            if generic_is_reachable(DG, w, v, II=II, l=l,
                                    stats=stats, verbose=verbose):
                # average case
                # return True
                # worst case analysis
                result = True

        # worst case analysis
        if result:
            return True

    else:
        # negative cut, but which one
        if isinstance(stats, dict):
            if l and not l[v] < l[u]:
                stats['level'].append(u)

    return False

# %% ../08_reach.ipynb 19
def generic_is_reachable_dfs(DG, u, v,
                             II=None, l=None,
                             stats=None):
    """Whether in large graph DG $v$ is reachable from $u$, utilizing given indices
  
    Given (u, v) ∈ V², two vertices in the DAG given by the DG parameter,
    calculate r(u,v), whether vertex v is reachable from vertex u.
  
    This is non-recursive version of the function, without verbose mode,
    intended for larger graphs.  It travels the graph using depth-first search (DFS).
  
    Parameters
    ----------
    DG : NetworkX digraph
         Directed acyclic graph.
  
    u : node
        Source node.
  
    v : node
        Target node.
  
    II : dict or None, optional (default=None)
        A dictionary with nodes as keys and min-post interval index as values
        (2-element lists, representing intervals), e.g. result of
        find_dfs_intervals().
  
    l : dict or None, optional (default=None)
        A dictionary with nodes as keys and vertex level as values
        (vertex level is also known as generation number), e.g. result of
        find_levels().
  
    stats : dict or None, optional (default=None)
        A dictionary gathering statistics about calls.  Currently supported
        are:
         * 'access' key, counting the number of intermediate vertices it
           checks / accesses.
         * 'level-filter' key, storing nodes that level index stopped searching at
         * 'walk' key, storing all walked nodes
         * 'min-post' key, storing node where min-post filter found reachable
         * 'max-depth' key, with maximum stack depth
  
    Returns
    -------
    r(u,v) : bool
        Whether v is reachable from u
    """
    # initialize stats
    if isinstance(stats, dict):
        stats['access'] = 0
        if l:
            stats['level-filter'] = []
        stats['walk'] = []
        stats['max-depth'] = 0
        stats['visited-filter'] = 0

    # iteration in place of recursion
    stack = []
    visited = set()  # it somewhat duplicates stats['walk'] list
    while u is not None:

        # mark 'u' as visited
        visited.add(u)

        if isinstance(stats, dict):
            stats['walk'].append(u)
            stats['max-depth'] = max(stats['max-depth'], len(stack))

        # have we arrived at destination?
        if u == v:
            return True

        # II_v ⊆ II_u <=> π(v) ∈ II_u (positive cut)
        # II_v = [min_{w∈T_v}(π(w)), π(v)]
        if II and II[u][0] <= II[v][1] <= II[u][1]:
            if isinstance(stats, dict):
                stats['min-post'] = u
            return True

        # l_v < l_u (no negative cut; note: u != v)
        if (l and l[v] < l[u]) or (not l):

            # TODO: sort successors
            for w in DG.successors(u):
                if isinstance(stats, dict):
                    stats['access'] += 1

                if w not in visited:
                    stack.append(w)
                    # TODO: break out of loop, to have DFS
                    # TODO= needs to remember which successors visited
                elif isinstance(stats, dict):
                    stats['visited-filter'] += 1

        else:
            # negative cut, but which one
            if isinstance(stats, dict):
                if l and not l[v] < l[u]:
                    stats['level-filter'].append(u)

        # next iteration
        if stack:
            u = stack.pop()
        else:
            # return False only if there is nothing left to do
            return False
        # end while

    # haven't found v
    return False

# %% ../08_reach.ipynb 24
def reachable_positive_cut(u, v,
                           II=None,
                           stats=None):
    """Whether given indices say that $v$ is reachable from $u$

    Given (u, v) ∈ V², a positive cut happens if the reachability index
    implies that vertex v is reachable from vertex u.

        test(u,v) => r(u,v)

    Parameters
    ----------
    u : node
        Source node.

    v : node
        Target node.

    II : dict or None, optional (default=None)
        A dictionary with nodes as keys and min-post interval index as values
        (2-element lists, representing intervals), e.g. result of
        `find_dfs_intervals()`.

        TODO:
        -----
        Or a dictionary with nodes as keys and dict describing DFS-derived
        info, with keys such as 'min' and 'post' describing min-post interval,
        and 'f_min', 'f_gap' and 'p_tree' - like in PReaCH paper; e.g result
        of `find_dfs_intervals_extra()`.

    stats : dict or None, optional (default=None)
        A dictionary gathering statistics about calls (positive cuts).

    Returns
    -------
    test(u,v) : bool
        Whether index indicates that v is reachable from u
    """
    if stats is None:
        stats = {}
    # no data to indicate that v is reachable from u
    if not II:
        return False

    # find_dfs_intervals() case
    if isinstance(II[u], list):
        # II_v ⊆ II_u (positive cut)
        if II[u][0] <= II[v][1] <= II[u][1]:
            stats['positive-cut'] = {
                'type': 'min-post',
                'node': u
            }
            # print("%s -> %s: %d in [%d,%d]" % (u,v,II[v][1], II[u][0], II[u][1]))
            return True

    # find_dfs_intervals_extra() case
    else:
        # π(v) ∈ range(u)  ⇒  r(u,v)
        if II[u]['min'] <= II[v]['post'] <= II[u]['post']:
            stats['positive-cut'] = {
                'type': 'min-post(node)',
                'node': u
            }
            return True

        # elif II[u]['p_tree'] is not None:
        #    p = II[u]['p_tree']
        #    # r(u,p_tree) ∧ ϕ(v) ∈ range(p_tree)  ⇒  r(u,v)
        #    if II[p]['min'] <= II[v]['post'] <= II[p]['post']:
        #        stats['positive-cut'] = {
        #            'type': 'min-post(p_tree)',
        #            'p_tree': p,
        #            'node': u
        #        }
        #        return True

    # no positive cut
    return False


def reachable_negative_cut(u, v,
                           II=None, l=None,
                           stats=None):
    """Whether given indices say that $v$ is not reachable from $u$

    Given (u, v) ∈ V², a negative cut happens if the index implies that
    vertex v is not reachable from vertex u.

        r(u,v) => test(u,v)

    Parameters
    ----------
    u : node
        Source node.

    v : node
        Target node.

    II : dict or None, optional (default=None)
        A dictionary with nodes as keys and min-post interval index as values
        (2-element lists, representing intervals), e.g. result of
        `find_dfs_intervals()`.

        TODO:
        -----
        Or a dictionary with nodes as keys and dict describing DFS-derived
        info, with keys such as 'min' and 'post' describing min-post interval,
        and 'f_min', 'f_gap' and 'p_tree' - like in PReaCH paper; e.g result
        of `find_dfs_intervals_extra()`.

    l : dict or None, optional (default=None)
        A dictionary with nodes as keys and vertex level as values
        (vertex level is also known as generation number), e.g. result of
        `find_levels()`.

    stats : dict or None, optional (default=None)
        A dictionary gathering statistics about calls (negative cuts).

    Returns
    -------
    test(u,v) : bool
        Whether index indicates that v is not reachable from u
    """
    if stats is None:
        stats = {}
    # find all conditions that match
    # otherwise stats would depend on check order
    result = False  # no negative cut

    # we can use levels filter
    if l:
        # r(u,v)    ∧ u ≠ v  ⇒  l_v < l_u, thus
        # l_u ≤ l_v ∧ u ≠ v  ⇒  ¬r(u,v)
        if l[u] < l[v]:
            stats['negative-cut']['level_lite'].append(u)
            result = True

        if u != v and l[u] <= l[v]:
            stats['negative-cut']['level_full'].append(u)
            result = True

    # we can use DFS numbering filter
    # from `find_dfs_intervals_extended()`
    if II and isinstance(II[u], dict):
        pos = II[v]['post']
        if 'f_min' in II[u] and pos < II[u]['f_min']:
            stats['negative-cut']['f_min'].append(u)
            result = True

        if pos > II[u]['post']:
            stats['negative-cut']['f_max'].append(u)
            result = True

        # if 'f_gap' in II[u] and \
        #   II[u]['f_gap'] is not None and \
        #   II[u]['f_gap'] < pos < II[u]['min']:
        #    stats['negative-cut']['f_gap'].append(u)
        #    result = True

    # no further checks
    return result


def walk_spanning(DG, u, v, II):
    """Walk spanning tree from $u$ to $v$, return path or []"""
    path = [u]
    while u != v:
        for w in DG.successors(u):
            # is it in spanning tree
            if not reachable_positive_cut(u, w, II):
                continue

            # can it reach target 'v'
            if reachable_positive_cut(w, v, II):
                u = w
                path.append(u)
                break
            else:
                # should not happen - cannot walk spanning tree to v
                return None

    return path


def generic_is_reachable_bfs(DG, u, v,
                             II=None, l=None,
                             stats=None):
    """Whether in large graph DG $v$ is reachable from $u$, utilizing given indices

    Given (u, v) ∈ V², two vertices in the DAG given by the DG parameter,
    calculate r(u,v), whether vertex v is reachable from vertex u.

    This is non-recursive version of the function, without verbose mode,
    intended for larger graphs.

    Parameters
    ----------
    DG : NetworkX digraph
        Directed acyclic graph.

    u : node
        Source node.

    v : node
        Target node.

    II : dict or None, optional (default=None)
        A dictionary with nodes as keys and min-post interval index as values
        (2-element lists, representing intervals), e.g. result of
        `find_dfs_intervals()`.

        TODO:
        -----
        Or a dictionary with nodes as keys and dict describing DFS-derived
        info, with keys such as 'min' and 'post' describing min-post interval,
        and 'f_min', 'f_gap' and 'p_tree' - like in PReaCH paper; e.g result
        of `find_dfs_intervals_extra()`.

    l : dict or None, optional (default=None)
        A dictionary with nodes as keys and vertex level as values
        (vertex level is also known as generation number), e.g. result of
        `find_levels()`.

    stats : dict or None, optional (default=None)
        A dictionary gathering statistics about calls.

    Returns
    -------
    r(u,v) : bool
        Whether v is reachable from u
    """

    # helper function
    def calc_path(u):
        path = [u]
        u = stats['prev'][u]
        while u is not None:
            path.append(u)
            u = stats['prev'][u]

        return list(reversed(path))

    # initialize stats
    if stats is None:
        stats = {}  # to simplify code always gather stats

    # gather info about negative and positive cuts
    stats['negative-cut'] = {}
    if l:
        # using topological levels / generation numbers for negative cut
        stats['negative-cut']['level_lite'] = []
        stats['negative-cut']['level_full'] = []
    if II and isinstance(II[u], dict):
        # using DFS traversal data from PReaCH paper for negative cut
        stats['negative-cut']['f_max'] = []
        if 'f_min' in II[u]:
            stats['negative-cut']['f_min'] = []
        # if 'f_gap' in II[u]:
        #    stats['negative-cut']['f_gap'] = []
    # do not visit any node twice
    stats['negative-cut']['visited'] = []

    # for finding length of path and path itself
    # compare Dijkstra algorithm
    stats['depth'] = {}
    stats['prev'] = {}

    stats['access'] = 0
    stats['walk'] = []
    stats['max_queue_size'] = 0

    # breadth-first walk in place of recursion
    # queue = Queue() # or PriorityQueue()
    queue = deque([u])
    stats['depth'][u] = 0
    stats['prev'][u] = None
    visited = set()  # it somewhat duplicates stats['walk'] list
    stats['visited'] = visited

    while queue:
        if len(queue) > stats['max_queue_size']:
            stats['max_queue_size'] = len(queue)

        u = queue.popleft()

        # mark 'u' as visited, add to walked
        visited.add(u)
        stats['walk'].append(u)

        # have we arrived at destination?
        if u == v:
            stats['path'] = calc_path(u)
            stats['len'] = stats['depth'][u]
            return True

        # positive cut: we know that 'v' is reachable from 'u'
        # end search (in the future: find full path to 'v')
        if reachable_positive_cut(u, v, II=II, stats=stats):
            stats['path-pre'] = calc_path(u)
            stats['path-post'] = walk_spanning(DG, u, v, II=II)
            stats['len-pre'] = len(stats['path-pre']) - 1
            stats['len-post'] = len(stats['path-post']) - 1
            stats['path'] = stats['path-pre'][:-1] + stats['path-post']
            stats['len'] = stats['len-pre'] + stats['len-post']
            stats['depth'] = stats['depth'][u]
            return True

        # negative cut: we know that 'v' is not reachable from 'u'
        # continue with next node on the list
        if reachable_negative_cut(u, v, l=l, II=II, stats=stats):
            continue

        # walk unvisited parents / successors if not known
        for w in DG.successors(u):
            stats['access'] += 1

            if w not in visited:
                queue.append(w)
                stats['depth'][w] = stats['depth'][u] + 1
                stats['prev'][w] = u
            else:
                stats['negative-cut']['visited'].append(w)

    # we have exhausted search space
    return False
