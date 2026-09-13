import sys
sys.path.insert(0, "/tmp/claude-0/-home-user-Alignment/ce4299d9-52cc-540f-afd3-bbf139fb48f9/scratchpad/audit/inspect_evals/src")
from inspect_evals.gdm_self_reasoning.data import dataset
from inspect_evals.gdm_self_reasoning import gdm_self_reasoning as g
import inspect_evals.gdm_self_reasoning.gdm_self_reasoning as G
# 1) samples per task
names = ["max_tokens","turn_off_filters","database_tool","approved_directories","read_logs",
         "context_length_mod_instrumental_only","context_length_mod_irreversibility_only",
         "calculator_improvement","latency_calculator","max_messages_calculator","oversight_frequency"]
for n in names:
    s = dataset.read_dataset(n)
    combos = [(x.metadata["noticing_difficulty"], x.metadata["execution_difficulty"]) for x in s]
    print(f"{n:42s} n_samples={len(s)} combos={combos}")
# 2) the task scorer only reads store SUCCESS (single binary); no noticing/execution split
import inspect
src = inspect.getsource(G._success_scorer)
print("\n_success_scorer body has 'noticing' or 'execution'? ->",
      ("noticing" in src or "execution" in src))
# 3) reducer + epochs
t = G.gdm_self_reasoning_max_tokens()
print("epochs:", t.epochs.epochs, "reducer:", [r.__name__ if hasattr(r,'__name__') else r for r in ([t.epochs.reducer] if not isinstance(t.epochs.reducer, list) else t.epochs.reducer)])
print("scorer metrics:", [m for m in t.scorer[0].__dict__] if hasattr(t.scorer[0],'__dict__') else "n/a")
