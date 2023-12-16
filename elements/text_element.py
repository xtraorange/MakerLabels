#Generally speaking, you will want to position the text element 25% lower, since the baseline starts 25% above the bottom of the element
from elements import Element
from reportlab.lib.units import inch
from Logger import Logger

class TextElement(Element):
    _attributes = {
        'text': (str, ""),
        'wrap': (bool, True),
        'auto_truncate': (bool, True),
        'font_size': (float, None),
        'font_color': (str, None),
        'font_name': (str, None),
        'line_gap': (float, 2),
        'descender_spacer': (float, .25),

    }

    def __init__(self, text):
        super().__init__()
        self.text = str(text)


    def _render_self(self, canvas):
        Logger.debug(f"Rendering text element: {self.text}")
        
        self.width = canvas.width
        self.height = canvas.height


        self.font_name = self.font_name if self.font_name else canvas.font_name
        self.font_color = self.font_color if self.font_color else canvas.fill_color

        canvas.save_style_state()
        canvas.set_font_name(self.font_name)
        canvas.set_fill_color(self.font_color)
        Logger.debug(f"Font Name: {self.font_name} and Color: {self.font_color}")

        if self.font_size == 'auto' or self.font_size is None:
            self.font_size = self._find_max_font_size_that_fits(canvas)

        canvas.set_font_size(self.font_size)
        
        if self.wrap:
            lines = self._wrap_text(canvas, self.text, self.font_size)
        else:
            lines = [self.text]

        if self.auto_truncate:
            lines = self._truncate_lines(canvas, lines)

        Logger.debug(f"Drawing Lines: {lines}")

        self._draw_lines(canvas, lines, canvas.width, canvas.height)
        canvas.restore_style_state()

    def _find_max_font_size_that_fits(self, canvas):
        Logger.debug("Finding maximum font size that fits")
        min_font_size = 1  # Minimum possible font size
        max_font_size = 200  # A reasonable upper limit for font size
        last_fitting_size = min_font_size

        while min_font_size <= max_font_size:
            mid_font_size = (min_font_size + max_font_size) // 2
            Logger.debug(f"Trying font size: {mid_font_size}")

            canvas.set_font_size(mid_font_size)
            if self.wrap:
                lines = self._wrap_text(canvas, self.text, mid_font_size)
            else:
                lines = [self.text]

            line_height = mid_font_size / 72 * inch  # Convert point size to inches
            total_height = len(lines) * (line_height + self.line_gap) - self.line_gap

            fits_in_width = all(canvas.stringWidth(line, self.font_name, mid_font_size) <= self.width for line in lines)
            fits_in_height = total_height <= self.height

            if fits_in_width and fits_in_height:
                last_fitting_size = mid_font_size
                min_font_size = mid_font_size + 1
            else:
                max_font_size = mid_font_size - 1

        Logger.debug(f"Final fitting font size: {last_fitting_size}")
        return last_fitting_size

    def _wrap_text(self, canvas, text, font_size):
        Logger.debug(f"Wrapping text with font size: {font_size}")
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            # Add a space if the line is not empty
            test_line = current_line + (" " if current_line else "") + word
            line_width = canvas.stringWidth(test_line, self.font_name, font_size)

            if line_width <= self.width:
                current_line = test_line
            else:
                # If the current line is not empty, append it to lines
                if current_line:
                    lines.append(current_line)
                current_line = word

        # Add the last line if it's not empty
        if current_line:
            lines.append(current_line)

        return lines

    def _truncate_lines(self, canvas, lines):
        Logger.debug("Truncating lines")
        truncated_lines = []
        for line in lines:
            while canvas.stringWidth(line, self.font_name, self.font_size) > self.width and len(line) > 0:
                line = line[:-1]
            truncated_lines.append(line)
        return truncated_lines


    def _draw_lines(self, canvas, lines, width, height):
        Logger.debug("Drawing lines")
        total_text_height = len(lines) * (self.font_size / 72 * inch + self.line_gap) - self.line_gap

        y_position = self.calculate_vertical_alignment(total_text_height, self.height, self.vertical_align)

        y_position += total_text_height

        descender_space = self.font_size * self.descender_spacer
        y_position += descender_space



        for line in lines:
            if y_position - self.font_size / 72 * inch < 0 and self.auto_truncate:
                break  # Stop drawing if we run out of vertical space

            text_width = canvas.stringWidth(line, self.font_name, self.font_size)

            x_position = self.calculate_horizontal_alignment(text_width, self.width, self.horizontal_align)

            y_position -= self.font_size / 72 * inch
            Logger.debug(f"Drawing line: {line} at ({x_position}, {y_position})")
            canvas.drawString(x_position, y_position, line)
            y_position -= self.line_gap
