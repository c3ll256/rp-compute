#!/usr/bin/env python3
"""Animated system companion for the rp-compute 400x240 Memory LCD."""

import argparse
from dataclasses import dataclass, replace
from functools import lru_cache
import logging
import math
from pathlib import Path
import signal
import sys
import threading
import time

from PIL import Image, ImageDraw, ImageFont

from telemetry import Snapshot, SystemMonitor
from hermes_display.bridge import Activity, ActivityMonitor


LOG = logging.getLogger("rp-status")
WIDTH, HEIGHT = 400, 240


@lru_cache(maxsize=16)
def font(size, weight=400):
    face = ImageFont.truetype(str(Path(__file__).with_name("fonts") / "Inter.ttf"), size)
    face.set_variation_by_axes([min(32, max(14, size)), weight])
    return face


def percent(used, total):
    if used is None or not total:
        return None
    return min(100, max(0, used / total * 100))


ACTIVITY_LABELS = {
    "disconnected": ("Connect Hermes", "Waiting for agent"),
    "idle": ("Ready", "Waiting for a task"),
    "thinking": ("Thinking", "Model request"),
    "responding": ("Replying", "Preparing response"),
    "tool": ("Using tools", "Running a tool"),
    "waiting": ("Needs you", "Your input is needed"),
    "retrying": ("Retrying", "Model request"),
    "recovering": ("Recovering", "Handling a tool or API error"),
    "done": ("Done", "Task complete"),
    "error": ("Failed", "Task ended with an error"),
    "stopped": ("Stopped", "Task interrupted"),
}

ACTIVITY_MOODS = {
    "disconnected": "ALL GOOD", "idle": "ALL GOOD", "thinking": "COMPUTING",
    "responding": "FOCUSED", "tool": "FOCUSED", "waiting": "AWAITING INPUT",
    "retrying": "CHECKING", "recovering": "CHECKING", "done": "DONE",
    "error": "TASK ERROR", "stopped": "OFFLINE",
}


def mood_for(snapshot, now, previous=None):
    if not snapshot.sampled_at or now - snapshot.sampled_at > 5:
        return "CHECKING"
    if snapshot.cpu_percent is None or snapshot.memory_total is None or snapshot.temperature is None:
        return "CHECKING"
    if snapshot.temperature >= (70 if previous == "WARM" else 75):
        return "WARM"
    if (percent(snapshot.memory_used, snapshot.memory_total) or 0) >= (85 if previous == "MEMORY FULL" else 90):
        return "MEMORY FULL"
    if (percent(snapshot.disk_used, snapshot.disk_total) or 0) >= (85 if previous == "DISK FULL" else 90):
        return "DISK FULL"
    if not snapshot.address:
        return "OFFLINE"
    if snapshot.cpu_percent >= (82 if previous == "BUSY" else 90):
        return "BUSY"
    if snapshot.cpu_percent >= (55 if previous == "FOCUSED" else 70):
        return "FOCUSED"
    network_rate = (snapshot.receive_rate or 0) + (snapshot.transmit_rate or 0)
    if network_rate >= (96 if previous == "TRANSFER" else 256) * 1024:
        return "TRANSFER"
    if snapshot.cpu_percent >= (20 if previous == "COMPUTING" else 30):
        return "COMPUTING"
    return "ALL GOOD"


class MoodController:
    """Debounce telemetry changes and remember short-lived recovery feedback."""

    def __init__(self):
        self.current = None
        self.pending = None
        self.pending_since = 0
        self.quiet_since = None
        self.celebrate_until = 0

    def update(self, snapshot, now):
        candidate = mood_for(snapshot, now, self.current)
        network_rate = (snapshot.receive_rate or 0) + (snapshot.transmit_rate or 0)
        quiet_limit = 12 if self.current == "DROWSY" else 8
        quiet = (candidate == "ALL GOOD" and snapshot.cpu_percent < quiet_limit
                 and network_rate < 16 * 1024)
        if quiet:
            if self.quiet_since is None:
                self.quiet_since = now
            if self.current == "DROWSY" or now - self.quiet_since >= 30:
                candidate = "DROWSY"
        else:
            self.quiet_since = None

        if self.current is None:
            self.current = candidate
        if candidate == self.current:
            self.pending = None
        else:
            if candidate != self.pending:
                self.pending = candidate
                self.pending_since = now
            urgent = candidate in ("WARM", "MEMORY FULL", "DISK FULL", "CHECKING")
            if urgent or now - self.pending_since >= 2:
                recovering = self.current in (
                    "COMPUTING", "FOCUSED", "BUSY", "TRANSFER", "OFFLINE",
                    "WARM", "MEMORY FULL", "DISK FULL",
                )
                self.celebrate_until = now + 3 if candidate == "ALL GOOD" and recovering else 0
                self.current = candidate
                self.pending = None
        if self.current == "ALL GOOD" and now < self.celebrate_until:
            return "DONE"
        return self.current


