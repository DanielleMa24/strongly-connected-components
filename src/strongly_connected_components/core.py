"""Tarjan's algorithm for strongly connected components.

The graph is a plain dict mapping each vertex to an iterable of its
successors. Vertices that appear only as keys (with an empty successor
list) are still part of the graph. Vertices that appear only as
successors are discovered during traversal and treated as having no
outgoing edges.

Components are returned in reverse topological order: if there is an
edge from a vertex in component A to a vertex in component B, then B
appears before A in the result. This is a natural consequence of
Tarjan's single-pass DFS and is the order the algorithm produces
without extra work, so we preserve it rather than sorting.
"""

from collections import defaultdict


def tarjan_scc(graph):
    """Return the strongly connected components of a directed graph.

    Parameters
    ----------
    graph : dict
        Mapping from vertex to an iterable of successor vertices.
        Vertices need not be hashable by any special rule beyond being
        usable as dict keys, which the caller already guarantees by
        placing them in ``graph``.

    Returns
    -------
    list of list
        Each inner list is one strongly connected component. Components
        are returned in reverse topological order (condensation sinks
        first). The order of vertices within a component is the order in
        which the DFS finished discovering them.

    Notes
    -----
    A vertex with no path back to itself forms a singleton component.
    Self-loops (``v`` in ``graph[v]``) place ``v`` in a component by
    itself, but that component still has size one — the self-loop does
    not add a second member.
    """
    # Build a normalized adjacency map. We copy so the caller's dict is
    # never mutated, and we materialize successor iterables into lists
    # so we can traverse them more than once if needed (we don't, but
    # it also defends against one-shot iterators).
    adjacency = {}
    for vertex, successors in graph.items():
        adjacency[vertex] = list(successors)

    index_counter = [0]
    stack = []
    on_stack = set()
    indices = {}
    lowlinks = {}
    result = []

    # Iterative DFS to avoid Python recursion limits on large or
    # pathologically deep graphs. We simulate the call stack with an
    # explicit frame list; each frame holds the vertex and an iterator
    # over its successors.
    for root in adjacency:
        if root in indices:
            continue
        work = [(root, iter(adjacency[root]))]
        while work:
            vertex, succ_iter = work[-1]
            if vertex not in indices:
                indices[vertex] = index_counter[0]
                lowlinks[vertex] = index_counter[0]
                index_counter[0] += 1
                stack.append(vertex)
                on_stack.add(vertex)

            advanced = False
            for successor in succ_iter:
                if successor not in indices:
                    # Tree edge: recurse into the successor.
                    work.append((successor, iter(adjacency.get(successor, ()))))
                    advanced = True
                    break
                elif successor in on_stack:
                    # Back edge or cross edge to a vertex still on the
                    # stack: it can contribute to our lowlink.
                    lowlinks[vertex] = min(lowlinks[vertex], indices[successor])
            if advanced:
                continue

            # Successor iterator exhausted: finalize this vertex.
            work.pop()
            if work:
                parent = work[-1][0]
                lowlinks[parent] = min(lowlinks[parent], lowlinks[vertex])

            if lowlinks[vertex] == indices[vertex]:
                component = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    component.append(w)
                    if w == vertex:
                        break
                result.append(component)

    return result


def strongly_connected_components(graph):
    """Alias for :func:`tarjan_scc`.

    Provided so callers can write
    ``strongly_connected_components(g)`` without naming the algorithm.
    """
    return tarjan_scc(graph)
