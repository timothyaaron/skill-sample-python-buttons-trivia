"""
Basic Animation Helper Library
"""

# //logger = require('./logger.js');

COLORS = {
    "white": "ffffff",
    "red": "ff0000",
    "orange": "ff3300",
    "green": "00ff00",
    "dark green": "004411",
    "blue": "0000ff",
    "light blue": "00a0b0",
    "purple": "4b0098",
    "yellow": "ffd400",
    "black": "000000",
}


class ColorHelper:
    @staticmethod
    def get_color(color):
        return COLORS[color.lower()]

    @staticmethod
    def validate_color(color):
        if color[:2] == '0x':
            return color[2:]
        elif color[0] == '#':
            return color[1:]
        else:
            return COLORS[color.lower()]


class BasicAnimations:
    @staticmethod
    def solid(cycles, color, duration):
        return [{
            "repeat": cycles,
            "target_lights": ["1"],
            "sequence": [
                {
                    "duration_ms": duration,
                    "blend": False,
                    "color": ColorHelper.validate_color(color),
                }
            ]
        }]

    @staticmethod
    def fade_in(cycles, color, duration):
        return [{
            "repeat": cycles,
            "target_lights": ["1"],
            "sequence": [
                {
                    "duration_ms": 1,
                    "blend": True,
                    "color": "000000"
                },
                {
                    "duration_ms": duration,
                    "blend": True,
                    "color": ColorHelper.validate_color(color)
                }
            ]
        }]

    @staticmethod
    def fade_out(cycles, color, duration):
        return [{
            "repeat": cycles,
            "target_lights": ["1"],
            "sequence": [
                {
                    "duration_ms": duration,
                    "blend": True,
                    "color": ColorHelper.validate_color(color)
                }, {
                    "duration_ms": 1,
                    "blend": True,
                    "color": "000000"
                }
            ]
        }]

    @staticmethod
    def cross_fade(cycles, color_one, color_two, duration_one, duration_two):
        return [{
            "repeat": cycles,
            "target_lights": ["1"],
            "sequence": [
                {
                    "duration_ms": duration_one,
                    "blend": True,
                    "color": ColorHelper.validate_color(color_one)
                }, {
                    "duration_ms": duration_two,
                    "blend": True,
                    "color": ColorHelper.validate_color(color_two)
                }
            ]
        }]

    @staticmethod
    def breathe(cycles, color, duration):
        return [{
            "repeat": cycles,
            "target_lights": ["1"],
            "sequence": [
                {
                    "duration_ms": 1,
                    "blend": True,
                    "color": "000000"
                },
                {
                    "duration_ms": duration,
                    "blend": True,
                    "color": ColorHelper.validate_color(color)
                },
                {
                    "duration_ms": 300,
                    "blend": True,
                    "color": ColorHelper.validate_color(color)
                },
                {
                    "duration_ms": 300,
                    "blend": True,
                    "color": "000000"
                }
            ]
        }]

    @staticmethod
    def blink(cycles, color):
        return [{
            "repeat": cycles,
            "target_lights": ["1"],
            "sequence": [
                {
                    "duration_ms": 500,
                    "blend": False,
                    "color": ColorHelper.validate_color(color)
                },
                {
                    "duration_ms": 500,
                    "blend": False,
                    "color": "000000"
                }
            ]
        }]

    @staticmethod
    def flip(cycles, color_one, color_two, duration_one, duration_two):
        return [{
            "repeat": cycles,
            "target_lights": ["1"],
            "sequence": [
                {
                    "duration_ms": duration_one,
                    "blend": False,
                    "color": ColorHelper.validate_color(color_one)
                },
                {
                    "duration_ms": duration_two,
                    "blend": False,
                    "color": ColorHelper.validate_color(color_two)
                }
            ]
        }]

    @staticmethod
    def pulse(cycles, color_one, color_two):
        return [{
            "repeat": cycles,
            "target_lights": ["1"],
            "sequence": [
                {
                    "duration_ms": 500,
                    "blend": True,
                    "color": ColorHelper.validate_color(color_one)
                },
                {
                    "duration_ms": 1000,
                    "blend": True,
                    "color": ColorHelper.validate_color(color_two)
                }
            ]
        }]


class ComplexAnimations:
    @staticmethod
    def answer(correct_color, baseline_color, duration):
        # blink correct color for 3 seconds
        sequence = [
            {
                "duration_ms": 500,
                "color": ColorHelper.validate_color(correct_color),
                "blend": False
            },
            {
                "duration_ms": 500,
                "color": ColorHelper.validate_color('black'),
                "blend": False
            }
        ] * 3

        sequence += [{
            "duration_ms": duration,
            "color": ColorHelper.validate_color(baseline_color),
            "blend": False
        }]

        return [{
            "repeat": 1,
            "target_lights": ["1"],
            "sequence": sequence
        }]

    @staticmethod
    def spectrum(cycles, colors):
        sequence = [
            {
                "duration_ms": 400,
                "color": ColorHelper.validate_color(c),
                "blend": True
            } for c in colors
        ]

        return [{
            "repeat": cycles,
            "target_lights": ["1"],
            "sequence": sequence
        }]
