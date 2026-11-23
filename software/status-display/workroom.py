"""One-bit room scene with layered perspective and Codex-driven animation."""

from functools import lru_cache
import math
from pathlib import Path
import time

from PIL import Image, ImageDraw, ImageFont

from codex_activity import Activity


WIDTH, HEIGHT = 400, 240
INK, PAPER = 0, 255
BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


@lru_cache(maxsize=24)
def font(size, weight=400):
    face = ImageFont.truetype(str(Path(__file__).with_name("fonts") / "Inter.ttf"), size)
    face.set_variation_by_axes([min(32, max(14, size)), weight])
    return face


@lru_cache(maxsize=8)
def stipple(density):
    pattern = Image.new("1", (WIDTH, HEIGHT), PAPER)
    pattern.putdata([INK if BAYER[y % 4][x % 4] < density else PAPER
                     for y in range(HEIGHT) for x in range(WIDTH)])
    return pattern


def shade(image, polygon, density):
    mask = Image.new("1", image.size)
    ImageDraw.Draw(mask).polygon(polygon, fill=PAPER)
    image.paste(stipple(density), mask=mask)


def outline(draw, points, width=1):
    draw.line((*points, points[0]), fill=INK, width=width)


@lru_cache(maxsize=7)
def city(shift):
    image = Image.new("1", (107, 68), INK)
    draw = ImageDraw.Draw(image)
    for x, y in ((9, 13), (39, 15), (57, 8), (78, 35), (102, 21)):
        draw.point((x, y), fill=PAPER)
    draw.ellipse((74, 8, 92, 26), fill=PAPER)
    draw.ellipse((82, 3, 96, 20), fill=INK)
    for left, top, wide in ((-3, 51, 18), (15, 44, 14), (25, 52, 16), (40, 34, 16),
                            (57, 45, 11), (70, 39, 16), (88, 49, 25)):
        x = left + shift
        draw.rectangle((x, top, x + wide, 68), fill=PAPER)
        if top < 45:
            draw.line((x + 5, top - 5, x + 5, top), fill=PAPER)
        for a in range(x + 3, x + wide - 1, 5):
            for b in range(top + 4, 67, 7):
                draw.rectangle((a, b, a + 1, b + 2), fill=INK)
    return image


