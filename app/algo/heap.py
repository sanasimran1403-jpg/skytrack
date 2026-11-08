from app.algo.geo import haversine_km


class MinHeap:
    """Binary min-heap stored in a list.

    push: O(log n), pop: O(log n), peek: O(1).
    Items must be comparable (e.g. tuples like (priority, value)).
    """

    def __init__(self):
        self._a = []

    def __len__(self):
        return len(self._a)

    def peek(self):
        if not self._a:
            raise IndexError("peek from empty heap")
        return self._a[0]

    def push(self, item):
        a = self._a
        a.append(item)
        i = len(a) - 1
        while i > 0:
            parent = (i - 1) // 2
            if a[i] < a[parent]:
                a[i], a[parent] = a[parent], a[i]
                i = parent
            else:
                break

    def pop(self):
        a = self._a
        if not a:
            raise IndexError("pop from empty heap")
        top = a[0]
        last = a.pop()
        if a:
            a[0] = last
            i, n = 0, len(a)
            while True:
                left, right = 2 * i + 1, 2 * i + 2
                smallest = i
                if left < n and a[left] < a[smallest]:
                    smallest = left
                if right < n and a[right] < a[smallest]:
                    smallest = right
                if smallest == i:
                    break
                a[i], a[smallest] = a[smallest], a[i]
                i = smallest
        return top


def n_nearest(points, lat, lon, n):
    """Return the n nearest points as [(distance_km, item_id), ...], nearest first.

    Keeps a bounded heap of size n (root = farthest of the kept points).
    Time: O(m log n) for m points. Space: O(n).
    points = [(item_id, lat, lon), ...]
    """
    heap = MinHeap()  # stores (-distance, item_id)
    for item_id, plat, plon in points:
        d = haversine_km(lat, lon, plat, plon)
        if len(heap) < n:
            heap.push((-d, item_id))
        elif d < -heap.peek()[0]:
            heap.pop()
            heap.push((-d, item_id))

    out = []
    while len(heap):
        neg_d, item_id = heap.pop()
        out.append((-neg_d, item_id))
    out.reverse()
    return out