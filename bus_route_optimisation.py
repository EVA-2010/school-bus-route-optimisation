"""
Graph-Based Optimisation of a School Bus Route in Ludhiana
Case Study: Sarabha Nagar and Nearby Localities

Methods:
- Weighted graph modelling
- Haversine geographic distance
- Dijkstra's shortest-path algorithm
- Nearest-neighbour route optimisation
- Before-and-after route comparison

Author: Eva Likhi
"""

import os
import math
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ------------------------------------------------------------
# 1. REAL-STYLE BUS STOP LOCATIONS IN LUDHIANA
# ------------------------------------------------------------

# Coordinates are approximate locality coordinates.
# Sarabha Nagar, Model Town and BRS Nagar use publicly available coordinates.
# Other stops use approximate coordinates for a realistic case study.

stop_data = {
    "Sarabha Nagar": (30.8925, 75.8176),
    "Model Town": (30.8883, 75.8444),
    "Gurdev Nagar": (30.8950, 75.8300),
    "Model Gram": (30.9010, 75.8260),
    "Jawaddi": (30.8840, 75.8260),
    "Civil Lines": (30.9050, 75.8450),
    "Dugri": (30.8760, 75.8150),
    "Kitchlu Nagar": (30.9120, 75.8070),
    "BRS Nagar": (30.8883, 75.8040),
    "Ayali Chowk": (30.8600, 75.8070),
    "Ferozepur Road": (30.8600, 75.8300)
}

START_LOCATION = "Sarabha Nagar"

# ------------------------------------------------------------
# 2. CALCULATE REALISTIC ROAD DISTANCES
# ------------------------------------------------------------

