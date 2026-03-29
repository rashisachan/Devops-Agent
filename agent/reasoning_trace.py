from datetime import datetime

class ReasoningTrace:
    """Logs every step the agent takes so you can see its thinking."""
    
    def __init__(self):
        self.steps = []
        self.start_time = datetime.now()
    
    def add(self, step_name: str, details: str, result: str = ""):
        entry = {
            "step": step_name,
            "details": details,
            "result": result,
            "time": datetime.now().strftime("%H:%M:%S")
        }
        self.steps.append(entry)
        # Print live so you can see it working
        print(f"\n{'='*50}")
        print(f"🔍 [{entry['time']}] {step_name}")
        print(f"   Details: {details}")
        if result:
            print(f"   Result:  {result}")
    
    def format_for_pr(self) -> str:
        """Format trace as markdown for the PR description."""
        lines = ["## 🧠 Agent Reasoning Trace\n"]
        for i, s in enumerate(self.steps, 1):
            lines.append(f"### Step {i}: {s['step']} `{s['time']}`")
            lines.append(f"- **Details:** {s['details']}")
            if s['result']:
                lines.append(f"- **Result:** {s['result']}")
            lines.append("")
        return "\n".join(lines)
    
    def save_to_file(self, path="reasoning_trace.md"):
        with open(path, "w") as f:
            f.write(self.format_for_pr())