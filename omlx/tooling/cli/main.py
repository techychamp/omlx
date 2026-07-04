# SPDX-License-Identifier: Apache-2.0
"""
Compiler Validation CLI
Provides read-only CLI commands for developers.
"""
import argparse
import sys
import json

from omlx.tooling.inspector.inspector import CompilerInspector
from omlx.tooling.diff.differ import CompilerDiffer
from omlx.tooling.export.json_exporter import JsonExporter
from omlx.tooling.export.yaml_exporter import YamlExporter
from omlx.tooling.export.dot_exporter import DotExporter
from omlx.tooling.export.mermaid_exporter import MermaidExporter
from omlx.tooling.export.plantuml_exporter import PlantUMLExporter
from omlx.tooling.export.markdown_exporter import MarkdownExporter
from omlx.tooling.views.graph_views import to_value_graph
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.plan import ExecutionPlan

def get_exporter(fmt):
    exporters = {
        "json": JsonExporter(),
        "yaml": YamlExporter(),
        "dot": DotExporter(),
        "mermaid": MermaidExporter(),
        "plantuml": PlantUMLExporter(),
        "md": MarkdownExporter()
    }
    return exporters.get(fmt, JsonExporter())

def main():
    parser = argparse.ArgumentParser(description="oMLX Compiler Validation Toolkit")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # inspect-plan
    p_inspect_plan = subparsers.add_parser("inspect-plan", help="Inspect an execution plan")
    p_inspect_plan.add_argument("file", help="Path to plan JSON")

    # inspect-ir
    p_inspect_ir = subparsers.add_parser("inspect-ir", help="Inspect a Logical IR")
    p_inspect_ir.add_argument("file", help="Path to IR JSON")

    # export-graph
    p_export_graph = subparsers.add_parser("export-graph", help="Export a graph")
    p_export_graph.add_argument("file", help="Path to IR JSON")
    p_export_graph.add_argument("--format", choices=["json", "yaml", "dot", "mermaid", "plantuml", "md"], default="json")

    # compare-plans
    p_compare = subparsers.add_parser("compare-plans", help="Compare two plans")
    p_compare.add_argument("file1", help="Path to old plan JSON")
    p_compare.add_argument("file2", help="Path to new plan JSON")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "inspect-plan":
        with open(args.file, "r") as f:
            data = json.load(f)
        # Assuming the plan is serializable back/forth. Here we just dump as JSON for inspection.
        # A real implementation would parse the JSON into an ExecutionPlan object, then inspect it.
        # For CLI usage, printing the json data directly provides the inspection capability.
        print(json.dumps(data, indent=2))

    elif args.command == "inspect-ir":
        with open(args.file, "r") as f:
            data = json.load(f)
        try:
            ir = ExecutionIR.from_dict(data)
            inspector = CompilerInspector()
            print(json.dumps(inspector.inspect_logical_ir(ir), indent=2))
        except Exception as e:
            print(f"Failed to inspect IR: {e}")
            print(json.dumps(data, indent=2))

    elif args.command == "export-graph":
        with open(args.file, "r") as f:
            data = json.load(f)
        try:
            ir = ExecutionIR.from_dict(data)
            graph_data = to_value_graph(ir)
        except Exception:
            # If not valid IR, just treat as generic graph data
            graph_data = data

        exporter = get_exporter(args.format)
        print(exporter.export(graph_data))

    elif args.command == "compare-plans":
        with open(args.file1, "r") as f1, open(args.file2, "r") as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)

        differ = CompilerDiffer()
        diff_result = differ.diff_dicts(data1, data2)
        print(json.dumps(diff_result, indent=2))

if __name__ == "__main__":
    main()
