from bitstring import BitArray
from random import shuffle
from pyDominoValueGenerator import Valid_Dominos
from datetime import datetime
from math import floor
import logging
import sys
from fpdf import FPDF

# Domino colors
DOMINO_FOREGROUND = (255, 255, 255)  # white
DOMINO_BACKGROUND = (0, 0, 0)  # black


def draw_rounded_rect(pdf, x, y, w, h, r):
    """
    Draw a rectangle with rounded corners.
    x, y: top-left corner
    w, h: width and height
    r: corner radius
    """
    pdf.set_fill_color(*DOMINO_BACKGROUND)
    # Draw four corner circles (quarter circles)
    pdf.ellipse(x, y, 2 * r, 2 * r, style='F')  # Top-left
    pdf.ellipse(x + w - 2 * r, y, 2 * r, 2 * r, style='F')  # Top-right
    pdf.ellipse(x, y + h - 2 * r, 2 * r, 2 * r, style='F')  # Bottom-left
    pdf.ellipse(x + w - 2 * r, y + h - 2 * r, 2 * r, 2 * r, style='F')  # Bottom-right

    # Draw rectangles to fill sides
    pdf.rect(x + r, y, w - 2 * r, h, style='F')  # horizontal central rect
    pdf.rect(x, y + r, w, h - 2 * r, style='F')  # vertical central rect


class Margin:
    Top = 0.0
    Left = 0.0
    Right = 0.0
    Bottom = 0.0


class Paper:
    Height = 0.0
    Width = 0.0
    Margin = Margin()
    Count = 0
    Center_Vertical = False
    Center_Horizontal = False
    X_ScaleFactor = 1.0
    Y_ScaleFactor = 1.0


class DominoPDF:
    MarginBorder = False

    RowSpacing = 3.0
    Page = Paper()
    VerificationScale = False
    Randomize = True
    PrintValues = False
    DebugFile = True
    RadiusCorners = False

    _units = "inch"
    _unit_scale = 1.0

    @property
    def Units(self):
        return self._units

    @Units.setter
    def Units(self, value):
        if value == "inch":
            self._unit_scale = 1.0
        elif value == "mm":
            self._unit_scale = 25.4
        elif value == "cm":
            self._unit_scale = 2.54
        else:
            self._unit_scale = 1.0
        self._units = value

    @property
    def DominoPadding(self):
        return 0.125 * self._unit_scale

    @property
    def DominoRadius(self):
        return 0.0625 * self._unit_scale

    @property
    def Pip_Padding(self):
        return 0.10 * self._unit_scale

    @property
    def Domino_Width(self):
        return 1.7 * self._unit_scale

    @property
    def Domino_Height(self):
        return 0.5 * self._unit_scale

    @property
    def CornerRadius(self):
        return 0.10 * self._unit_scale

    @property
    def Pip_Diameter(self):
        return 0.10 * self._unit_scale

    @property
    def Pip_Radius(self):
        return 0.05 * self._unit_scale

    def __place_domino(self, pdf: FPDF, x, y, value):
        # Draw domino background
        pdf.set_fill_color(*DOMINO_BACKGROUND)
        if self.RadiusCorners:
            draw_rounded_rect(pdf, x, y, self.Domino_Width, self.Domino_Height, self.CornerRadius)
        else:
            pdf.rect(x, y, self.Domino_Width, self.Domino_Height, style='F')

        self.drawValueText(pdf, value, x, y, self.Domino_Width, self.Domino_Height)

        # Draw pips
        DPips = BitArray(uint=int(value), length=12)
        BitRow = [DPips[:6], DPips[6:]]  # two rows
        for py in range(2):
            for px in range(8):
                if px == 0 or px == 7 or BitRow[py][px - 1]:
                    pip_x = x + self.Pip_Padding + self.Pip_Radius + (px * 2 * self.Pip_Diameter)
                    pip_y = y + self.Pip_Padding + self.Pip_Radius + (py * 2 * self.Pip_Diameter)
                    pdf.set_fill_color(*DOMINO_FOREGROUND)
                    pdf.ellipse(pip_x - self.Pip_Radius, pip_y - self.Pip_Radius,
                                self.Pip_Diameter, self.Pip_Diameter, style='F')

    def drawValueText(self, pdf, value, x, y, w, h):
        if self.PrintValues:
            # optional label in corner
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Courier", "", 6)
            pdf.text(x + 1.45, y + 0.60, "{:04d}".format(value))

    def __prepare_file(self, pdf: FPDF):
        if self.Randomize:
            shuffle(Valid_Dominos)

        work_width = self.Page.Width - (self.Page.Margin.Left + self.Page.Margin.Right)
        work_height = self.Page.Height - (self.Page.Margin.Top + self.Page.Margin.Bottom)

        pg_Num_Rows = 1 + floor((work_height - self.Domino_Height) / (self.Domino_Height + self.RowSpacing))
        pg_Num_Cols = 1 + floor((work_width - self.Domino_Width) / (self.Domino_Width + self.DominoPadding))

        x_offset = 0
        y_offset = 0
        if self.Page.Center_Horizontal:
            x_domino_space = (pg_Num_Cols * (self.Domino_Width + self.DominoPadding)) - self.DominoPadding
            x_offset = round((work_width - x_domino_space) / 2, 4)
        if self.Page.Center_Vertical:
            y_domino_space = (pg_Num_Rows * (self.Domino_Height + self.RowSpacing)) - self.RowSpacing
            y_offset = round((work_height - y_domino_space) / 2, 4)

        ValueIndex = 0
        ValueIndexMax = len(Valid_Dominos)

        for page in range(self.Page.Count):
            pdf.add_page()
            if self.MarginBorder:
                pdf.set_draw_color(0, 0, 255)
                pdf.rect(self.Page.Margin.Left, self.Page.Margin.Top,
                         self.Page.Width - self.Page.Margin.Left - self.Page.Margin.Right,
                         self.Page.Height - self.Page.Margin.Top - self.Page.Margin.Bottom)

            for py in range(pg_Num_Rows):
                for px in range(pg_Num_Cols):
                    DX = self.Page.Margin.Left + x_offset + (px * self.Domino_Width) + (px * self.DominoPadding)
                    DY = self.Page.Margin.Top + y_offset + (py * self.RowSpacing) + (py * self.Domino_Height)

                    if ValueIndex >= ValueIndexMax:
                        ValueIndex = 0
                        if self.Randomize:
                            shuffle(Valid_Dominos)

                    ValueIndex += 1
                    self.__place_domino(pdf, DX, DY, Valid_Dominos[ValueIndex])

    def SavePDF(self, filepath):
        pdf = FPDF(unit='in', format=(self.Page.Width, self.Page.Height))
        self.__prepare_file(pdf)
        pdf.output(filepath)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    testdoc = DominoPDF()
    testdoc.Units = "inch"
    testdoc.Page.Height = 11
    testdoc.Page.Width = 8.5
    testdoc.Page.Center_Vertical = True
    testdoc.Page.Center_Horizontal = True
    testdoc.Page.Margin.Top = 0.6
    testdoc.Page.Margin.Left = 0.6
    testdoc.Page.Margin.Right = 0.6
    testdoc.Page.Margin.Bottom = 0.6
    testdoc.Page.Count = 1
    testdoc.RowSpacing = 0.5
    testdoc.Randomize = True
    testdoc.RadiusCorners = True
    testdoc.PrintValues = True
    testdoc.MarginBorder = False
    filename = f"Output-{datetime.now().strftime('%Y%m%d-%H%M')}.pdf"
    testdoc.SavePDF(filename)
    print('Done.')
