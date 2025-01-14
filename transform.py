def transform(self, x, y):
    return self.trasform_perspective(x, y)


def transform2D(self, x, y):
    return int(x), int(y)


def trasform_perspective(self, x, y):
    lin_y = y * self.perspective_point_y / self.height
    if lin_y > self.perspective_point_y:
        lin_y = self.perspective_point_y

    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - lin_y
    factor_y = diff_y / self.perspective_point_y
    factor_y **= 4

    tr_x = self.perspective_point_x + diff_x * factor_y
    tr_y = (1 - factor_y) * self.perspective_point_y - factor_y

    return int(tr_x), int(tr_y)