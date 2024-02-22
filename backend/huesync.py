import os
from config import (
    logging,
    LED_PATH,
    IS_LED_SUPPORTED,
    IS_AYANEO_EC_SUPPORTED,
    SYS_VENDOR,
)
from ec import EC
import time
try:
    from wincontrols import WinControls
except:
    from .wincontrols import WinControls

class AyaJoystick:
    Left = 1
    Right = 2
    ALL = 3


class AyaLedPosition:
    Right = 1
    Bottom = 2
    Left = 3
    Top = 4


class Color:
    def __init__(self, r, g, b):
        self.R = r
        self.G = g
        self.B = b

    def hex(self):
        return f"{self.R:02x}{self.G:02x}{self.B:02x}"


class LedControl:
    @staticmethod
    def set_Color(color: Color, brightness: int = 100):
        if IS_LED_SUPPORTED:
            for x in range(2):
                with open(os.path.join(LED_PATH, "brightness"), "w") as f:
                    _brightness: int = brightness * 255 // 100
                    logging.debug(f"brightness={_brightness}")
                    f.write(str(_brightness))
                with open(os.path.join(LED_PATH, "multi_intensity"), "w") as f:
                    f.write(f"{color.R} {color.G} {color.B}")
                time.sleep(0.01)
        elif IS_AYANEO_EC_SUPPORTED:
            LedControl.set_aya_all_pixels(color, brightness)
        elif SYS_VENDOR == "GPD":
            LedControl.set_gpd_color(color, brightness)
    
    @staticmethod
    def set_gpd_color(color: Color, brightness: int = 100):
        try:
            wc = WinControls(disableFwCheck=True)
            color = Color(
                color.R * brightness // 100,
                color.G * brightness // 100,
                color.B * brightness // 100,
            )
            conf = ["ledmode=solid", f"colour={color.hex()}"]
            logging.debug(f"conf={conf}")
            if wc.loaded and wc.setConfig(conf):
                wc.writeConfig()
        except Exception as e:
            logging.error(e)

    @staticmethod
    def set_aya_all_pixels(color: Color, brightness: int = 100):

        color = Color(
            color.R * brightness // 100,
            color.G * brightness // 100,
            color.B * brightness // 100,
        )

        LedControl.set_aya_pixel(AyaJoystick.ALL, AyaLedPosition.Right, color)
        LedControl.set_aya_pixel(AyaJoystick.ALL, AyaLedPosition.Bottom, color)
        LedControl.set_aya_pixel(AyaJoystick.ALL, AyaLedPosition.Left, color)
        LedControl.set_aya_pixel(AyaJoystick.ALL, AyaLedPosition.Top, color)

        # AyaLed.set_pixel(Joystick.Right, LedPosition.Right, color)
        # AyaLed.set_pixel(Joystick.Right, LedPosition.Bottom, color)
        # AyaLed.set_pixel(Joystick.Right, LedPosition.Left, color)
        # AyaLed.set_pixel(Joystick.Right, LedPosition.Top, color)

    @staticmethod
    def set_aya_pixel(js, led, color: Color):
        LedControl.set_aya_subpixel(js, led * 3, color.R)
        LedControl.set_aya_subpixel(js, led * 3 + 1, color.G)
        LedControl.set_aya_subpixel(js, led * 3 + 2, color.B)

    @staticmethod
    def set_aya_subpixel(js, subpixel_idx, brightness):
        logging.debug(f"js={js} subpixel_idx={subpixel_idx},brightness={brightness}")
        LedControl.aya_ec_cmd(js, subpixel_idx, brightness)

    @staticmethod
    def aya_ec_cmd(cmd, p1, p2):
        for x in range(2):
            EC.Write(0x6D, cmd)
            EC.Write(0xB1, p1)
            EC.Write(0xB2, p2)
            EC.Write(0xBF, 0x10)
            # time.sleep(0.01)
            EC.Write(0xBF, 0xFF)
            # time.sleep(0.01)
