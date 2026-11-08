from collections import deque


class SlidingWindow:
    """Keeps the (ts, value) pairs from the last `seconds` seconds.

    add: O(1) amortised, average: O(1) (running sum), oldest: O(1).
    ts must be datetime objects, added in increasing time order.
    """

    def __init__(self, seconds):
        self.seconds = seconds
        self.items = deque()
        self.total = 0.0

    def add(self, ts, value):
        self.items.append((ts, value))
        self.total += value
        while (ts - self.items[0][0]).total_seconds() > self.seconds:
            _, old_value = self.items.popleft()
            self.total -= old_value

    def oldest(self):
        return self.items[0]

    def average(self):
        return self.total / len(self.items)

    def __len__(self):
        return len(self.items)