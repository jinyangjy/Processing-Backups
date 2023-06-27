from collections import deque
from typing import Any
import math

class Graph:
    def __init__(self, origin, target, flow, maxIn, maxOut):
        """
        Approach Description:
            "Initialisation of the residual graph's implementation, taken and modfied from the previous
             assignment of creating a roads and locations graph to meet the specifications for this
             assignment."
            The approach for this question will be split into two parts where I'll first explain
            the approach taken to plot the residual graph instead of needing drawing a flow graph,
            it could be done by directly plotting the residual graph. Following the concept of bottleneck,
            we'll first find the minimum between the connection given, and update the array each
            time we've picked the minimum of a connection. For example, if we have a connection of
            (0,1,5000), it will be listed as min(maxOut[0], maxIn[1], 5000), and in the list of
            maxOut, let's say data centre 0 has a maxOut of 10000, data centre 1 has a maxIn of 5000,
            the minimum would be 5000. Then we would deduct the minimum from the list of both maxOut
            (10000-5000 = 5000, now out max out of 0 will be 5000 available capacity for the following
            iterations) and maxIn (5000-5000 = 0, now maxIn of 1 will no longer have any remaining
            capacity for the following iterations), we'll keep repeating the same process till we
            attained all available capacity for each communication channel. If there're more than two
            targets given, a "super desination" vertex will be added towards the end of the list and
            there'll be an edge connecting them. The purpose of having the capacity to be maxIn of
            target to the super destination's suppose to give us the maximum potential the target has.
        Input:
            origin:
                The source vertex
            target:
                The sink vertex, could be the super destination vertex
            flow:
                A list of tuples, representing an edge in the graph. The first element of each
                tuple is the current vertex, the second element is the next vertex, and the
                third element is the capacity of the edge.
            maxIn:
                A list of integers, where each integer represents the maximum flow that could
                possibly enter the vetex.
            maxOut:
                A list of integers, where each integer represents the maximum flow that could
                possibly flow out of the vetex.
        Return:
            None
        Time Complexity:
            O(|D|+|C|)
        Aux Space Complexity:
            O(|D|)
        """
        self.origin = origin
        self.target = target
        self.flow = flow
        self.maxIn = maxIn
        self.maxOut = maxOut

        # find the maximum vertex number in a list of roads
        maximum_vertex = 0
        for i in flow:
            # checking if the first or second element of the road is greater than the current
            # maximum vertex. If it is, it updates the max number vertex to the element.
            if i[0] > maximum_vertex:
                maximum_vertex = i[0]
            if i[1] > maximum_vertex:
                maximum_vertex = i[1]

        # creating a list of vertices, to store all possible vertices from origin towards target
        self.graph = list(Vertex(centres) for centres in range(maximum_vertex + 1))

        # adding the super vertex to the end of the list of vertices
        self.graph.append(Vertex(len(self.graph)))

        # connecting target vertices to the super destination vertex
        for vertex in target:
            original_edge = Edges(self.graph[vertex], self.graph[-1], self.maxIn[vertex])
            self.graph[vertex].edges.append(original_edge)

        # creating a forward edge for one vertex to the next vertex
        for edges in flow:
            #find the bottle neck between the three values within the connection given
            minimum = min(self.maxOut[edges[0]], self.maxIn[edges[1]], edges[2])
            #updating the capacity on the edge of the choosen minimum
            self.update_terms(edges[0], edges[1], minimum)

            original_edge = Edges(self.graph[edges[0]], self.graph[edges[1]], minimum)

            # if the edge(minimum) has a value of 0, don't take the path
            if minimum == 0 :
                original_edge.available = False

            # reversed_edge = Edges(self.graph[edges[1]], self.graph[edges[0]], 0, True)

            self.graph[edges[0]].insert_edge(original_edge)
            # self.graph[edges[1]].insert_edge(reversed_edge)

            # original_edge.opposite = reversed_edge
            # reversed_edge.opposite = original_edge

    def update_terms(self, vertexOut: int, vertexIn: int, value: int):
        """
        Function Description:
            To update the values for the available capacity of an edge
        Input:
            vertexOut: The ID of the vertex that is sending the flow.
            vertexIn: The ID of the vertex that is receiving the flow.
            value:  The amount of flow to be subtracted from the maxIn and maxOut lists.
        Return:
            None
        Time Complexity:
            O(1)
        Aux Space Complexity:
            O(1)
        """
        self.maxIn[vertexIn] -= value
        self.maxOut[vertexOut] -= value

    def bfs(self, origin, target):
        """
        Function Description:
            Running BFS in order to look for the possible taken to reach the
            destination from source
        Input:
            origin: the source vertex
            target: the sink/ destination vertex
        Time Complexity:
            O(|D|+|C|)
        Aux Space Complexity:
            O(|D|)
        """
        #creating a queue discovered and adding an origin vertex to the queue
        discovered = deque([])
        discovered.append(origin)

        while len(discovered) > 0:
            #removing the current vertex on the queue once it has been discovered
            #the vertex will then be marked as visited
            current_vertex = discovered.popleft()
            current_vertex.visited = True

            if current_vertex == target:
                return

            for edge in current_vertex.edges:
                #the function gets the next possible vertex from the edge
                if edge.available == False:
                    continue
                next_vertex = edge.next_vertex
                #if it's not visited
                if next_vertex.discovered == False:
                    #add the next vertex to the queue, marking it as visted.
                    discovered.append(next_vertex)
                    next_vertex.discovered = True
                    next_vertex.previous = edge
        return

    def bfs_restart(self):
        """
        Function Description:
            In order for ford fulkerson to run bfs to multiple times, this
            function would reset, and re-run bfs.
        Time Complexity:
            O(|D|)
        Aux Space Complexity:
            O(|C|)
        """
        for vertex in self.graph:
            vertex.discovered = False
            vertex.visited = False
            vertex.previous = False

    def has_AugmentingPath(self, origin, target):
        """
        Function Description:
            As long as there's a possible path to be taken from the orign
            towards the target, it will keep iterating.
        Inout:
            origin: the source vertex
            target: the sink vertex
        Return:
            True if there's an augmenting path
            False if there's no augmenting path
        Time Complexity:
            O(|D|+|E|)
        Aux Space Complexity:
            O(D)
        """
        self.bfs(origin, target)
        if target.previous is not False:
            return True
        else:
            return False

    def get_AugmentingPath(self, origin, target):
        """
        Function Description:
            It will take the path for every possible path found. The function
            calls the backtrack function to find the augmenting path from the
            target to origin.
        Input:
            origin: the source vertex
            target: the sink vertex
        Return
            a list of vertices that form the augementing path
        Time Complexity:
            O(|D|+|C|)
        Aux Space Complexity:
            O(D)
        """
        path =  self.backtrack(target, origin)
        return path

    def backtrack(self, origin, target):
        """
        Function description:
            Track the path from start to finish. The function iterates over
            the target's previous vertices and for each of the previous vertex,
            the function would add the vertex to the path list. If the target
            vertex's previous vertex is the origin vertex, it will eventually
            return the path's list.
        Input:
            Origin: The source vertex
            taget: the sink vertex
        Return:
            A list of vertices that form the augmenting path.
        Time Complexity:
            O(|D|+|C|)
        Aux Space Complexity:
            O(D)
        """
        path = []
        currentPosition = origin

        while currentPosition != target:
            if currentPosition == None:
                return path
            #adds the current vertex to the list
            path.append(currentPosition.previous)
            #setting the current vertex to the current vertex's previous vertex
            currentPosition = currentPosition.previous.current_vertex
        return path

    def residual_capacity(self, path: list):
        """
        Function Description:
            the function checks if the edge's capacity is less than the current value
            of bottleneck
        Input:
            path: the list of path that we've form from the augmented path.
        Return:
            The residual capacity of the augmenting path.
        Time Complexity:
            O(|D|)
        Aux Space Complexity:
            O(1)
        """
        bottleneck = math.inf
        for i in path:
            if i.capacity < bottleneck:
                bottleneck = i.capacity
        return bottleneck

    def augmentFlow(self, path, change):
        """
        Function Description:
            Updating the residual network
        Input:
            path: A list of edges that form a path from the source to the sink.
            change: The amount of flow to augment.
        Return:
            The amount of flow that has been augmented
        Time Complexity:
            O(|C|)
        Aux Space Complexity:
            O(|C|)
        """
        for edge in path:
                # if edge.next_vertex.node_id == len(self.maxIn):
                #     edge.capacity -= change
                #     return
                # opposite = edge.opposite
                if edge.reversed == False:
                    edge.capacity -= change
                    # opposite.capacity += change
                else:
                    edge.capacity += change
                    # opposite.capacity -= change
                if edge.capacity <= 0:
                    edge.available = False
                # if opposite.capacity <= 0:
                #     opposite.available = False

                # if opposite.capacity > 0:
                #     opposite.available = True

                # if edge.capacity > 0:
                #     edge.available = True

    def ford_fulkerson(self):
        """
        Approach Description:
            After building a residual network. Run ford fulkerson till there's no longer an
            augmented path. Using this method, we'll update the maximum flow each time a
            bottleneck has been choosen for an augmenting path. When there's no longer an
            augmenting path, it will terminate.
        Return:
            the maximum flow in the network
        Time Complexity:
            O(|D|*|C|^2)
        Space Complexity:
            O(|D|*|C|)
        """
        #initialising the flow
        flow = 0
        residual_network = self
        #Finds the augment path
        while residual_network.has_AugmentingPath(self.graph[self.origin], self.graph[-1]):
            #take the path once it's been found
            path = residual_network.get_AugmentingPath(self.graph[self.origin], self.graph[-1])
            #augment the flow it makes up for the residual capacity
            minimum = residual_network.residual_capacity(path)
            flow += minimum
            #lastly it would update the residual network
            residual_network.augmentFlow(path, minimum)
            #allow bfs to run multiple times to allowance to find multiple paths
            residual_network.bfs_restart()
        return flow

