import graphlib from 'graphlib'
import first from 'lodash/first'
import isEmpty from 'lodash/isEmpty'

class InvalidGraphError extends Error {
  constructor(message) {
    super(message)
    this.name = 'InvalidGraphError'
  }
}

export default class Graph extends graphlib.Graph {
  constructor({ rootNode, ...args }) {
    super(args)
    this.rootNode = rootNode
  }

  static fromNodeLinkGraph(nodeLinkGraph) {
    const graph = new Graph({ directed: true, rootNode: nodeLinkGraph.root_node })
    nodeLinkGraph.nodes.forEach(({ id, ...label }) => {
      graph.setNode(id, label)
    })
    nodeLinkGraph.links.forEach(({ source, target, ...label }) => {
      graph.setEdge(source, target, label)
    })
    graph.checkAllNodesHaveOneSuccessor()
    return graph
  }

  checkAllNodesHaveOneSuccessor() {
    const nodesWithInvalidSuccessors = this.nodes().filter((node) => this.successors(node).length > 1)
    if (!isEmpty(nodesWithInvalidSuccessors)) {
      throw new InvalidGraphError(
        `All nodes must have exactly one successor. Invalid nodes: ${nodesWithInvalidSuccessors.join(', ')}`,
      )
    }
  }

  successor(id) {
    return first(this.successors(id))
  }

  successors_of(id, numSuccessors = 1, successors = []) {
    if (numSuccessors === 0) return successors
    const successor = this.successor(id)
    return this.successors_of(successor, numSuccessors - 1, [...successors, successor])
  }

  _traverse(callback, node = this.rootNode) {
    const successor = this.successor(node)
    if (successor === this.rootNode) return
    const edge = this.edge(node, successor)
    callback({ node: { id: node, ...this.node(node) }, successor: { id: successor, ...this.node(successor) }, edge })
    this._traverse(callback, successor)
  }

  traverse(callback) {
    this._traverse(callback)
  }

  _buildPath(current, to, path = []) {
    const successor = this.successor(current)
    if (successor === to) return path
    return this._buildPath(successor, to, [...path, successor])
  }

  buildPath(from, to) {
    return this._buildPath(from, to)
  }
}
