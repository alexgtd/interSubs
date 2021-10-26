from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QBrush, QPen, QPalette, QPaintEvent, QFontMetrics
from PyQt5.QtWidgets import QLabel


class OutlinedLabel(QLabel):
    def __init__(self, text: str, config):
        super().__init__(text)
        self.cfg = config

    def draw_text_and_outline(self) -> None:
        x = 0
        y = 0
        y += self.fontMetrics().ascent()
        y = y + self.cfg.outline_top_padding - self.cfg.outline_bottom_padding

        painter = QPainter(self)
        text_painter_path = self.get_text_painter_path(x, y)
        outline_color = QColor(self.cfg.outline_color)
        outline_width = self.cfg.outline_thickness

        self.draw_blur(painter, text_painter_path, outline_color, outline_width)
        self.draw_outline(painter, text_painter_path, outline_color, outline_width)
        self.draw_text(painter, x, y)

    def get_text_painter_path(self, x: int, y: int) -> QPainterPath:
        text_painter_path = QPainterPath()
        text_painter_path.addText(x, y, self.font(), self.text())
        return text_painter_path

    def draw_blur(self, painter: QPainter, text_path: QPainterPath, outline_color: QColor, outline_width: int) -> None:
        range_width = range(outline_width, outline_width + self.cfg.outline_blur)
        for width in range_width:
            if width == min(range_width):
                alpha = 200
            else:
                alpha = (max(range_width) - width) / max(range_width) * 200
                alpha = int(alpha)

            blur_color = QColor(outline_color.red(), outline_color.green(), outline_color.blue(), alpha)
            blur_brush = QBrush(blur_color, Qt.SolidPattern)
            blur_pen = QPen(blur_brush, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

            painter.setPen(blur_pen)
            painter.drawPath(text_path)

    def draw_outline(self, painter: QPainter, text_path: QPainterPath, outline_color: QColor,
                     outline_width: int) -> None:
        outline_color = QColor(outline_color.red(), outline_color.green(), outline_color.blue(), 255)
        outline_brush = QBrush(outline_color, Qt.SolidPattern)
        outline_pen = QPen(outline_brush, outline_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(outline_pen)
        painter.drawPath(text_path)

    def draw_text(self, painter: QPainter, x: int, y: int) -> None:
        color = self.palette().color(QPalette.Text)
        painter.setPen(color)
        painter.drawText(x, y, self.text())

    def paintEvent(self, evt: QPaintEvent):
        self.draw_text_and_outline()

    def resizeEvent(self, *args):
        self.setFixedSize(
            self.fontMetrics().width(self.text()),
            self.fontMetrics().height() + self.cfg.outline_bottom_padding + self.cfg.outline_top_padding
        )

    def sizeHint(self):
        return QSize(self.fontMetrics().width(self.text()), self.fontMetrics().height())


class HighlightableLabel(QLabel):
    def __init__(self, text: str, config):
        super().__init__(text)
        self.setMouseTracking(True)
        self.cfg = config
        self.word = text
        self.is_highlighting = False

        self.setStyleSheet('background: transparent; color: transparent;')

    def highlight(self, color, underline_width):
        color = QColor(color)
        color = QColor(color.red(), color.green(), color.blue(), 200)
        painter = QPainter(self)

        if self.cfg.is_hover_underline:
            font_metrics = QFontMetrics(self.font())
            text_width = font_metrics.width(self.word)
            text_height = font_metrics.height()

            brush = QBrush(color)
            pen = QPen(brush, underline_width, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(0, text_height - underline_width, text_width, text_height - underline_width)

        if self.cfg.is_hover_highlight:
            x = y = 0
            y += self.fontMetrics().ascent()

            painter.setPen(color)
            painter.drawText(x, y + self.cfg.outline_top_padding - self.cfg.outline_bottom_padding, self.word)

    def paintEvent(self, evt: QPaintEvent):
        if self.is_highlighting:
            self.highlight(self.cfg.hover_color, self.cfg.hover_underline_thickness)

    def resizeEvent(self, event):
        text_height = self.fontMetrics().height()
        text_width = self.fontMetrics().width(self.word)

        self.setFixedSize(text_width, text_height + self.cfg.outline_bottom_padding + self.cfg.outline_top_padding)

    def enterEvent(self, event):
        self.is_highlighting = True
        self.repaint()

    def leaveEvent(self, event):
        self.is_highlighting = False
        self.repaint()