class Vertex:
    def __init__(self, node_id):
        """
        Function description:
            Initialising a node object
        Input:
            node_id: the id of the node/vertex
        Time complexity:
            O(1)
        Space complexity:
            O(1)
        """
        self.node_id = node_id
        self.edges = []
        self.previous = False
        self.visited = False
        self.discovered = False

    def insert_edge(self, edge):
        """
        Function Description:
            Inserts an edge into the trie.
        Input:
            edge: The edge to insert.
        Returns:
            The index of the new edge in the trie.
        Time Complexity:
            O(|C|)
        Space Complexity:
            O(|C|)
        """
        self.edges.append(edge)

class Edges:
    def __init__(self, current_vertex, next_vertex, capacity, is_reversed = False):
        """
        Function description:
            Initialising an edge object
        Input:
            current_vertex: id of current vertex
            next_vertex: id of next vertex
            capacity: The capacity of the edge(flow)
            available: the availablity of an edge
            not used
                opposite
                reversed
        Time complexity:
            O(1)
        Space complexity:
            O(1)
        """
        self.current_vertex = current_vertex
        self.next_vertex = next_vertex
        self.capacity = capacity
        self.available = True
        self.opposite = None
        self.reversed = is_reversed

    def __str__(self) ->str:
        output = " Current: " + str(self.current_vertex.node_id) + " Next: "+ str(self.next_vertex.node_id) + " Capacity: " + str(self.capacity)
        return output

def maxThroughput(connections, maxIn, maxOut, origin, targets):
    """
    Function description:
        Calculates the maximum flow of a network.
    Input:
        connections: A list of connections. Each connection is a tuple of (source, destination, capacity).
        maxIn: A list of maximum indegrees.
        maxOut: A list of maximum outdegrees.
        origin: The source node.
        targets: The target nodes.
    Returns:
        The maximum throughput of the network.
    Time Complexity:
        O(|D|*|C|^2)
    Space Complexity:
        O(|D|+|C|)
    """
    graph = Graph(origin, targets, connections, maxIn, maxOut)
    output = graph.ford_fulkerson()
    return output