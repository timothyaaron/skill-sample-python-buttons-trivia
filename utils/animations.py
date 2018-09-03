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
            "targetLights": ["1"],
            "sequence": [
                {
                    "durationMs": duration,
                    "blend": False,
                    "color": ColorHelper.validate_color(color),
                }
            ]
        }]

    @staticmethod
    def fade_in(cycles, color, duration):
        return [{
            "repeat": cycles,
            "targetLights": ["1"],
            "sequence": [
                {
                    "durationMs": 1,
                    "blend": True,
                    "color": "000000"
                },
                {
                    "durationMs": duration,
                    "blend": True,
                    "color": ColorHelper.validate_color(color)
                }
            ]
        }]

    @staticmethod
    def fade_out(cycles, color, duration):
        return [{
            "repeat": cycles,
            "targetLights": ["1"],
            "sequence": [
                {
                    "durationMs": duration,
                    "blend": True,
                    "color": ColorHelper.validate_color(color)
                }, {
                    "durationMs": 1,
                    "blend": True,
                    "color": "000000"
                }
            ]
        }]

    @staticmethod
    def cross_fade(cycles, color_one, color_two, duration_one, duration_two):
        return [{
            "repeat": cycles,
            "targetLights": ["1"],
            "sequence": [
                {
                    "durationMs": duration_one,
                    "blend": True,
                    "color": ColorHelper.validate_color(color_one)
                }, {
                    "durationMs": duration_two,
                    "blend": True,
                    "color": ColorHelper.validate_color(color_two)
                }
            ]
        }]

    @staticmethod
    def breathe(cycles, color, duration):
        return [{
            "repeat": cycles,
            "targetLights": ["1"],
            "sequence": [
                {
                    "durationMs": 1,
                    "blend": True,
                    "color": "000000"
                },
                {
                    "durationMs": duration,
                    "blend": True,
                    "color": ColorHelper.validate_color(color)
                },
                {
                    "durationMs": 300,
                    "blend": True,
                    "color": ColorHelper.validate_color(color)
                },
                {
                    "durationMs": 300,
                    "blend": True,
                    "color": "000000"
                }
            ]
        }]

    @staticmethod
    def blink(cycles, color):
        return [{
            "repeat": cycles,
            "targetLights": ["1"],
            "sequence": [
                {
                    "durationMs": 500,
                    "blend": False,
                    "color": ColorHelper.validate_color(color)
                },
                {
                    "durationMs": 500,
                    "blend": False,
                    "color": "000000"
                }
            ]
        }]

    @staticmethod
    def flip(cycles, color_one, color_two, duration_one, duration_two):
        return [{
            "repeat": cycles,
            "targetLights": ["1"],
            "sequence": [
                {
                    "durationMs": duration_one,
                    "blend": False,
                    "color": ColorHelper.validate_color(color_one)
                },
                {
                    "durationMs": duration_two,
                    "blend": False,
                    "color": ColorHelper.validate_color(color_two)
                }
            ]
        }]

    @staticmethod
    def pulse(cycles, color_one, color_two):
        return [{
            "repeat": cycles,
            "targetLights": ["1"],
            "sequence": [
                {
                    "durationMs": 500,
                    "blend": True,
                    "color": ColorHelper.validate_color(color_one)
                },
                {
                    "durationMs": 1000,
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
                "durationMs": 500,
                "color": ColorHelper.validate_color(correct_color),
                "blend": False
            },
            {
                "durationMs": 500,
                "color": ColorHelper.validate_color('black'),
                "blend": False
            }
        ] * 3

        sequence += [{
            "durationMs": duration,
            "color": ColorHelper.validate_color(baseline_color),
            "blend": False
        }]

        return [{
            "repeat": 1,
            "targetLights": ["1"],
            "sequence": sequence
        }]

    @staticmethod
    def spectrum(cycles, colors):
        sequence = [
            {
                "durationMs": 400,
                "color": ColorHelper.validate_color(c),
                "blend": True
            } for c in colors
        ]

        return [{
            "repeat": cycles,
            "targetLights": ["1"],
            "sequence": sequence
        }]
