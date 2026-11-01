from enum import Enum

class PetState(Enum):
    IDLE = 'idle'
    WALK = 'walk'
    FALL = 'fall'
    DRAG = 'drag'
    COLLECT = 'collect'
    EAT = 'eat'
    WORK = 'work'
    RANDOM = 'random'
    ANIMATION = 'animation'
    FOLLOW = 'follow'

class StateMixin:
    ACTIONS = {
        PetState.IDLE: 'startIdle', PetState.WALK: 'startWalk',
        PetState.FALL: 'startFall', PetState.DRAG: 'startLift',
        PetState.COLLECT: 'startCollect', PetState.EAT: 'enter_eat_mode',
        PetState.WORK: 'enter_work_mode', PetState.RANDOM: 'play_random_animation',
        PetState.ANIMATION: 'startIdle',
        PetState.FOLLOW: 'start_follow',
    }

    @property
    def currentAction(self):
        return getattr(self, self.ACTIONS[self.state])

    @currentAction.setter
    def currentAction(self, action):
        state = next(key for key, value in self.ACTIONS.items() if value == action.__name__)
        self._transition(state)

    @property
    def is_working(self): return self.state == PetState.WORK
    @property
    def is_eating(self): return self.state == PetState.EAT
    @property
    def is_playing_random_animation(self): return self.state == PetState.RANDOM

    def _transition(self, state):
        self.stopOtherActions()
        self.state = state
        if state in (PetState.EAT, PetState.WORK):
            self.collectible_timer.stop()
            self.collectible_check_timer.stop()
            self.random_animation_timer.stop()
            for item in self.collectibles:
                item.close()
                item.deleteLater()
            self.collectibles.clear()
        else:
            self._resume_background()
