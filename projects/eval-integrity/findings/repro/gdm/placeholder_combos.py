"""dataset._get_all_placeholder_combinations claims (README) to build the full
cartesian product of multi-valued placeholders, but iterates i%len per variable,
so with 2+ multi-valued vars it returns only the 'diagonal' (with duplicates)."""
import sys
sys.path.insert(0, "/tmp/claude-0/-home-user-Alignment/ce4299d9-52cc-540f-afd3-bbf139fb48f9/scratchpad/audit/inspect_evals/src")
from inspect_evals.gdm_self_proliferation.dataset import _get_all_placeholder_combinations as f
variables = {"INSTANCE_NAME": ["vm-1","vm-2"], "INSTANCE_ZONE": ["zone-a","zone-b"]}
got = f(variables, "variables.json")
print("got:", got)
want = [{"INSTANCE_NAME":n,"INSTANCE_ZONE":z} for n in ["vm-1","vm-2"] for z in ["zone-a","zone-b"]]
print("full cartesian product (4):", want)
print("distinct combos returned:", len({tuple(sorted(d.items())) for d in got}), "of 4 expected")