def walls():
    image = Image.new("1", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    # Floor joints converge behind the desk. The two walls meet at their base.
    shade(image, ((0, 34), (246, 34), (246, 146), (0, 162)), 1)
    shade(image, ((246, 34), (399, 34), (399, 128), (246, 146)), 3)
    shade(image, ((0, 162), (246, 146), (399, 128), (399, 239), (0, 239)), 2)
    draw.line((246, 35, 246, 146), fill=INK)
    draw.line((0, 162, 246, 146, 399, 128), fill=INK, width=2)
    draw.line((0, 168, 246, 151, 399, 134), fill=INK)
    for x in (-245, -172, -99, -26, 47, 120, 193, 266, 339, 412, 485):
        joint = round(243 + (x - 243) * .42)
        draw.line((joint, round(151 - (joint - 246) * .085), x, 240), fill=INK)
    for y in (193, 224):
        draw.line((0, y, 246, y - 16, 399, y - 34), fill=INK)
    rug = ((45, 190), (148, 181), (216, 209), (101, 226))
    shade(image, rug, 6)
    outline(draw, rug)
    outline(draw, ((53, 192), (147, 185), (207, 208), (102, 222)))

    # Window inset, reveal and sill. The sky image is composed later.
    draw.polygon(((18, 49), (140, 49), (146, 126), (23, 126)), fill=INK)
    draw.rectangle((18, 49, 139, 122), fill=PAPER, outline=INK, width=2)
    draw.polygon(((14, 122), (140, 122), (148, 127), (20, 128)), fill=PAPER, outline=INK)
    draw.line((21, 128, 147, 127), fill=INK, width=2)

    # Little gallery frame on the back wall.
    draw.rectangle((167, 55, 204, 83), fill=INK)
    draw.rectangle((165, 53, 202, 81), fill=PAPER, outline=INK)
    draw.ellipse((189, 58, 195, 64), fill=INK)
    draw.line((169, 75, 177, 64, 183, 71, 187, 66, 198, 75), fill=INK, width=2)

    # A shelf on the receding wall with books and a trailing plant.
    draw.polygon(((302, 66), (379, 55), (388, 58), (311, 70)), fill=PAPER, outline=INK)
    draw.polygon(((311, 70), (388, 58), (388, 62), (311, 74)), fill=INK)
    for x, y, h, w in ((308, 65, 18, 6), (316, 64, 21, 5), (324, 63, 15, 8), (334, 62, 19, 6)):
        draw.polygon(((x, y), (x + w, y - 1), (x + w, y - h - 1), (x, y - h)),
                     fill=PAPER, outline=INK)
        draw.line((x + 1, y - h + 5, x + w - 1, y - h + 4), fill=INK)
    draw.polygon(((352, 48), (368, 46), (365, 57), (355, 59)), fill=INK)
    draw.line((360, 48, 357, 38, 351, 35), fill=INK, width=2)
    draw.line((360, 48, 366, 38, 372, 35), fill=INK, width=2)
    draw.ellipse((346, 34, 354, 39), fill=INK)
    draw.ellipse((366, 33, 374, 38), fill=INK)
    draw.arc((361, 35, 378, 73), 268, 88, fill=INK, width=2)
    return image


def furniture():
    layer = Image.new("1", (WIDTH, HEIGHT), PAPER)
    mask = Image.new("1", layer.size)
    draw, shape = ImageDraw.Draw(layer), ImageDraw.Draw(mask)
    def face(points, density=0):
        shape.polygon(points, fill=PAPER)
        if density:
            shade(layer, points, density)
        else:
            draw.polygon(points, fill=PAPER)
        outline(draw, points)

    # Side cabinet and desk legs form the foreground layer.
    face(((301, 173), (346, 161), (367, 175), (323, 190)))
    face(((301, 173), (323, 190), (323, 228), (301, 209)), 7)
    face(((323, 190), (367, 175), (367, 212), (323, 228)), 3)
    for y in (201, 213):
        draw.line((324, y, 366, y - 15), fill=INK)
    for y in (194, 206, 219):
        draw.line((341, y, 349, y - 3), fill=INK, width=2)
    face(((159, 164), (168, 166), (168, 212), (159, 208)), 7)
    face(((215, 190), (225, 193), (225, 235), (215, 232)), 7)

    back_left, back_right, front_right, front_left = (160, 150), (293, 126), (369, 155), (226, 189)
    face((back_left, back_right, front_right, front_left))
    face((back_left, front_left, (226, 196), (160, 157)), 8)
    face((front_left, front_right, (369, 162), (226, 196)), 5)
    draw.line((170, 150, 292, 129, 356, 155), fill=INK)
    # The keyboard, mat and monitor stand share the desktop's perspective.
    draw.polygon(((186, 150), (244, 138), (279, 149), (219, 164)), fill=INK)
    draw.polygon(((194, 150), (242, 141), (267, 149), (218, 160)), fill=PAPER)
    draw.line((201, 150, 221, 157, 257, 149), fill=INK)
    draw.line((211, 149, 229, 155, 251, 150), fill=INK)
    draw.polygon(((265, 137), (289, 130), (314, 139), (286, 145)), fill=INK)
    draw.polygon(((281, 116), (294, 114), (294, 135), (281, 138)), fill=INK)
    # Mug silhouette and a separate right-hand accent.
    shape.ellipse((328, 127, 349, 151), fill=PAPER)
    draw.ellipse((340, 132, 350, 144), fill=PAPER, outline=INK, width=2)
    draw.rounded_rectangle((327, 128, 343, 150), radius=4, fill=INK)
    draw.ellipse((328, 126, 342, 132), fill=PAPER, outline=INK)
    return layer, mask


SCREEN_ORIGIN = (230, 80)
SCREEN_W, SCREEN_H = 88, 62
SCREEN_SLOPE = 10 / SCREEN_W


class Renderer:
    def __init__(self):
        self.room = walls()
        self.desk, self.desk_mask = furniture()
        self.mood = "idle"
        self.mood_started = None
        self.phase = 0.0
        self.last_frame = None
        self.speed = .24

    def screen(self, image, state, activity, elapsed):
        draw = ImageDraw.Draw(image)
        x, y = SCREEN_ORIGIN
        front = ((x - 4, y - 4), (x + SCREEN_W + 4, y - 15),
                 (x + SCREEN_W + 4, y + SCREEN_H - 6), (x - 4, y + SCREEN_H + 4))
        depth = ((x + 6, y - 9), (x + SCREEN_W + 14, y - 20),
                 (x + SCREEN_W + 14, y + SCREEN_H - 11))
        draw.polygon((front[0], depth[0], depth[1], depth[2], front[2], front[3]), fill=INK)
        draw.line((*depth, front[2]), fill=PAPER)
        draw.polygon(front, fill=PAPER, outline=INK, width=2)
        monitor = monitor_frame(state, min(activity.active_tasks, 9), int(elapsed * 5) % 20)
        image.paste(monitor, (x, y - 10), SCREEN_MASK)

    def character(self, draw, state, elapsed, delta):
        rate = {"thinking": .41, "working": 1.65, "replying": .93,
                "waiting": .32, "done": .72, "stopped": .19, "attention": .22, "sleep": .15}.get(state, .24)
        self.speed += (rate - self.speed) * (1 - math.exp(-delta * 7))
        self.phase += self.speed * math.tau * delta
        high = 2.6 if state in ("working", "done") else 1.35
        lift = 8 * abs(math.sin(elapsed * 5)) * math.exp(-elapsed) if state == "done" else 0
        cx = 132 + 2.6 * math.sin(self.phase * .72)
        cy = 150 + high * math.sin(self.phase) - lift
        wobble = math.sin(self.phase) * (1.5 if state == "working" else .5)
        # The floating orb occludes the rear wall. Its contact shadow sits on the floor.
        draw.ellipse((92, 192, 173, 207), fill=INK)
        for x in range(94, 172, 3):
            draw.point((x, 201), fill=PAPER)
        draw.ellipse((cx - 45 - wobble, cy - 45 + wobble, cx + 45 + wobble, cy + 45 - wobble), fill=PAPER)
        draw.ellipse((cx - 42 - wobble, cy - 42 + wobble, cx + 42 + wobble, cy + 42 - wobble), fill=INK)
        draw.arc((cx - 37, cy - 37, cx + 35, cy + 37), 198, 263, fill=PAPER, width=2)
        turn = math.sin(self.phase * .51)
        gaze = -10 if state == "waiting" else 5 if state == "working" else 0
        blink = max(0.0, 1 - abs((elapsed % 4.9) - 3.7) / .12)
        closed = state in ("sleep", "done")
        for dx, dy, length, width in ((6, -16, 16, 6), (25, -20, 13, 4)):
            x, y = cx + dx + gaze + 2 * turn, cy + dy + (7 if state == "sleep" else 0)
            if closed or blink > .78:
                draw.arc((x - 4, y - 3, x + 5, y + 4), 10, 170, fill=PAPER, width=2)
            else:
                tilt = math.radians(24 + 9 * turn)
                half = (length - width) * (1 - blink) / 2
                vx, vy = math.sin(tilt) * half, math.cos(tilt) * half
                draw.line((x - vx, y - vy, x + vx, y + vy), fill=PAPER, width=width)
                for sign in (-1, 1):
                    ex, ey = x + sign * vx, y + sign * vy
                    r = (width - 1) / 2
                    draw.ellipse((ex - r, ey - r, ex + r, ey + r), fill=PAPER)
        return cx, cy

    def render(self, snapshot, elapsed, now=None, preview=False, wall_time=None, activity=None, keyboard=False):
        now = time.monotonic() if now is None else now
        activity = activity or Activity()
        if self.mood_started is None or activity.state != self.mood:
            self.mood, self.mood_started = activity.state, now
        age = now - self.mood_started
        state = "sleep" if self.mood == "idle" and age > 40 and (snapshot.cpu_percent or 0) < 20 else self.mood
        delta = 0 if self.last_frame is None else min(.1, max(0, now - self.last_frame))
        self.last_frame = now
        image = self.room.copy()
        image.paste(city(round(3 * math.sin(elapsed * .51))), (24, 52))
        draw = ImageDraw.Draw(image)
        draw.line((73, 51, 73, 122), fill=PAPER, width=2)
        draw.line((75, 51, 75, 121), fill=INK, width=2)
        # The lamp reaches over the character, and the nearer desk crosses its silhouette.
        draw.line((190, 146, 202, 100, 218, 89), fill=INK, width=3)
        draw.polygon(((211, 86), (226, 79), (235, 92), (218, 100)), fill=INK)
        draw.line((219, 99, 234, 93), fill=PAPER, width=2)
        cx, cy = self.character(draw, state, age, delta)
        image.paste(self.desk, mask=self.desk_mask)
        self.screen(image, state, activity, elapsed)
        if state == "working":
            for key in range(2):
                y = 147 - 4 * abs(math.sin(elapsed * 11 + key * math.pi / 2))
                x = 201 + key * 13
                draw.ellipse((x - 5, y - 5, x + 6, y + 2), fill=INK, outline=PAPER)
        elif state in ("thinking", "waiting", "done"):
            marker = {"thinking": "…", "waiting": "?", "done": "✓"}[state]
            x, y = round(cx + 34), round(cy - 52 - 2 * math.sin(elapsed * 4))
            draw.rounded_rectangle((x - 10, y - 7, x + 10, y + 9), radius=4, fill=PAPER, outline=INK)
            draw.text((x, y), marker, font=font(11, 760), fill=INK, anchor="mm")
        if state != "sleep":
            for i in range(2):
                drift = (3 * elapsed + i * 4) % 9
                x, y = 332 + i * 5 + math.sin(elapsed * 2 + i), 124 - drift
                draw.line((x, y, x + 1, y - 3), fill=INK)
        self.header(draw, wall_time, keyboard, preview)
        return image

    @staticmethod
    def header(draw, wall_time, keyboard, preview):
        draw.rectangle((0, 0, WIDTH - 1, 33), fill=PAPER)
        draw.line((0, 33, WIDTH - 1, 33), fill=INK)
        draw.text((14, 12), "Makit Compute", font=font(14, 750), fill=INK, anchor="lt")
        if preview or keyboard:
            draw.text((139, 16), "Preview" if preview else "Ctrl+Alt+T", font=font(9, 650), fill=INK, anchor="lt")
        clock = time.strftime("%H:%M", time.localtime(time.time() if wall_time is None else wall_time))
        draw.text((385, 12), clock, font=font(14, 700), fill=INK, anchor="rt")


def skew_screen(image):
    # Convert the screen's horizontal coordinates to the desk's oblique plane.
    return image.transform((SCREEN_W, SCREEN_H + 10), Image.Transform.AFFINE,
                           (1, 0, 0, SCREEN_SLOPE, 1, -10), resample=Image.Resampling.NEAREST)


SCREEN_MASK = skew_screen(Image.new("1", (SCREEN_W, SCREEN_H), PAPER))


@lru_cache(maxsize=128)
def monitor_frame(state, active_tasks, tick):
    display = Image.new("1", (SCREEN_W, SCREEN_H), INK)
    draw = ImageDraw.Draw(display)
    labels = {"idle": "Ready", "thinking": "Thinking", "working": "Working", "replying": "Replying",
              "waiting": "Needs you", "done": "Done", "attention": "Attention", "stopped": "Stopped",
              "sleep": "Resting"}
    draw.text((7, 6), "Codex", font=font(10, 750), fill=PAPER, anchor="lt")
    if active_tasks > 1:
        draw.text((81, 7), f"×{active_tasks}", font=font(9, 700), fill=PAPER, anchor="rt")
    draw.line((7, 19, 80, 19), fill=PAPER)
    draw.text((7, 25), labels[state], font=font(13, 750), fill=PAPER, anchor="lt")
    if state == "done":
        draw.line((11, 49, 16, 54, 26, 44), fill=PAPER, width=2)
    elif state in ("working", "replying", "thinking"):
        for i, size in enumerate((28, 41, 17)):
            y = 43 + 5 * i
            length = size + (tick * (i + 2)) % 16
            draw.line((8, y, 8 + length, y), fill=PAPER)
        draw.rectangle((70, 44 + tick % 10, 76, 46 + tick % 10), fill=PAPER)
    elif state == "sleep":
        draw.ellipse((8, 43, 20, 55), fill=PAPER)
        draw.ellipse((14, 40, 23, 52), fill=INK)
    else:
        draw.line((8, 50, 13, 53, 8, 56), fill=PAPER)
        if tick % 8 < 5:
            draw.line((17, 56, 24, 56), fill=PAPER)
    return skew_screen(display)
