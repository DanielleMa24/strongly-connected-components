import unittest

from strongly_connected_components import tarjan_scc, strongly_connected_components


class TestTarjanSCC(unittest.TestCase):

    def test_empty_graph(self):
        self.assertEqual(tarjan_scc({}), [])

    def test_single_vertex_no_edges(self):
        result = tarjan_scc({"a": []})
        self.assertEqual(result, [["a"]])

    def test_single_vertex_self_loop(self):
        # A self-loop does not grow the component; it stays a singleton.
        result = tarjan_scc({"a": ["a"]})
        self.assertEqual(result, [["a"]])

    def test_two_vertex_cycle(self):
        result = tarjan_scc({"a": ["b"], "b": ["a"]})
        self.assertEqual(result, [["b", "a"]])

    def test_simple_dag_reverse_topological_order(self):
        # a -> b -> c, no cycles. Each vertex is its own component.
        # Reverse topological order means c before b before a.
        result = tarjan_scc({"a": ["b"], "b": ["c"], "c": []})
        self.assertEqual(result, [["c"], ["b"], ["a"]])

    def test_cycle_plus_tail(self):
        # a -> b <-> c, and c -> d (d is a sink).
        # Components: {b, c} and {a} and {d}.
        # Reverse topological: {d} first, then {b, c}, then {a}.
        graph = {
            "a": ["b"],
            "b": ["c"],
            "c": ["b", "d"],
            "d": [],
        }
        result = tarjan_scc(graph)
        self.assertEqual(result, [["d"], ["c", "b"], ["a"]])

    def test_two_separate_cycles(self):
        graph = {
            "a": ["b"],
            "b": ["a"],
            "c": ["d"],
            "d": ["c"],
        }
        result = tarjan_scc(graph)
        # The two cycles are independent. Root "a" is processed first,
        # so its component is emitted before we ever start "c".
        self.assertEqual(result, [["b", "a"], ["d", "c"]])

    def test_nested_cycles(self):
        # Outer cycle a -> b -> c -> a, plus inner edge b -> c.
        graph = {
            "a": ["b"],
            "b": ["c"],
            "c": ["a"],
        }
        result = tarjan_scc(graph)
        self.assertEqual(result, [["c", "b", "a"]])

    def test_vertex_appearing_only_as_successor(self):
        # "b" is never a key, but is reachable from "a". It should be
        # treated as a vertex with no outgoing edges.
        graph = {"a": ["b"]}
        result = tarjan_scc(graph)
        self.assertEqual(result, [["b"], ["a"]])

    def test_integer_vertices(self):
        graph = {1: [2], 2: [1]}
        result = tarjan_scc(graph)
        self.assertEqual(result, [[2, 1]])

    def test_tuple_vertices(self):
        graph = {(0, 0): [(0, 1)], (0, 1): [(0, 0)]}
        result = tarjan_scc(graph)
        self.assertEqual(result, [[(0, 1), (0, 0)]])

    def test_successor_iterable_is_consumed_once(self):
        # A generator must be safe to pass as a successor list.
        def gen():
            yield "b"
        result = tarjan_scc({"a": gen(), "b": []})
        self.assertEqual(result, [["b"], ["a"]])

    def test_input_graph_not_mutated(self):
        graph = {"a": ["b"], "b": ["a"]}
        original = {k: list(v) for k, v in graph.items()}
        tarjan_scc(graph)
        self.assertEqual(graph, original)

    def test_alias_matches_primary(self):
        graph = {"a": ["b"], "b": ["a"]}
        self.assertEqual(
            strongly_connected_components(graph),
            tarjan_scc(graph),
        )

    def test_large_chain_no_cycle(self):
        # Stresses the iterative implementation: a deep chain would
        # blow the recursion limit in a naive recursive version.
        n = 2000
        graph = {i: [i + 1] for i in range(n)}
        graph[n - 1] = []
        result = tarjan_scc(graph)
        self.assertEqual(len(result), n)
        # Each component is a singleton; reverse topological order.
        self.assertEqual(result[0], [n - 1])
        self.assertEqual(result[-1], [0])

    def test_cross_edge_between_branches(self):
        # a -> b, a -> c, c -> b. No cycle. b is a sink.
        graph = {"a": ["b", "c"], "b": [], "c": ["b"]}
        result = tarjan_scc(graph)
        self.assertEqual(result, [["b"], ["c"], ["a"]])


if __name__ == "__main__":
    unittest.main()
