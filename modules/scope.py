
class Scope:

    def __init__(self):
        self._stack = []
        self.enter()  # default "global" scope

    def enter(self):
        self._stack.append({})

    def leave(self):
        self._stack.pop()

    def get_var(self, name):
        for scope in reversed(self._stack):
            if name in scope:
                return scope[name]

        return None

    def set_var(self, name, value):
        # FIXME Inside functions, writes to global variables (without prefix) must not be visible to the global scope
        for scope in reversed(self._stack):
            if name in scope:
                scope[name] = value
                break
        else:
            self._stack[-1][name] = value

    def del_var(self, name):
        for scope in self._stack:
            if name in scope:
                del scope[name]
