from heapq import heappop, heappush, heapify
import route_function as rf


class MaxRouteHeap:

    def __init__(self, weights):
        # Creating empty heap
        self.heap = []
        heapify(self.heap)
        self.weights = weights

    def add_route_to_heap(self, route):
        # Adding items to the heap using heappush
        # function by multiplying them with -1
        heappush(self.head, -1 * rf.route_score(route, self.weights))

    def select_k_best_routes(self, k):
        best_routes = []
        for i in range(k):
            best_routes.append(heappop(self.heap))



