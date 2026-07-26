import collections

class ActionBuffer:
    def __init__(self, max_length=5):
        self.buffer = collections.deque(maxlen=max_length)

    def add_action(self, action_type, target_description):
        self.buffer.append({"action": action_type, "target": target_description})

    def get_context_string(self):
        if not self.buffer:
            return ""
        context = "Recent Actions Taken (Context):\n"
        for i, act in enumerate(self.buffer, 1):
            context += f"{i}. {act['action']} - {act['target']}\n"
        return context

    def detect_loop(self):
        if len(self.buffer) < 3:
            return False
        
        last_three = list(self.buffer)[-3:]
        first = last_three[0]
        return all(x == first for x in last_three)

    def clear(self):
        self.buffer.clear()