def haversine_distance(coord1, coord2):
    """
    Calculates straight-line distance between two latitude-longitude points.
    Returns distance in kilometres.
    """

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    R = 6371  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2)
        * math.sin(delta_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def estimate_road_distance(coord1, coord2):
    """
    Converts straight-line distance into an estimated road distance.
    A road-detour factor of 1.35 is commonly used for urban planning estimates.
    """

    straight_line = haversine_distance(coord1, coord2)
    road_distance = straight_line * 1.35

    return round(road_distance, 2)


# Create a complete distance matrix between all stops
stop_names = list(stop_data.keys())

distance_matrix = {}

for i in range(len(stop_names)):
    for j in range(i + 1, len(stop_names)):
        stop_a = stop_names[i]
        stop_b = stop_names[j]

        distance = estimate_road_distance(
            stop_data[stop_a],
            stop_data[stop_b]
        )

        distance_matrix[(stop_a, stop_b)] = distance
        distance_matrix[(stop_b, stop_a)] = distance

# ------------------------------------------------------------
# 3. BUILD THE WEIGHTED GRAPH
# ------------------------------------------------------------

G = nx.Graph()
G.add_nodes_from(stop_names)

for (stop_a, stop_b), distance in distance_matrix.items():
    G.add_edge(stop_a, stop_b, weight=distance)

# ------------------------------------------------------------
# 4. DIJKSTRA'S ALGORITHM
# ------------------------------------------------------------

def find_shortest_path(graph, start, end):
    try:
        path = nx.dijkstra_path(graph, start, end, weight="weight")
        distance = nx.dijkstra_path_length(graph, start, end, weight="weight")
        return path, distance
    except nx.NetworkXNoPath:
        return None, None


print("=" * 75)
print("DIJKSTRA'S ALGORITHM: SHORTEST PATH EXAMPLE")
print("=" * 75)

example_end = "Ferozepur Road"

example_path, example_distance = find_shortest_path(
    G,
    START_LOCATION,
    example_end
)

print(f"Shortest path from {START_LOCATION} to {example_end}:")
print(" -> ".join(example_path))
print(f"Shortest distance: {example_distance:.2f} km")

# ------------------------------------------------------------
# 5. NEAREST-NEIGHBOUR ROUTE OPTIMISATION
# ------------------------------------------------------------

def nearest_neighbour_route(graph, start_stop):
    unvisited = set(graph.nodes)
    unvisited.remove(start_stop)

    current_stop = start_stop
    route = [current_stop]
    total_distance = 0

    while unvisited:
        nearest_stop = None
        nearest_distance = float("inf")

        for stop in unvisited:
            distance = nx.dijkstra_path_length(
                graph,
                current_stop,
                stop,
                weight="weight"
            )

            if distance < nearest_distance:
                nearest_distance = distance
                nearest_stop = stop

        route.append(nearest_stop)
        total_distance += nearest_distance
        unvisited.remove(nearest_stop)
        current_stop = nearest_stop

    return_distance = nx.dijkstra_path_length(
        graph,
        current_stop,
        start_stop,
        weight="weight"
    )

    total_distance += return_distance
    route.append(start_stop)

    return route, total_distance


optimised_route, optimised_distance = nearest_neighbour_route(
    G,
    START_LOCATION
)

print("\n" + "=" * 75)
print("NEAREST-NEIGHBOUR OPTIMISED ROUTE")
print("=" * 75)
print("Optimised route:")
print(" -> ".join(optimised_route))
print(f"Total optimised distance: {optimised_distance:.2f} km")

# ------------------------------------------------------------
# 6. EXISTING ROUTE: BEFORE OPTIMISATION
# ------------------------------------------------------------

# This represents an inefficient existing route:
# the bus travels outward and then returns in a non-optimal order.

existing_route = [
    "Sarabha Nagar",
    "Model Town",
    "Civil Lines",
    "Model Gram",
    "Jawaddi",
    "Dugri",
    "Kitchlu Nagar",
    "BRS Nagar",
    "Ayali Chowk",
    "Ferozepur Road",
    "Gurdev Nagar",
    "Sarabha Nagar"
]

def calculate_route_distance(graph, route):
    total_distance = 0

    for i in range(len(route) - 1):
        start = route[i]
        end = route[i + 1]

        distance = nx.dijkstra_path_length(
            graph,
            start,
            end,
            weight="weight"
        )

        total_distance += distance

    return total_distance


existing_distance = calculate_route_distance(G, existing_route)

distance_saved = existing_distance - optimised_distance
percentage_improvement = (distance_saved / existing_distance) * 100

print("\n" + "=" * 75)
print("BEFORE AND AFTER ROUTE COMPARISON")
print("=" * 75)

print("Existing route:")
print(" -> ".join(existing_route))
print(f"Existing route distance: {existing_distance:.2f} km")

print("\nOptimised route:")
print(" -> ".join(optimised_route))
print(f"Optimised route distance: {optimised_distance:.2f} km")

print(f"\nDistance saved: {distance_saved:.2f} km")
print(f"Percentage improvement: {percentage_improvement:.2f}%")

# ------------------------------------------------------------
# 7. SAVE RESULTS
# ------------------------------------------------------------

os.makedirs("results", exist_ok=True)

results = pd.DataFrame([
    {
        "Route Type": "Existing Route",
        "Route Order": " -> ".join(existing_route),
        "Total Distance (km)": round(existing_distance, 2)
    },
    {
        "Route Type": "Optimised Route",
        "Route Order": " -> ".join(optimised_route),
        "Total Distance (km)": round(optimised_distance, 2)
    }
])

results.to_csv("results/route_comparison.csv", index=False)

# Save distance matrix
matrix_rows = []

for stop_a in stop_names:
    row = {"Stop": stop_a}

    for stop_b in stop_names:
        if stop_a == stop_b:
            row[stop_b] = 0
        else:
            row[stop_b] = distance_matrix[(stop_a, stop_b)]

    matrix_rows.append(row)

distance_df = pd.DataFrame(matrix_rows)
distance_df.to_csv("results/distance_matrix.csv", index=False)

print("\nCSV files saved:")
print("- results/route_comparison.csv")
print("- results/distance_matrix.csv")

# ------------------------------------------------------------
# 8. GRAPH 1: GEOGRAPHIC BEFORE-AFTER ROUTE MAP
# ------------------------------------------------------------

plt.figure(figsize=(14, 10))

# Extract coordinates
x_coords = [stop_data[stop][1] for stop in stop_names]
y_coords = [stop_data[stop][0] for stop in stop_names]

# Draw all possible connections lightly
for (stop_a, stop_b), distance in distance_matrix.items():
    if stop_names.index(stop_a) < stop_names.index(stop_b):
        x = [stop_data[stop_a][1], stop_data[stop_b][1]]
        y = [stop_data[stop_a][0], stop_data[stop_b][0]]

        plt.plot(
            x,
            y,
            color="#CFD8DC",
            linewidth=0.8,
            alpha=0.45,
            zorder=1
        )

# Function to draw a route on the map
def draw_route(route, colour, label, linewidth=3.5, linestyle="-"):
    route_x = []
    route_y = []

    for stop in route:
        lon, lat = stop_data[stop][1], stop_data[stop][0]
        route_x.append(lon)
        route_y.append(lat)

    plt.plot(
        route_x,
        route_y,
        color=colour,
        linewidth=linewidth,
        linestyle=linestyle,
        label=label,
        zorder=3,
        alpha=0.9
    )

# Draw existing route in red
draw_route(
    existing_route,
    "#E53935",
    f"Existing route: {existing_distance:.2f} km",
    linewidth=3,
    linestyle="--"
)

# Draw optimised route in green
draw_route(
    optimised_route,
    "#00C853",
    f"Optimised route: {optimised_distance:.2f} km",
    linewidth=4
)

# Draw stops
for stop, (lat, lon) in stop_data.items():
    if stop == START_LOCATION:
        plt.scatter(
            lon,
            lat,
            s=450,
            color="#FFD54F",
            edgecolor="black",
            linewidth=2,
            zorder=5
        )
    else:
        plt.scatter(
            lon,
            lat,
            s=260,
            color="#E3F2FD",
            edgecolor="#1565C0",
            linewidth=1.8,
            zorder=4
        )

    plt.text(
        lon,
        lat + 0.0012,
        stop,
        fontsize=9,
        ha="center",
        fontweight="bold",
        color="#263238",
        zorder=6
    )

plt.title(
    "Before and After: School Bus Route Optimisation in Ludhiana",
    fontsize=17,
    fontweight="bold",
    pad=20
)

plt.xlabel("Longitude", fontsize=12)
plt.ylabel("Latitude", fontsize=12)

plt.legend(
    loc="upper left",
    fontsize=11,
    frameon=True,
    facecolor="white",
    edgecolor="#90A4AE"
)

plt.grid(True, linestyle="--", alpha=0.35)

plt.text(
    0.01,
    0.02,
    f"Distance saved: {distance_saved:.2f} km\n"
    f"Improvement: {percentage_improvement:.1f}%",
    transform=plt.gca().transAxes,
    fontsize=12,
    fontweight="bold",
    verticalalignment="bottom",
    bbox=dict(
        facecolor="white",
        edgecolor="#455A64",
        boxstyle="round,pad=0.5"
    )
)

plt.tight_layout()
plt.savefig("results/before_after_route_map.png", dpi=300, bbox_inches="tight")
plt.show()

print("Saved: results/before_after_route_map.png")

# ------------------------------------------------------------
# 9. GRAPH 2: DISTANCE COMPARISON
# ------------------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 6))

route_names = ["Existing Route", "Optimised Route"]
route_distances = [existing_distance, optimised_distance]
colours = ["#E53935", "#00C853"]

bars = ax.bar(
    route_names,
    route_distances,
    color=colours,
    width=0.55,
    edgecolor="black",
    linewidth=1.3
)

ax.bar_label(
    bars,
    fmt="%.2f km",
    padding=8,
    fontsize=13,
    fontweight="bold"
)

ax.set_title(
    "Total School Bus Route Distance: Before vs After Optimisation",
    fontsize=16,
    fontweight="bold",
    pad=15
)

ax.set_ylabel("Total Route Distance (km)", fontsize=12)
ax.set_ylim(0, max(route_distances) * 1.25)
ax.grid(axis="y", linestyle="--", alpha=0.4)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig("results/distance_comparison.png", dpi=300)
plt.show()

print("Saved: results/distance_comparison.png")

# ------------------------------------------------------------
# 10. GRAPH 3: DISTANCE MATRIX HEATMAP
# ------------------------------------------------------------

matrix_values = np.zeros((len(stop_names), len(stop_names)))

for i, stop_a in enumerate(stop_names):
    for j, stop_b in enumerate(stop_names):
        if stop_a == stop_b:
            matrix_values[i, j] = 0
        else:
            matrix_values[i, j] = distance_matrix[(stop_a, stop_b)]

plt.figure(figsize=(13, 10))

heatmap = plt.imshow(
    matrix_values,
    cmap="YlGnBu",
    interpolation="nearest"
)

plt.colorbar(heatmap, label="Estimated Road Distance (km)")

plt.xticks(
    ticks=range(len(stop_names)),
    labels=stop_names,
    rotation=45,
    ha="right",
    fontsize=9
)

plt.yticks(
    ticks=range(len(stop_names)),
    labels=stop_names,
    fontsize=9
)

plt.title(
    "Estimated Road-Distance Matrix Between Ludhiana Bus Stops",
    fontsize=16,
    fontweight="bold",
    pad=15
)

for i in range(len(stop_names)):
    for j in range(len(stop_names)):
        value = matrix_values[i, j]

        plt.text(
            j,
            i,
            f"{value:.1f}",
            ha="center",
            va="center",
            fontsize=7,
            color="black" if value < matrix_values.max() * 0.6 else "white"
        )

plt.tight_layout()
plt.savefig("results/distance_matrix_heatmap.png", dpi=300)
plt.show()

print("Saved: results/distance_matrix_heatmap.png")

# ------------------------------------------------------------
# 11. GRAPH 4: DISTANCE FROM SARABHA NAGAR
# ------------------------------------------------------------

distance_from_start = {}

for stop in stop_names:
    if stop != START_LOCATION:
        path, distance = find_shortest_path(G, START_LOCATION, stop)
        distance_from_start[stop] = distance

distance_df = pd.DataFrame(
    list(distance_from_start.items()),
    columns=["Stop", "Shortest Distance from Sarabha Nagar (km)"]
).sort_values("Shortest Distance from Sarabha Nagar (km)")

plt.figure(figsize=(12, 7))

bars = plt.barh(
    distance_df["Stop"],
    distance_df["Shortest Distance from Sarabha Nagar (km)"],
    color="#42A5F5",
    edgecolor="black"
)

plt.bar_label(
    bars,
    fmt="%.2f km",
    padding=5,
    fontsize=10,
    fontweight="bold"
)

plt.title(
    "Shortest Estimated Road Distance from Sarabha Nagar",
    fontsize=16,
    fontweight="bold",
    pad=15
)

plt.xlabel("Shortest Distance (km)", fontsize=12)
plt.ylabel("Pickup Zone", fontsize=12)
plt.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("results/distance_from_sarabha_nagar.png", dpi=300)
plt.show()

print("Saved: results/distance_from_sarabha_nagar.png")
print("\nAll results and graphs saved in the 'results' folder.")
print("Program completed successfully.")