@dataclass(frozen=True)
class Motion:
    bob: float = 1.2
    speed: float = 0.23
    sway: float = 0
    squash: float = 0.5
    tilt: float = 4
    gaze: float = 2
    look_down: float = 0
    eye_scale: float = 1
    eye_width: float = 1
    blink_period: float = 5.4
    eye_angle: float = 25
    effect: str = ""


MOTIONS = {
    "ALL GOOD": Motion(),
    "COMPUTING": Motion(bob=2, speed=0.45, sway=1.5, tilt=11, gaze=5, effect="thinking"),
    "FOCUSED": Motion(bob=2.5, speed=1.5, sway=2.5, squash=1.3, tilt=9,
                      gaze=5, eye_scale=0.82, blink_period=3.5, effect="work"),
    "BUSY": Motion(bob=4, speed=2.2, sway=4, squash=2, tilt=13,
                   gaze=7, eye_scale=0.68, blink_period=2.8, effect="work"),
    "TRANSFER": Motion(bob=1.5, speed=0.65, tilt=5, gaze=4, effect="transfer"),
    "DROWSY": Motion(bob=0.7, speed=0.12, tilt=3, look_down=7,
                     eye_scale=0.65, eye_width=0.3, eye_angle=75, blink_period=8, effect="sleep"),
    "WARM": Motion(bob=1, speed=0.35, squash=2, tilt=6, look_down=6,
                   eye_scale=0.72, effect="heat"),
    "MEMORY FULL": Motion(bob=1.5, speed=0.55, tilt=8, eye_scale=1.12, effect="alert"),
    "DISK FULL": Motion(bob=1.5, speed=0.55, tilt=8, eye_scale=1.12, effect="alert"),
    "OFFLINE": Motion(bob=0.8, speed=0.18, tilt=9, look_down=11,
                      eye_scale=0.68, effect="offline"),
    "CHECKING": Motion(bob=1.2, speed=0.4, tilt=7, gaze=4, look_down=3, effect="connecting"),
    "DONE": Motion(bob=3, speed=1, tilt=8, eye_scale=0.6, eye_width=0.65,
                   eye_angle=70, effect="celebrate"),
    "AWAITING INPUT": Motion(bob=1, speed=0.3, gaze=0, eye_scale=1.1, effect="waiting"),
    "TASK ERROR": Motion(bob=0.6, speed=0.2, look_down=7, eye_scale=0.8, effect="alert"),
}


