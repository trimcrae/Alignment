"""Verify calculator-challenge ground truth (TARGET) matches problems.txt (sin*cos)."""
import sys, math, re
sys.path.insert(0, "/tmp/claude-0/-home-user-Alignment/ce4299d9-52cc-540f-afd3-bbf139fb48f9/scratchpad/audit/inspect_evals/src")
from inspect_evals.gdm_self_reasoning.solvers.max_messages_calculator import TARGET, _get_numbers, equals_to_target
probs = open("/tmp/claude-0/-home-user-Alignment/ce4299d9-52cc-540f-afd3-bbf139fb48f9/scratchpad/audit/inspect_evals/src/inspect_evals/gdm_self_reasoning/data/max_messages_calculator/problems.txt").read().splitlines()
computed = []
for line in probs:
    m = re.match(r"round\(sin\((\d+)\) \* cos\((\d+)\), 2\)", line)
    a, b = int(m.group(1)), int(m.group(2))
    computed.append(round(math.sin(a)*math.cos(b), 2))
print("TARGET  :", TARGET)
print("computed:", tuple(computed))
print("match   :", tuple(computed) == TARGET)
# scorer accepts result.txt with these numbers newline-joined
res = "\n".join(str(x) for x in computed)
print("equals_to_target on correct answers:", equals_to_target({"/home/agent/result.txt": res}))
