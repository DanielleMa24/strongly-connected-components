# strongly_connected_components

Finds the strongly connected components of a directed graph using Tarjan's single-pass algorithm. The graph is a plain `dict` mapping each vertex to an iterable of its successors.

```python
from strongly_connected_components import tarjan_scc

graph = {
    "a": ["b"],
    "b": ["c"],
    "c": ["a", "d"],
    "d": [],
}
components = tarjan_scc(graph)
# components == [["d"], ["a", "b", "c"], ["a"]]  — see ordering note below
```

## Exports

- `tarjan_scc(graph)` — returns a `list` of `list`s, one per component.
- `strongly_connected_components(graph)` — alias for `tarjan_scc`.

## Why this exists

The problem is small enough that pulling in a graph library is overkill, but fiddly enough that hand-rolling a correct SCC implementation every time is a tax. This library is the one file you reach for when you have a `dict` of adjacency lists and need the components, with no dependencies.

The trade-off: the input is a plain `dict`, not a custom graph type. That means vertices must be hashable (they are dict keys), and there is no built-in notion of edge weights or labels. If you need those, this is the wrong library.

## Ordering

Components are returned in **reverse topological order** of the condensation: if an edge runs from component A to component B, B appears before A in the result. This is the order Tarjan's algorithm produces naturally; the library does not sort. Within a component, vertices appear in DFS-finish order.

## Awkward edges

- A vertex that appears only as a successor (never as a key in the dict) is still discovered and treated as having no outgoing edges. It will show up as a singleton component.
- A self-loop (`v` in `graph[v]`) does not enlarge the component; `v` remains a singleton.
- The input dict is never mutated, and successor iterables are consumed once and copied internally, so passing a generator is safe.

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

## Contributing

Issues and pull requests are welcome. Please keep the dependency list empty —
that constraint is the point of the project, not an oversight.

