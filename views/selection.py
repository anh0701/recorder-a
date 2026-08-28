from PySide6.QtCore import QPoint, QRect


class SelectionController:

    def __init__(
        self,
        screen_rect: QRect,
        min_size: int = 20,
    ):
        self.screen_rect = QRect(screen_rect)
        self.min_size = min_size

        self.selection = QRect()

        self.mode = None
        self.ratio = None

        self.action = None

        self.drag_start = QPoint()
        self.original_selection = QRect()


    def set_mode(
        self,
        mode,
        ratio=None,
    ):
        self.mode = mode
        self.ratio = ratio

        self.reset()


    def reset(self):

        self.selection = QRect()

        self.action = None

        self.drag_start = QPoint()

        self.original_selection = QRect()


    def is_valid(self):

        return (
            not self.selection.isNull()
            and self.selection.width()
            >= self.min_size
            and self.selection.height()
            >= self.min_size
        )


    def create(
        self,
        start: QPoint,
        end: QPoint,
    ):

        if self.ratio is None:

            self.selection = QRect(
                start,
                end,
            ).normalized()

        else:

            endpoint = self.calculate_ratio_endpoint(
                start,
                end,
            )

            self.selection = QRect(
                start,
                endpoint,
            ).normalized()

        self.selection = (
            self.clamp_rect_to_screen(
                self.selection
            )
        )

        return self.selection


    def start_move(
        self,
        pos: QPoint,
    ):

        if not self.is_valid():
            return False

        if not self.selection.contains(pos):
            return False

        self.action = "move"

        self.drag_start = QPoint(pos)

        self.original_selection = QRect(
            self.selection
        )

        return True


    def move(
        self,
        pos: QPoint,
    ):

        if self.action != "move":
            return

        delta = (
            pos
            - self.drag_start
        )

        new_rect = QRect(
            self.original_selection
        )

        new_rect.translate(
            delta
        )

        self.selection = (
            self.clamp_rect_to_screen(
                new_rect
            )
        )


    def get_handle_at(
        self,
        pos: QPoint,
    ):

        if not self.is_valid():
            return None

        rect = self.selection

        hs = 16

        handles = {
            "nw": QPoint(
                rect.left(),
                rect.top(),
            ),

            "n": QPoint(
                rect.center().x(),
                rect.top(),
            ),

            "ne": QPoint(
                rect.right(),
                rect.top(),
            ),

            "e": QPoint(
                rect.right(),
                rect.center().y(),
            ),

            "se": QPoint(
                rect.right(),
                rect.bottom(),
            ),

            "s": QPoint(
                rect.center().x(),
                rect.bottom(),
            ),

            "sw": QPoint(
                rect.left(),
                rect.bottom(),
            ),

            "w": QPoint(
                rect.left(),
                rect.center().y(),
            ),
        }

        for name, point in handles.items():

            handle_rect = QRect(
                point.x() - hs,
                point.y() - hs,
                hs * 2,
                hs * 2,
            )

            if handle_rect.contains(pos):
                return name

        return None
    

    def start_resize(
        self,
        handle,
        pos: QPoint,
    ):

        if not handle:
            return False

        if not self.is_valid():
            return False

        self.action = handle

        self.drag_start = QPoint(pos)

        self.original_selection = QRect(
            self.selection
        )

        return True



    def resize(
        self,
        pos: QPoint,
    ):

        if self.action not in (
            "nw",
            "n",
            "ne",
            "e",
            "se",
            "s",
            "sw",
            "w",
        ):
            return

        if self.ratio is None:

            self.selection = (
                self.resize_free(
                    self.original_selection,
                    pos,
                )
            )

        else:

            self.selection = (
                self.resize_ratio(
                    self.original_selection,
                    pos,
                )
            )

        self.selection = (
            self.clamp_rect_to_screen(
                self.selection
            )
        )


    def resize_free(
        self,
        rect: QRect,
        pos: QPoint,
    ):

        left = rect.left()
        top = rect.top()
        right = rect.right()
        bottom = rect.bottom()

        if "w" in self.action:
            left = pos.x()

        if "e" in self.action:
            right = pos.x()

        if "n" in self.action:
            top = pos.y()

        if "s" in self.action:
            bottom = pos.y()

        if (
            right - left + 1
            < self.min_size
        ):

            if "w" in self.action:

                left = (
                    right
                    - self.min_size
                    + 1
                )

            else:

                right = (
                    left
                    + self.min_size
                    - 1
                )

        if (
            bottom - top + 1
            < self.min_size
        ):

            if "n" in self.action:

                top = (
                    bottom
                    - self.min_size
                    + 1
                )

            else:

                bottom = (
                    top
                    + self.min_size
                    - 1
                )

        return QRect(
            QPoint(left, top),
            QPoint(right, bottom),
        ).normalized()


    def resize_ratio(
        self,
        rect: QRect,
        pos: QPoint,
    ):

        ratio = self.ratio

        if ratio is None:
            return rect

        handle = self.action

        # Corners

        if handle in (
            "nw",
            "ne",
            "se",
            "sw",
        ):

            if handle == "nw":

                anchor = QPoint(
                    rect.right(),
                    rect.bottom(),
                )

                width = abs(
                    pos.x()
                    - anchor.x()
                )

                height = int(
                    width / ratio
                )

                return QRect(
                    anchor.x()
                    - width
                    + 1,

                    anchor.y()
                    - height
                    + 1,

                    width,
                    height,
                )

            if handle == "ne":

                anchor = QPoint(
                    rect.left(),
                    rect.bottom(),
                )

                width = abs(
                    pos.x()
                    - anchor.x()
                )

                height = int(
                    width / ratio
                )

                return QRect(
                    anchor.x(),
                    anchor.y()
                    - height
                    + 1,

                    width,
                    height,
                )

            if handle == "se":

                anchor = QPoint(
                    rect.left(),
                    rect.top(),
                )

                width = abs(
                    pos.x()
                    - anchor.x()
                )

                height = int(
                    width / ratio
                )

                return QRect(
                    anchor.x(),
                    anchor.y(),
                    width,
                    height,
                )

            # sw

            anchor = QPoint(
                rect.right(),
                rect.top(),
            )

            width = abs(
                pos.x()
                - anchor.x()
            )

            height = int(
                width / ratio
            )

            return QRect(
                anchor.x()
                - width
                + 1,

                anchor.y(),

                width,
                height,
            )

        # Horizontal

        if handle in ("e", "w"):

            width = max(
                self.min_size,
                abs(
                    pos.x()
                    - (
                        rect.left()
                        if handle == "e"
                        else rect.right()
                    )
                ),
            )

            height = max(
                self.min_size,
                int(width / ratio),
            )

            if handle == "e":

                x = rect.left()

            else:

                x = (
                    rect.right()
                    - width
                    + 1
                )

            y = (
                rect.center().y()
                - height // 2
            )

            return QRect(
                x,
                y,
                width,
                height,
            )

        # Vertical

        if handle in ("n", "s"):

            height = max(
                self.min_size,
                abs(
                    pos.y()
                    - (
                        rect.bottom()
                        if handle == "n"
                        else rect.top()
                    )
                ),
            )

            width = max(
                self.min_size,
                int(height * ratio),
            )

            if handle == "s":

                y = rect.top()

            else:

                y = (
                    rect.bottom()
                    - height
                    + 1
                )

            x = (
                rect.center().x()
                - width // 2
            )

            return QRect(
                x,
                y,
                width,
                height,
            )

        return rect


    def calculate_ratio_endpoint(
        self,
        start: QPoint,
        pos: QPoint,
    ):

        dx = pos.x() - start.x()
        dy = pos.y() - start.y()

        if dx == 0 and dy == 0:
            return start

        ratio = self.ratio

        abs_dx = abs(dx)
        abs_dy = abs(dy)

        if (
            abs_dx
            / max(abs_dy, 1)
            > ratio
        ):

            width = abs_dx
            height = int(
                width / ratio
            )

        else:

            height = abs_dy
            width = int(
                height * ratio
            )

        width = max(
            width,
            self.min_size,
        )

        height = max(
            height,
            self.min_size,
        )

        direction_x = (
            1 if dx >= 0 else -1
        )

        direction_y = (
            1 if dy >= 0 else -1
        )

        return QPoint(
            start.x()
            + direction_x * width,

            start.y()
            + direction_y * height,
        )


    def clamp_rect_to_screen(
        self,
        rect: QRect,
    ):

        result = QRect(rect)

        screen = self.screen_rect

        if result.left() < screen.left():

            result.moveLeft(
                screen.left()
            )

        if result.right() > screen.right():

            result.moveRight(
                screen.right()
            )

        if result.top() < screen.top():

            result.moveTop(
                screen.top()
            )

        if result.bottom() > screen.bottom():

            result.moveBottom(
                screen.bottom()
            )

        return result


    def finish_action(self):

        self.action = None

        self.drag_start = QPoint()

        self.original_selection = QRect()