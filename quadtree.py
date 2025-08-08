import random
import time
import math

class Point:
    def __init__(self, x, y, label=None):
        self.x = x
        self.y = y
        self.label = label

    def __repr__(self):
        return f"Point({self.x:.2f}, {self.y:.2f}, {self.label})"

class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def distance_sq_to_point(self, point):
        """Calculates the squared shortest distance from a point to this rectangle."""
        dx = max(0, self.x - point.x, point.x - (self.x + self.width))
        dy = max(0, self.y - point.y, point.y - (self.y + self.height))
        return dx*dx + dy*dy

    def contains(self, point):
        """Check if the rectangle contains the given point."""
        return (self.x <= point.x < self.x + self.width and
                self.y <= point.y < self.y + self.height)

class QuadtreeNode:
    def __init__(self, boundary, capacity):
        self.boundary = boundary
        self.capacity = capacity
        self.points = []
        self.divided = False
        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def subdivide(self):
        x, y, w, h = self.boundary.x, self.boundary.y, self.boundary.width / 2, self.boundary.height / 2
        self.northwest = QuadtreeNode(Rectangle(x, y, w, h), self.capacity)
        self.northeast = QuadtreeNode(Rectangle(x + w, y, w, h), self.capacity)
        self.southwest = QuadtreeNode(Rectangle(x, y + h, w, h), self.capacity)
        self.southeast = QuadtreeNode(Rectangle(x + w, y + h, w, h), self.capacity)
        self.divided = True

    def insert(self, point):
        # Ignore points outside the boundary
        if not self.boundary.contains(point):
            return False

        if len(self.points) < self.capacity and not self.divided:
            self.points.append(point)
            return True
        else:
            if not self.divided:
                self.subdivide()
                # Move existing points to children
                for p in self.points:
                    self._insert_to_children(p)
                self.points = []  # Clear points from parent after distributing
            # Insert the new point to children
            return self._insert_to_children(point)

    def _insert_to_children(self, point):
        return (self.northwest.insert(point) or
                self.northeast.insert(point) or
                self.southwest.insert(point) or
                self.southeast.insert(point))

    def query(self, point, best_found):
        """
        Recursively finds the nearest point to a given point.
        'best_found' is a dictionary tracking the best point and its distance.
        """
        # 1. Pruning Step: If this quadrant can't possibly have a closer point, stop.
        if self.boundary.distance_sq_to_point(point) > best_found['dist_sq']:
            return

        # 2. Check points in this node
        for p in self.points:
            dist_sq = (p.x - point.x)**2 + (p.y - point.y)**2
            if dist_sq < best_found['dist_sq']:
                best_found['dist_sq'] = dist_sq
                best_found['point'] = p

        # 3. Recursively search children, if they exist
        if self.divided:
            children = [self.northwest, self.northeast, self.southwest, self.southeast]
            # Search children in order of proximity to query point for efficiency
            children.sort(key=lambda child: child.boundary.distance_sq_to_point(point))
            for child in children:
                child.query(point, best_found)

    def _find_nearest(self, query_point, best_found):
        # Prune if this node can't possibly have a closer point
        if self.boundary.distance_sq_to_point(query_point) > best_found['dist_sq']:
            return

        # Check all points in this node
        for p in self.points:
            dist_sq = (p.x - query_point.x)**2 + (p.y - query_point.y)**2
            if dist_sq < best_found['dist_sq']:
                best_found['dist_sq'] = dist_sq
                best_found['point'] = p

        # Recursively search children, prioritizing the quadrant containing the query_point
        if self.divided:
            children = [self.northwest, self.northeast, self.southwest, self.southeast]
            # Prioritize the quadrant containing the query_point
            children.sort(key=lambda child: not child.boundary.contains(query_point))
            for child in children:
                child._find_nearest(query_point, best_found)

class Quadtree:
    def __init__(self, boundary, capacity=4):
        self.boundary = boundary
        self.root = QuadtreeNode(boundary, capacity)

    def insert(self, point):
        return self.root.insert(point)

    def query(self, point, best_found):
        return self.root.query(point, best_found)

    def find_nearest(self, query_point):
        best_found = {'dist_sq': float('inf'), 'point': None}
        self.root._find_nearest(query_point, best_found)
        return best_found['point'], math.sqrt(best_found['dist_sq'])

def find_closest_brute_force(query_point, all_points):
    """The simple O(N) search for comparison."""
    best_p = None
    min_dist_sq = float('inf')
    for p in all_points:
        dist_sq = (p.x - query_point.x)**2 + (p.y - query_point.y)**2
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            best_p = p
    return best_p, min_dist_sq

# --- Setup ---
map_boundary = Rectangle(0, 0, 1000, 1000)
qt = Quadtree(map_boundary, capacity=4)

# Populate with a large number of random points (drivers)
num_points = 5000
points = [Point(random.uniform(0, 1000), random.uniform(0, 1000), f"Driver-{i}") for i in range(num_points)]
for p in points:
    qt.insert(p)

# Define a query point (rider)
query_point = Point(512, 512, "Rider")

print(f"--- Searching for nearest to {query_point} among {num_points} points ---\n")

# --- Quadtree Search ---
start_time_qt = time.perf_counter()

best_found_qt = {'dist_sq': float('inf'), 'point': None}
qt.query(query_point, best_found_qt)

end_time_qt = time.perf_counter()
elapsed_qt = (end_time_qt - start_time_qt) * 1000

print(f"Quadtree Search found: {best_found_qt['point']} at distance {math.sqrt(best_found_qt['dist_sq']):.2f}")
print(f"Time taken: {elapsed_qt:.6f} ms\n")

# --- Brute-Force Search ---
start_time_bf = time.perf_counter()

best_point_bf, best_dist_sq_bf = find_closest_brute_force(query_point, points)

end_time_bf = time.perf_counter()
elapsed_bf = (end_time_bf - start_time_bf) * 1000

print(f"Brute-Force Search found: {best_point_bf} at distance {math.sqrt(best_dist_sq_bf):.2f}")
print(f"Time taken: {elapsed_bf:.6f} ms\n")

# --- Comparison ---
print(f"Quadtree was {elapsed_bf / elapsed_qt:.2f}x faster than brute-force.")