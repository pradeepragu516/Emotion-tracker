from jarvis.emotion_logic import EmotionEngine
from jarvis.planner import TaskPlanner
from jarvis.system import SystemController
from jarvis.memory import ContextMemory
from jarvis.speaker import speak

class JarvisCore:
    def __init__(self):
        self.memory = ContextMemory()
        self.emotion_engine = EmotionEngine()
        self.planner = TaskPlanner()
        self.system = SystemController()

    def perceive(self, emotion, gender, age):
        self.memory.update_user_profile(gender, age)
        mood_state = self.emotion_engine.analyze(emotion)
        self.memory.update_emotion(mood_state)

        verbal_resp = mood_state.get("verbal_response", "")
        if verbal_resp:
            speak(verbal_resp)
        return mood_state

    def think(self, command_text):
        if not command_text:
            return [{"action": "IDLE", "message": "No command heard"}]
        context = self.memory.get_context()
        plan = self.planner.create_plan(command_text, context)
        self.memory.update_last_result({"command": command_text, "plan": plan})
        return plan

    def act(self, plan):
        results = []
        if isinstance(plan, list):
            for step in plan:
                res = self.system.execute(step)
                results.append(res)
        return results

    def feedback(self, results=None):
        """
        Provides verbal and visual feedback on completed actions.
        """
        if not results:
            context = self.memory.get_context()
            last_res = context.get("last_result")
            if last_res:
                speak(f"Completed command: {last_res.get('command')}")
            else:
                speak("Task processing completed.")
            return

        for res in results:
            if isinstance(res, dict) and "speech" in res and res["speech"]:
                speak(res["speech"])
            elif isinstance(res, str):
                speak(res)

