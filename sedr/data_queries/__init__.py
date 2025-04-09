import util
import pytest
import math

from collections import namedtuple
from urllib.parse import urljoin, urlencode

Point = namedtuple("Point", ["long", "lat"])
Queries = namedtuple("Queries", ["inside", "outside"])


def position_queries(base_url, extent, data_query_json):
    point_inside = points_inside(1, extent)[0]
    point_outside = points_outside(1, extent)[0]

    if len(point_outside) == 0:
        return Queries(
            urljoin(base_url, "position")
            + f"?coords=POINT({point_inside.long} {point_inside.lat})",
            "",
        )

    return Queries(
        urljoin(base_url, "position")
        + f"?coords=POINT({point_inside.long} {point_inside.lat})",
        urljoin(base_url, "position")
        + f"?coords=POINT({point_outside.long} {point_outside.lat})",
    )


def radius_queries(base_url, extent, data_query_json):
    long = (extent[2] - extent[0]) / 2 + extent[0]
    lat = (extent[3] - extent[1]) / 2 + extent[1]

    query_params = {
        "coords": f"POINT({long} {lat})",
        "within": "1000",
        "within_units": "m",
    }

    return Queries(
        urljoin(base_url, "position") + "?" + urlencode(query_params),
    )


def area_queries(base_url, extent):
    inside_polygon = ""
    outside_polygon = ""

    n_points = 4
    for i, p in enumerate(points_inside(n_points, extent)):
        inside_polygon += f"{p.long} {p.lat}"
        if i != n_points:
            inside_polygon += ","

    for i, p in enumerate(points_outside(n_points, extent)):
        outside_polygon += f"{p.long} {p.lat}"
        if i != n_points:
            outside_polygon += ","

    return Queries(
        urljoin(base_url, "area") + "?" + f"coords=POLYGON({inside_polygon})",
        urljoin(base_url, "area") + "?" + f"coords=POLYGON({outside_polygon})",
    )

def trajectory_queries(base_url, extent):
    inside_trajectory = ""
    outside_trajectory = ""

    n_points = 4
    for i, p in enumerate(points_inside(n_points, extent)):
        inside_trajectory += f"{p.long} {p.lat}"
        if i != n_points:
            inside_trajectory += ","

    for i, p in enumerate(points_outside(n_points, extent)):
        outside_trajectory += f"{p.long} {p.lat}"
        if i != n_points:
            outside_trajectory += ","

    return Queries(
        urljoin(base_url, "trajectory") + "?" + f"coords=LINESTRING({inside_trajectory})",
        urljoin(base_url, "trajectory") + "?" + f"coords=LINESTRING({outside_trajectory})",
    )


def points_inside(n_points, extent):
    points = []
    long_step = (extent[2] - extent[0]) / (n_points + 1)
    lat_step = (extent[3] - extent[1]) / (n_points + 1)

    for point in range(n_points):
        long = extent[0] + long_step * (point+1)
        lat = extent[1] + lat_step * (point+1)

        points.append(Point(long, lat))

    return points


def points_outside(n_points, extent):
    points = []

    # Check if extent is global. If so, no points can be created
    if extent[0] == -180 and extent[1] == -90 and extent[2] == 180 and extent[3] == 90:
        return points

    # Create a set of points relatively close to each other.
    # Either north or south of spatial extent. Pick north first if it has most "room".
    long_step = (extent[2] - extent[0]) / (n_points * 100)
    if abs(extent[3]) < abs(extent[1]):
        lat_step = (90 - abs(extent[3])) / (n_points * 100)
        for point in range(n_points):
            long = extent[0] + long_step * (point+1)
            lat = extent[3] + lat_step * (point+1)

            points.append(Point(long, lat))
    else:
        lat_step = (90 - abs(extent[1])) / (n_points * 100)
        for point in range(n_points):
            long = extent[0] + long_step * (point+1)
            lat = extent[1] - lat_step * (point+1)

            points.append(Point(long, lat))

    return points


def collection_url(links):
    collection_link = next((x for x in links if x["rel"] == "data"), None)

    if collection_link is None:
        pytest.fail(f"Expected link with rel=self to be present: {links}")

    return collection_link["href"]
