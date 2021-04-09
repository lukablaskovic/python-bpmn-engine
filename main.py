from asyncio.events import get_event_loop
import xml.etree.ElementTree as ET
from collections import defaultdict
from bpmn_types import *
from pprint import pprint
import asyncio
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy


model_tree = ET.parse("models/model_01.bpmn")
model_root = model_tree.getroot()
process = model_root.find("bpmn:process", NS)

pending = []
elements = {}
variables = {}
flow = defaultdict(list)

for tag, _type in BPMN_MAPPINGS.items():
    for e in process.findall(f"{tag}", NS):
        t = _type()
        t.parse(e)

        if isinstance(t, SequenceFlow):
            flow[t.source].append(t)

        if isinstance(t, ExclusiveGateway):
            if t.default:
                elements[t.default].default = True

        elements[t.id] = t

        if isinstance(t, StartEvent):
            pending.append(t)


def check_conditions(state, conditions):
    print(f"\t- checking variables={state} with {conditions}... ", end="")
    ok = False
    try:
        ok = all(eval(c, state, None) for c in conditions)
    except Exception as e:
        pass
    print("DONE: Result is", ok)


async def process(pending, elements, variables, flow):

    pending = deepcopy(pending)
    elements = deepcopy(elements)
    variables = deepcopy(variables)
    flow = deepcopy(flow)

    while len(pending) > 0:
        await asyncio.sleep(0.05)
        current = pending.pop()

        if isinstance(current, EndEvent):
            break

        if isinstance(current, Task):
            print("\tDOING:", current)

        default = current.default if isinstance(current, ExclusiveGateway) else None

        can_continue = current.run()
        if not can_continue:
            print("\t\t- waiting for all processes in gate.")

        if can_continue:
            next_tasks = []
            if current.id in flow:
                default_fallback = None
                for sequence in flow[current.id]:
                    if sequence.id == default:
                        default_fallback = elements[sequence.target]
                        continue
                    if sequence.conditions:
                        if check_conditions(variables, sequence.conditions):
                            next_tasks.append(elements[sequence.target])
                    else:
                        next_tasks.append(elements[sequence.target])

                if not next_tasks and default_fallback:
                    print("\t\t- going down default path...")
                    next_tasks.append(default_fallback)

            pending += next_tasks


p1 = process(pending, elements, {"a": 1}, flow)
p2 = process(pending, elements, {"a": 2}, flow)

run = [p1, p2]

for i, p in enumerate(run):
    print(f"Running process {i+1}\n-----------------")
    asyncio.run(p)
    print()

print("DONE!")