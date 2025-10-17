def print_bezier_point(point, index=0):
    print(f'Point {index}: {point.co}')


def print_spline(spline, index):
    points = spline.bezier_points
    print(f'Spline {index} has {len(points)} points')
    for index, point in enumerate(points):
        print_bezier_point(point, index)


def print_splines(so):
    print(f'Object {so.name} has {len(so.data.splines)} splines')
    for index, spline in enumerate(so.data.splines):
        print_spline(spline, index)

    print()