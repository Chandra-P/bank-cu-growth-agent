"""Reproduce a scripted recorded-evidence sample; no credential access."""
import argparse
from pathlib import Path

from langgraph.types import Command

from .demo import DemoSearch, DemoAnalyst, demo_request
from .graph import build_graph, new_state
from .report import export_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo",action="store_true",required=True)
    parser.add_argument("--approve-demo",action="store_true",help="Explicitly approve the scripted recorded sample, not a live report")
    parser.add_argument("--outage",action="store_true")
    args = parser.parse_args()
    graph = build_graph(DemoSearch(outage=args.outage),DemoAnalyst())
    state = new_state(demo_request(),"recorded")
    config = {"configurable":{"thread_id":state["run_id"]},"recursion_limit":60}
    result = graph.invoke(state,config)
    result = graph.invoke(Command(resume={"competitors":result["candidates"]}),config)
    if not args.approve_demo:
        print("Recorded demo reached the review gate. Pass --approve-demo to create a labeled scripted sample export.")
        return
    result = graph.invoke(Command(resume={"approve":True,"note":"Scripted recorded-evidence demonstration approval. Not a real human review or live provider evaluation."}),config)
    md,js = export_bundle(result)
    output = Path(__file__).resolve().parent.parent / "samples"
    output.mkdir(exist_ok=True)
    stem = "charlotte-outage-demo" if args.outage else "charlotte-recorded-demo"
    (output / f"{stem}.md").write_text(md,encoding="utf-8")
    (output / f"{stem}.json").write_text(js,encoding="utf-8")
    print(f"Recorded demo exported: {stem}.md and {stem}.json")


if __name__ == "__main__":
    main()
