from kivy.uix.relativelayout import RelativeLayout


def keyboard_closed(self):
    self._keyboad.unbind(on_key_down=self.on_keyboard_down)
    self._keyboad.unbind(on_key_down=self.on_keyboard_up)
    self._keyboad = None


def on_touch_down(self, touch):
    if not self.game_over and self.game_start:
        if touch.x < self.width / 2:
            # self.current_speed_x = self.SPEED_X
            self.current_speed_x = self.game_speed_x
        else:
            # self.current_speed_x = -self.SPEED_X
            self.current_speed_x = -self.game_speed_x
    return super(RelativeLayout, self).on_touch_down(touch)

def on_touch_up(self, touch):
    self.current_speed_x = 0


def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'left':
        # self.current_speed_x = self.SPEED_X
        self.current_speed_x = self.game_speed_x
    elif keycode[1] == 'right':
        # self.current_speed_x = -self.SPEED_X
        self.current_speed_x = -self.game_speed_x
    return True


def on_keyboard_up(self, keyboard, keycode):
    self.current_speed_x = 0
    return True