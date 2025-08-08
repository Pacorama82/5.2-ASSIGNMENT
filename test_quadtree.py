import random
from quadtree import Point, Rectangle, Quadtree

def find_closest_brute_force(query_point, all_points):
    best_p = None
    min_dist_sq = float('inf')
    for p in all_points:
        dist_sq = (p.x - query_point.x)**2 + (p.y - query_point.y)**2
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            best_p = p
    return best_p, min_dist_sq

if __name__ == "__main__":
    # Initialize Quadtree
    boundary = Rectangle(0, 0, 1000, 1000)
    qt = Quadtree(boundary, capacity=4)

    # Generate random points
    num_points = 5000
    points = [Point(random.uniform(0, 1000), random.uniform(0, 1000), f"Driver-{i}") for i in range(num_points)]
    for p in points:
        qt.insert(p)

    # Pick a random query point
    query_point = Point(random.uniform(0, 1000), random.uniform(0, 1000), "Rider")

    # Quadtree nearest neighbor
    qt_nearest, qt_distance = qt.find_nearest(query_point)

    # Brute-force nearest neighbor
    bf_nearest, bf_dist_sq = find_closest_brute_force(query_point, points)
    bf_distance = bf_dist_sq ** 0.5

    # Assert correctness
    assert qt_nearest == bf_nearest, "Quadtree and brute-force results do not match!"

    # Print results
    print(f"Query Point: {query_point}")
    print(f"Quadtree Nearest: {qt_nearest} at distance {qt_distance:.2f}")
    print(f"Brute-Force Nearest: {bf_nearest} at distance {bf_distance:.2f}")
    print("Test passed: Both methods found the same nearest point.")