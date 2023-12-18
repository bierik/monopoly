import { expect, test } from 'vitest'
import Graph from '@/board/graph'

function createSimpleGraph() {
  return Graph.fromNodeLinkGraph({
    nodes: [
      { id: 'a', type: 1 },
      { id: 'b', type: 1 },
      { id: 'c', type: 1 },
      { id: 'd', type: 1 },
    ],
    links: [
      { source: 'a', target: 'b', direction: 'BOTTOM' },
      { source: 'b', target: 'c', direction: 'RIGHT' },
      { source: 'c', target: 'd', direction: 'LEFT' },
      { source: 'd', target: 'a', direction: 'TOP' },
    ],
    root_node: 'a',
  })
}

test('constructs graph from a serialized node link graph', () => {
  const graph = createSimpleGraph()
  expect(graph.nodes()).toEqual(['a', 'b', 'c', 'd'])
  expect(graph.edges()).toEqual([
    { v: 'a', w: 'b' },
    { v: 'b', w: 'c' },
    { v: 'c', w: 'd' },
    { v: 'd', w: 'a' },
  ])
})

test('does not allow a graph where nodes have more than one successor', () => {
  expect(() => {
    Graph.fromNodeLinkGraph({
      nodes: [{ id: 'a' }, { id: 'b' }, { id: 'c' }],
      links: [
        { source: 'a', target: 'b' },
        { source: 'a', target: 'c' },
      ],
    })
  }).throws('All nodes must have exactly one successor. Invalid nodes: a')
})

test('gets n successors of a node', () => {
  const graph = createSimpleGraph()
  expect(graph.successors_of('a', 0)).toEqual([])
  expect(graph.successors_of('a', 1)).toEqual(['b'])
  expect(graph.successors_of('a', 2)).toEqual(['b', 'c'])
  expect(graph.successors_of('a', 3)).toEqual(['b', 'c', 'd'])
  expect(graph.successors_of('a', 4)).toEqual(['b', 'c', 'd', 'a'])
})

test('traverse the graph', () => {
  const graph = createSimpleGraph()
  const callbacks = []
  graph.traverse(({ node, successor, edge }) => callbacks.push({ node, successor, edge }))
  expect(callbacks).toEqual([
    { node: { id: 'a', type: 1 }, successor: { id: 'b', type: 1 }, edge: { direction: 'BOTTOM' } },
    { node: { id: 'b', type: 1 }, successor: { id: 'c', type: 1 }, edge: { direction: 'RIGHT' } },
    { node: { id: 'c', type: 1 }, successor: { id: 'd', type: 1 }, edge: { direction: 'LEFT' } },
  ])
})

test('build a path between two nodes', () => {
  const graph = createSimpleGraph()
  expect(graph.buildPath('a', 'd')).toEqual(['b', 'c'])
})
