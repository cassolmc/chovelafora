class Scene:
    def __init__(self, manager):
        self.manager = manager
        self.screen  = manager.screen

    def on_enter(self): pass
    def on_exit(self):  pass
    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self, screen): pass


class SceneManager:
    def __init__(self, screen):
        self.screen  = screen
        self._scenes = {}
        self.current = None
        self.current_name = None

    def register(self, name, scene_class):
        self._scenes[name] = scene_class(self)

    def go_to(self, name):
        if self.current:
            self.current.on_exit()
        self.current = self._scenes[name]
        self.current_name = name
        self.current.on_enter()

    def handle_event(self, event):
        if self.current:
            self.current.handle_event(event)

    def update(self, dt):
        if self.current:
            self.current.update(dt)

    def draw(self):
        if self.current:
            self.current.draw(self.screen)