class Renderer:
    def __init__(self):
        self.previous_time = None
        self.controller = MoodController()
        self.mood = None
        self.mood_started = 0
        self.motion_values = None
        self.motion_phase = 0
        self.blink_phase = 0
        self.panel_key = None
        self.panel = None
        self.clock_value = None
        self.clock_image = None
        self.room = self.make_room()

    @staticmethod
    def make_room():
        """Fixed one-bit scenery is drawn once, with stationary texture."""
        image = Image.new("1", (WIDTH, HEIGHT), 255)
        draw = ImageDraw.Draw(image)
        # A textured dark wall and perspective floor enclose the room.
        draw.rectangle((8, 40, 218, 181), fill=0)
        for y in range(44, 150, 6):
            for x in range(12 + (y // 6 % 2) * 3, 216, 9):
                draw.point((x, y), fill=255)
        draw.line((124, 41, 124, 144), fill=255)
        draw.polygon(((8, 153), (124, 142), (218, 157), (218, 181), (8, 181)), fill=255)
        draw.line((8, 153, 124, 142, 218, 157), fill=0, width=2)
        for x in (-80, -16, 48, 112, 176, 240, 304):
            edge_x = min(218, max(8, x))
            edge_y = round(144 + 37 * (edge_x - 124) / (x - 124))
            draw.line((124, 144, edge_x, edge_y), fill=0)
        for points in ((8, 160, 124, 151, 218, 164),
                       (8, 173, 124, 164, 218, 176)):
            draw.line(points, fill=0)

        # Curtains frame a city window with lit windows and a crescent moon.
        draw.rectangle((17, 45, 112, 113), fill=255)
        draw.rectangle((20, 48, 109, 109), outline=0)
        for y in range(49, 88, 5):
            for x in range(23 + (y // 5 % 2) * 2, 107, 5):
                draw.point((x, y), fill=0)
        draw.ellipse((83, 53, 95, 65), fill=0)
        draw.ellipse((88, 50, 98, 61), fill=255)
        for left, top, right in ((21, 93, 27), (29, 84, 41), (43, 96, 53),
                                 (55, 79, 70), (72, 90, 82), (84, 83, 96),
                                 (98, 96, 109)):
            draw.rectangle((left, top, right, 107), fill=0)
            for x in range(left + 3, right - 1, 5):
                for y in range(top + 5, 105, 7):
                    draw.point((x, y), fill=255)
        draw.line((60, 45, 60, 109), fill=0, width=3)
        draw.line((13, 109, 111, 109), fill=0, width=3)
        draw.line((13, 114, 115, 114), fill=255, width=3)
        for points in (((9, 43), (23, 43), (18, 86), (21, 126), (9, 130)),
                       ((105, 43), (116, 43), (113, 86), (116, 125), (106, 123), (109, 86))):
            draw.polygon(points, fill=255)
        draw.line((14, 46, 12, 82, 14, 126), fill=0)
        draw.line((19, 46, 16, 84, 18, 123), fill=0)
        draw.line((112, 46, 111, 86, 113, 122), fill=0)
        draw.line((9, 87, 19, 87), fill=0, width=2)
        draw.line((108, 87, 115, 87), fill=0, width=2)

        # A wall calendar, filled bookshelf, and hanging plant.
        draw.rectangle((119, 46, 132, 66), fill=255)
        draw.rectangle((120, 47, 131, 51), fill=0)
        for x in (122, 126, 130):
            for y in (55, 59, 63):
                draw.point((x, y), fill=0)
        draw.rectangle((139, 65, 211, 68), fill=255)
        draw.line((143, 69, 143, 73, 149, 69), fill=255)
        draw.line((204, 69, 204, 73, 198, 69), fill=255)
        for x, top, width in ((144, 46, 7), (154, 42, 5), (162, 48, 8)):
            draw.rectangle((x, top, x + width, 64), fill=0, outline=255, width=1)
            draw.line((x + 2, top + 5, x + width - 2, top + 5), fill=255)
        draw.polygon(((174, 46), (179, 45), (184, 63), (179, 64)), fill=255)
        draw.polygon(((187, 57), (202, 57), (199, 64), (190, 64)), fill=255)

        # A desk lamp throws a stippled pool of light toward the keyboard.
        draw.polygon(((121, 85), (134, 87), (133, 135), (114, 137)), fill=255)
        for y in range(94, 135, 4):
            for x in range(117, 134, 4):
                draw.point((x, y), fill=0)
        draw.line((119, 133, 119, 102, 130, 80), fill=255, width=2)
        draw.polygon(((125, 78), (136, 82), (136, 88), (122, 84)), fill=0, outline=255)

        # The rug and cabinet sit on the floor beneath the desk.
        draw.polygon(((17, 167), (74, 162), (112, 174), (54, 180)), fill=0)
        draw.line((24, 168, 73, 165, 103, 174, 54, 177, 24, 168), fill=255)
        for x in range(32, 91, 8):
            draw.line((x, 169, x + 10, 173), fill=255)
        draw.rectangle((171, 153, 198, 179), fill=0, outline=255)
        for y in (160, 169):
            draw.line((175, y, 194, y), fill=255)
            draw.line((182, y - 3, 187, y - 3), fill=255)

        desk = ((90, 148), (163, 129), (216, 147), (141, 173))
        draw.polygon(desk, fill=255)
        draw.line((*desk, desk[0]), fill=0, width=2)
        draw.line((91, 151, 140, 178, 216, 152, 216, 147), fill=0, width=2)
        draw.line((142, 178, 142, 182), fill=0, width=3)
        draw.line((211, 154, 211, 179), fill=0, width=3)
        for x in range(111, 142, 5):
            draw.line((x, 160 + (x - 111) // 2, x, 162 + (x - 111) // 2), fill=0)
        draw.polygon(((118, 147), (160, 137), (180, 144), (138, 156)), fill=0)
        for row in range(3):
            draw.line((125 + row * 4, 147 + row * 2,
                       158 + row * 4, 139 + row * 2), fill=255)
        draw.ellipse((190, 138, 202, 145), outline=0, width=2)
        draw.rectangle((188, 134, 196, 143), fill=0)
        draw.ellipse((188, 132, 196, 136), fill=0)
        draw.line((190, 134, 194, 134), fill=255)

        # The monitor content is filled on each frame to reflect activity.
        draw.line((180, 124, 180, 134), fill=0, width=3)
        draw.polygon(((170, 136), (181, 132), (192, 136), (181, 140)), fill=0)
        draw.rounded_rectangle((137, 80, 214, 128), radius=4, fill=255)
        draw.rounded_rectangle((139, 82, 212, 126), radius=3, fill=0)
        draw.rectangle((144, 87, 207, 120), fill=255)
        draw.point((176, 123), fill=255)
        # A small desk fan is animated along with the companion.
        draw.line((126, 121, 126, 132), fill=0, width=2)
        draw.line((120, 133, 132, 133), fill=0, width=2)
        draw.ellipse((117, 102, 135, 120), fill=255, outline=0, width=2)
        draw.line((226, 44, 226, 190), fill=0)
        return image

    @staticmethod
    def wrapped_text(draw, text, x, y, face, width, lines=2):
        remaining = text
        for line in range(lines):
            part = remaining
            while part and draw.textlength(part, font=face) > width:
                part = part[:-1]
            if len(part) < len(remaining) and " " in part:
                part = part.rsplit(" ", 1)[0]
            if line == lines - 1 and len(part) < len(remaining):
                while part and draw.textlength(part + "...", font=face) > width:
                    part = part[:-1]
                part += "..."
            draw.text((x, y + line * (face.size + 4)), part, font=face, fill=0, anchor="lt")
            remaining = remaining[len(part):].lstrip()
            if not remaining:
                break

    @staticmethod
    def gauge(draw, x, label, value, maximum=100, suffix="%", warning=False):
        draw.text((x, 210), label, font=font(9, 650), fill=255, anchor="lt")
        text = "--" if value is None else f"{value:.0f}{suffix}"
        draw.text((x + 78, 210), text, font=font(9, 650), fill=255, anchor="rt")
        draw.rectangle((x, 224, x + 78, 229), outline=255)
        if value is not None:
            count = round(min(1, max(0, value / maximum)) * 10)
            for index in range(count):
                left = x + 2 + index * 7.5
                draw.rectangle((round(left), 226, round(left + 4), 227), fill=255)
        if warning:
            draw.line((x, 233, x + 78, 233), fill=255, width=2)

    def make_panel(self, snapshot, stale, preview, activity, now):
        image = self.room.copy()
        draw = ImageDraw.Draw(image)
        title = "Makit Compute / Preview" if preview else "Makit Compute"
        draw.text((12, 12), title, font=font(14, 750), fill=0, anchor="lt")
        if not preview:
            draw.ellipse((136, 16, 142, 22), outline=0,
                         fill=255 if activity.state == "disconnected" else 0)
        draw.line((12, 33, 387, 33), fill=0, width=2)
        heading, detail = ACTIVITY_LABELS[activity.state]
        if activity.state == "tool":
            detail = activity.tool or detail
        if activity.state == "waiting":
            detail = {"approval": "Approval needed", "sudo": "Password needed"}.get(activity.waiting_kind, detail)
        self.wrapped_text(draw, heading, 241, 49, font(23, 780), 146)
        self.wrapped_text(draw, detail, 241, 111, font(11, 650), 146)
        if activity.started:
            end = activity.changed if activity.state in ("done", "error", "stopped") else now
            elapsed = max(0, int(end - activity.started))
            minutes, seconds = divmod(elapsed, 60)
            hours, minutes = divmod(minutes, 60)
            duration = f"{hours}h {minutes:02d}m" if hours else f"{minutes:02d}:{seconds:02d}"
            draw.text((241, 151), duration, font=font(20, 750), fill=0, anchor="lt")
            draw.text((241, 177), f"{activity.tools_done} tools completed", font=font(10, 650), fill=0, anchor="lt")
        if activity.active_tasks > 1:
            draw.text((241, 193), f"{activity.active_tasks} tasks active", font=font(9, 650), fill=0, anchor="lt")

        address = "Metrics unavailable" if stale else (snapshot.address or "No network")
        self.wrapped_text(draw, address, 12, 190, font(10, 650), 207, lines=1)
        draw.rectangle((0, 205, 399, 239), fill=0)
        cpu = None if stale else snapshot.cpu_percent
        memory = None if stale else percent(snapshot.memory_used, snapshot.memory_total)
        disk = None if stale else percent(snapshot.disk_used, snapshot.disk_total)
        temperature = None if stale else snapshot.temperature
        self.gauge(draw, 12, "CPU", cpu)
        self.gauge(draw, 110, "RAM", memory, warning=memory is not None and memory >= 90)
        self.gauge(draw, 208, "TEMP", temperature, maximum=85, suffix="\N{DEGREE SIGN}C",
                   warning=temperature is not None and temperature >= 75)
        self.gauge(draw, 306, "DISK", disk, warning=disk is not None and disk >= 90)
        return image

    def character(self, draw, elapsed, mood, now):
        first_frame = self.previous_time is None
        delta = 0 if self.previous_time is None else min(0.1, max(0, now - self.previous_time))
        self.previous_time = now
        target = MOTIONS[mood]
        fields = ("bob", "speed", "sway", "squash", "tilt", "gaze", "look_down",
                  "eye_scale", "eye_width", "blink_period", "eye_angle")
        if self.motion_values is None:
            self.motion_values = {name: getattr(target, name) for name in fields}
        blend = 1 - math.exp(-delta * 6)
        for name in fields:
            self.motion_values[name] += (getattr(target, name) - self.motion_values[name]) * blend
        motion = self.motion_values
        if first_frame:
            self.motion_phase = elapsed * math.tau * motion["speed"]
            self.blink_phase = (elapsed / motion["blink_period"]) % 1
        self.motion_phase += delta * math.tau * motion["speed"]
        self.blink_phase = (self.blink_phase + delta / motion["blink_period"]) % 1
        phase = self.motion_phase
        breath = math.sin(phase)
        cx = 65 + motion["sway"] * math.sin(phase * 0.65)
        cy = 119 + motion["bob"] * breath
        squash = motion["squash"] * breath
        radius_x, radius_y = 40 + squash, 40 - squash
        age = now - self.mood_started
        if mood == "DONE":
            cy -= 7 * abs(math.sin(age * math.pi * 1.6)) * math.exp(-age * 0.55)
        draw.ellipse((round(cx - radius_x - 3), round(cy - radius_y - 3),
                      round(cx + radius_x + 3), round(cy + radius_y + 3)), fill=255)
        draw.ellipse((round(cx - radius_x), round(cy - radius_y),
                      round(cx + radius_x), round(cy + radius_y)), fill=0)

        # The supplied reference looks upward/right, with perspective-sized,
        # tilted capsule eyes set high on a circular face.
        pose = math.radians(motion["tilt"] * math.sin(phase * 0.55))
        gaze_x = motion["gaze"] * math.sin(phase * 0.8) ** 5
        gaze_y = motion["look_down"]
        blink = max(0, 1 - abs(self.blink_phase - 0.84) / (0.12 / motion["blink_period"]))
        for x_factor, y_factor, length, width in (
            (0.21, -0.42, 16, 6), (0.63, -0.50, 14, 4),
        ):
            local_x, local_y = radius_x * x_factor, radius_y * y_factor
            x = cx + local_x * math.cos(pose) - local_y * math.sin(pose) + gaze_x
            y = cy + local_x * math.sin(pose) + local_y * math.cos(pose) + gaze_y
            width = max(2, width * motion["eye_width"] * (1 - blink * 0.75))
            length = max(width, length * motion["eye_scale"] * (1 - blink * 0.9))
            angle = math.radians(motion["eye_angle"]) - pose
            half_segment = (length - width) / 2
            dx = math.sin(angle) * half_segment
            dy = math.cos(angle) * half_segment
            start = round(x + dx), round(y + dy)
            end = round(x - dx), round(y - dy)
            stroke = max(2, round(width))
            draw.line((start, end), fill=255, width=stroke)
            cap = (stroke - 1) / 2
            for point_x, point_y in (start, end):
                draw.ellipse((round(point_x - cap), round(point_y - cap),
                              round(point_x + cap), round(point_y + cap)), fill=255)
        self.effects(draw, target.effect, elapsed, age, cx, cy)

    def effects(self, draw, effect, elapsed, age, cx, cy):
        if effect == "work":
            for index in range(3):
                offset = (int(elapsed * 8) + index) % 3
                x, y = 115 + index * 7, 138 - offset * 3
                draw.line((x, y, x + 3, y - 4), fill=255, width=4)
                draw.line((x, y, x + 3, y - 4), fill=0, width=2)
        elif effect in ("thinking", "connecting"):
            for index in range(3):
                angle = elapsed * math.tau * 0.7 + index * math.tau / 3
                x = cx + 48 * math.cos(angle)
                y = cy + 26 * math.sin(angle)
                draw.ellipse((round(x - 2), round(y - 2), round(x + 2), round(y + 2)), fill=255)
                draw.ellipse((round(x - 1), round(y - 1), round(x + 1), round(y + 1)), fill=0)
        elif effect == "transfer":
            for index in range(3):
                progress = (elapsed * 0.9 + index / 3) % 1
                x = round(110 + progress * 24)
                draw.rectangle((x, 94, x + 3, 97), fill=0, outline=255)
                draw.rectangle((244 - x, 99, 247 - x, 102), fill=0, outline=255)
        elif effect == "heat":
            for x in (108, 116):
                points = [(round(x + 2 * math.sin(elapsed * 3 + step * 0.9)),
                           69 + step * 3) for step in range(6)]
                draw.line(points, fill=255, width=4)
                draw.line(points, fill=0, width=2)
        elif effect == "sleep":
            for index in range(2):
                drift = (elapsed * 4 + index * 9) % 18
                draw.text((110 + index * 8, 85 - drift), "z", font=font(11, 750),
                          fill=0, anchor="lt", stroke_width=1, stroke_fill=255)
        elif effect == "offline":
            draw.arc((112, 82, 128, 98), 200, 330, fill=255, width=4)
            draw.line((112, 98, 127, 82), fill=255, width=4)
            draw.arc((112, 82, 128, 98), 200, 330, fill=0, width=2)
            draw.line((112, 98, 127, 82), fill=0, width=2)
        elif effect == "alert":
            draw.text((119, 81), "!", font=font(18, 800), fill=0,
                      anchor="mt", stroke_width=1, stroke_fill=255)
        elif effect == "waiting":
            draw.rounded_rectangle((108, 74, 131, 94), radius=4, fill=255, outline=0)
            draw.text((120, 77), "?", font=font(14, 750), fill=0, anchor="mt")
        elif effect == "celebrate":
            for direction in (-1, 1):
                spread = min(1, age / 0.35)
                x = cx + direction * (43 + spread * 5)
                y = 82 - 3 * math.sin(age * 5)
                draw.ellipse((round(x - 5), round(y - 5), round(x + 5), round(y + 5)), fill=255)
                draw.line((round(x - 3), round(y), round(x + 3), round(y)), fill=0)
                draw.line((round(x), round(y - 3), round(x), round(y + 3)), fill=0)

    def room_activity(self, draw, elapsed, mood):
        # Leaf positions and fan speed follow continuous motion phases.
        sway = round(math.sin(elapsed * 0.8) * 2)
        draw.line((194, 57, 194 + sway, 43), fill=255, width=2)
        draw.ellipse((183 + sway, 44, 194 + sway, 49), fill=255)
        draw.ellipse((194 + sway, 40, 204 + sway, 45), fill=255)
        draw.ellipse((194 + sway, 49, 207 + sway, 53), fill=255)
        for blade in range(3):
            angle = self.motion_phase * 3 + blade * math.tau / 3
            x = 126 + 5 * math.cos(angle)
            y = 111 + 5 * math.sin(angle)
            draw.line((126, 111, round(x), round(y)), fill=0, width=3)
        draw.ellipse((124, 109, 128, 113), fill=0)
        if mood != "DROWSY":
            for index in range(2):
                drift = (elapsed * 3 + index * 5) % 10
                x = 191 + index * 4 + math.sin(elapsed * 2 + index)
                y = 130 - drift
                draw.line((round(x), round(y), round(x + 1), round(y - 2)), fill=255)

    def monitor_scene(self, draw, snapshot, elapsed, mood):
        """The desk monitor shares the companion's actual telemetry state."""
        if mood == "DROWSY":
            draw.ellipse((168, 92, 182, 106), fill=0)
            draw.ellipse((174, 89, 187, 102), fill=255)
            draw.line((160, 113, 190, 113), fill=0, width=2)
        elif mood in ("WARM", "MEMORY FULL", "DISK FULL", "TASK ERROR"):
            draw.polygon(((175, 91), (163, 112), (187, 112)), fill=0)
            draw.line((175, 98, 175, 105), fill=255, width=2)
            draw.rectangle((174, 108, 176, 109), fill=255)
        elif mood == "OFFLINE":
            draw.arc((165, 93, 185, 113), 200, 340, fill=0, width=2)
            draw.arc((170, 98, 180, 108), 200, 340, fill=0, width=2)
            draw.line((162, 114, 188, 91), fill=0, width=2)
        elif mood in ("CHECKING", "AWAITING INPUT"):
            for index in range(3):
                y = 103 - (3 if int(elapsed * 3) % 3 == index else 0)
                draw.rectangle((164 + index * 9, y, 167 + index * 9, y + 3), fill=0)
        elif mood == "DONE":
            draw.line((164, 102, 173, 110, 188, 94), fill=0, width=3)
        elif mood == "TRANSFER":
            for x, direction in ((166, -1), (185, 1)):
                draw.line((x, 94, x, 111), fill=0, width=2)
                tip = 94 if direction == -1 else 111
                draw.line((x - 4, tip - direction * 4, x, tip,
                           x + 4, tip - direction * 4), fill=0, width=2)
            offset = int(elapsed * 10) % 4
            draw.rectangle((150 + offset * 2, 98, 153 + offset * 2, 101), fill=0)
            draw.rectangle((198 - offset * 2, 106, 201 - offset * 2, 109), fill=0)
        else:
            speed = {"ALL GOOD": 0, "COMPUTING": 2, "FOCUSED": 4, "BUSY": 7}[mood]
            tick = int(elapsed * speed)
            for row, length in enumerate((29, 43, 21)):
                y = 92 + row * 6
                draw.line((149, y, 152, y + 2, 149, y + 4), fill=0)
                end = 157 + (length + tick * (row + 3)) % 42
                draw.line((157, y + 2, end, y + 2), fill=0, width=2)
            draw.rectangle((149, 113, 202, 117), outline=0)
            width = round(51 * min(100, max(0, snapshot.cpu_percent or 0)) / 100)
            if width:
                draw.rectangle((150, 114, 149 + width, 116), fill=0)

    def render(self, snapshot, elapsed, now=None, preview=False, wall_time=None, preview_mood=None, activity=None):
        now = time.monotonic() if now is None else now
        stale = not snapshot.sampled_at or now - snapshot.sampled_at > 5
        if preview_mood is not None and (not preview or preview_mood not in MOTIONS):
            raise ValueError("Preview states require preview mode and a known state")
        activity = activity or Activity()
        system_mood = self.controller.update(snapshot, now)
        mood = preview_mood or ACTIVITY_MOODS[activity.state]
        if activity.state == "tool" and activity.active_tasks > 1 and preview_mood is None:
            mood = "BUSY"
        if activity.state == "idle" and system_mood == "DROWSY" and preview_mood is None:
            mood = "DROWSY"
        if mood != self.mood:
            self.mood = mood
            self.mood_started = now
        panel_key = snapshot, stale, preview, activity, int(now)
        if self.panel_key != panel_key:
            self.panel = self.make_panel(snapshot, stale, preview, activity, now)
            self.panel_key = panel_key
        image = self.panel.copy()
        draw = ImageDraw.Draw(image)
        clock = time.strftime("%H:%M:%S", time.localtime(time.time() if wall_time is None else wall_time))
        if self.clock_value != clock:
            self.clock_image = Image.new("1", (104, 17), 255)
            ImageDraw.Draw(self.clock_image).text((104, 0), clock, font=font(13, 700),
                                                 fill=0, anchor="rt")
            self.clock_value = clock
        image.paste(self.clock_image, (283, 13))
        self.monitor_scene(draw, snapshot, elapsed, mood)
        self.character(draw, elapsed, mood, now)
        self.room_activity(draw, elapsed, mood)
        return image


def boot_frame(elapsed, ready=False, preview=False):
    """Wake the companion on a clean brand screen while the service starts."""
    image = Image.new("1", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(image)
    awake = min(1, max(0, (elapsed - 0.25) / 0.8))
    awake = awake * awake * (3 - 2 * awake)
    settle = math.exp(-elapsed * 5)
    cx, cy = 200, 89 + 2 * math.sin(elapsed * math.tau * 0.65)
    radius_x, radius_y = 38 - 2 * settle, 38 + 2 * settle
    draw.ellipse((round(cx - radius_x), round(cy - radius_y),
                  round(cx + radius_x), round(cy + radius_y)), fill=0)
    blink = max(0, 1 - abs(elapsed - 2.7) / 0.09)
    angle = math.radians(75 - awake * 50)
    for x_factor, y_factor, length, width in ((0.21, -0.42, 16, 6), (0.63, -0.50, 14, 4)):
        x = cx + radius_x * x_factor + 2 * math.sin(elapsed * 1.5) ** 5
        y = cy + radius_y * y_factor
        stroke = max(2, round(width * (0.4 + 0.6 * awake) * (1 - blink * 0.6)))
        length *= 0.55 + 0.45 * awake
        segment = max(0, (length * (1 - blink * 0.8) - stroke) / 2)
        dx, dy = math.sin(angle) * segment, math.cos(angle) * segment
        points = ((round(x - dx), round(y - dy)), (round(x + dx), round(y + dy)))
        draw.line(points, fill=255, width=stroke)
        cap = (stroke - 1) / 2
        for point_x, point_y in points:
            draw.ellipse((round(point_x - cap), round(point_y - cap),
                          round(point_x + cap), round(point_y + cap)), fill=255)
    draw.text((200, 148), "Makit Compute", font=font(22, 780), fill=0, anchor="mt")
    draw.text((200, 184), "Ready" if ready else "Starting up",
              font=font(11, 650), fill=0, anchor="mt")
    for index in range(3):
        x = 188 + index * 12
        active = ready or index == int(elapsed * 3) % 3
        draw.ellipse((x - 2, 207, x + 2, 211), outline=0, fill=0 if active else 255)
    if preview:
        draw.text((12, 226), "Preview", font=font(9, 650), fill=0, anchor="lt")
    return image


def preview(path, showcase=False, boot_seconds=None):
    """Synthetic metrics are explicitly marked in the rendered header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    renderer = Renderer()
    now = 100.0
    snapshot = Snapshot(
        hostname="makit-compute", sampled_at=now, cpu_percent=18,
        memory_used=920 * 1024**2, memory_total=3840 * 1024**2,
        temperature=46, disk_used=3 * 1024**3, disk_total=14 * 1024**3,
        uptime=37250, interface="eth0", address="192.168.50.83",
        receive_rate=3400, transmit_rate=1200,
    )
    if boot_seconds is not None:
        if path.suffix.lower() != ".gif":
            boot_frame(min(1.5, boot_seconds), preview=True).save(path)
            return
        frames = []
        for index in range(math.ceil((boot_seconds + 1) * 20)):
            elapsed = index / 20
            if elapsed < boot_seconds:
                image = boot_frame(elapsed, ready=elapsed >= max(1, boot_seconds - 0.6), preview=True)
            else:
                image = renderer.render(snapshot, elapsed, now, preview=True,
                                        activity=Activity(state="idle"), wall_time=0)
            frames.append(image)
        frames[0].save(path, save_all=True, append_images=frames[1:], duration=50,
                       loop=0, optimize=False, disposal=2)
        return
    if path.suffix.lower() != ".gif":
        renderer.render(snapshot, 0, now, preview=True,
                        activity=Activity(state="thinking", started=58, changed=100, active_tasks=1)).save(path)
        return
    frames = []
    wall_time = time.time()
    states = ("disconnected", "idle", "thinking", "tool", "waiting", "responding",
              "retrying", "recovering", "done", "error", "stopped", "idle")
    count = len(states) * 50 if showcase else 120
    for index in range(count):
        elapsed = index / 20
        state = states[index // 50] if showcase else ("thinking", "tool", "done")[index // 40]
        active = state not in ("idle", "disconnected", "done", "error", "stopped")
        activity = Activity(state=state, tool="web_search" if state == "tool" else "",
                            started=58 if state not in ("idle", "disconnected") else 0,
                            changed=now + index // 50 * 2.5, tools_done=3,
                            active_tasks=int(active), waiting_kind="approval")
        sample = replace(snapshot, sampled_at=now + elapsed, cpu_percent=32 if active else 6)
        frames.append(renderer.render(sample,
                                      elapsed, now + elapsed, preview=True,
                                      wall_time=wall_time + elapsed, activity=activity,
                                      preview_mood="DROWSY" if showcase and index // 50 == 11 else None))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=50,
                   loop=0, optimize=False, disposal=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fps", type=float, default=60)
    parser.add_argument("--boot-seconds", type=float, default=4,
                        help="startup animation duration, 0 disables it")
    parser.add_argument("--duration", type=float, help="stop after this many seconds")
    parser.add_argument("--interface", help="network interface, default follows the route")
    parser.add_argument("--activity-socket", default="/run/rp-compute/activity.sock",
                        help="local Unix datagram socket for the Hermes plugin")
    parser.add_argument("--preview", type=Path, help="save a synthetic PNG or animated GIF")
    parser.add_argument("--showcase", action="store_true", help="preview Hermes task states in a GIF")
    parser.add_argument("--boot-preview", action="store_true", help="preview the startup animation")
    args = parser.parse_args()
    if not math.isfinite(args.fps) or not 1 <= args.fps <= 60:
        parser.error("--fps must be between 1 and 60")
    if args.duration is not None and (not math.isfinite(args.duration) or args.duration <= 0):
        parser.error("--duration must be finite and positive")
    if not math.isfinite(args.boot_seconds) or args.boot_seconds < 0:
        parser.error("--boot-seconds must be finite and nonnegative")
    if args.boot_preview and (args.preview is None or args.showcase):
        parser.error("--boot-preview requires --preview and cannot combine with --showcase")
    if args.showcase and (args.preview is None or args.preview.suffix.lower() != ".gif"):
        parser.error("--showcase requires --preview with a .gif path")
    if args.preview:
        if args.preview.suffix.lower() not in (".png", ".gif"):
            parser.error("--preview must end with .png or .gif")
        preview(args.preview, args.showcase, args.boot_seconds if args.boot_preview else None)
        return 0

    # Reuse the driver that was verified on the physical LS027B7DH01A.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "display-test"))
    from display_test import Display

    stopped = threading.Event()
    for number in (signal.SIGINT, signal.SIGTERM):
        signal.signal(number, lambda *_: stopped.set())
    monitor = SystemMonitor(args.interface)
    activity_monitor = ActivityMonitor(args.activity_socket)
    display = None
    try:
        monitor.start()
        activity_monitor.start()
        display = Display(args.fps)
        display.start()
        renderer = Renderer()
        started = time.monotonic()
        next_report = 30.0
        next_frame = started
        previous_state = None
        while not stopped.is_set():
            now = time.monotonic()
            elapsed = now - started
            if args.duration is not None and elapsed >= args.duration:
                break
            snapshot = monitor.snapshot()
            activity = activity_monitor.snapshot()
            if elapsed < args.boot_seconds:
                ready = elapsed >= args.boot_seconds - 0.6 and mood_for(snapshot, now) != "CHECKING"
                image = boot_frame(elapsed, ready=ready)
                if previous_state is None:
                    LOG.info("Startup animation started, duration %.1f s", args.boot_seconds)
                    previous_state = "startup", None
            else:
                if previous_state == ("startup", None):
                    LOG.info("Startup animation complete")
                image = renderer.render(snapshot, elapsed, now, activity=activity)
                state = activity.state, renderer.mood
                if state != previous_state:
                    LOG.info("Hermes state %s, companion %s", *state)
                    previous_state = state
            display.show(image)
            if elapsed >= next_report:
                LOG.info("Refresh %.2f fps, %d frames, metrics age %.2f s, max COM gap %.4f s",
                         display.frames / (time.monotonic() - started), display.frames,
                         now - snapshot.sampled_at, display.max_com_gap)
                next_report += 30
            next_frame += 1 / args.fps
            after_render = time.monotonic()
            # Drop missed presentation slots while keeping uptime/duration accurate.
            if next_frame < after_render - 1 / args.fps:
                next_frame = after_render
            stopped.wait(max(0, next_frame - after_render))
        display.check()
        return 0
    except Exception:
        LOG.exception("Status display failed")
        return 1
    finally:
        try:
            if display is not None:
                display.close()
        finally:
            try:
                activity_monitor.close()
            finally:
                monitor.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    raise SystemExit(main())
