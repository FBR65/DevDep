"""
CLI entry point for the Superpowers system.

Usage:
    uv run python -m devdep.superpowers bootstrap
    uv run python -m devdep.superpowers check "I need to implement auth"
    uv run python -m devdep.superpowers gate hard-gate
    uv run python -m devdep.superpowers skills
"""

import sys
import argparse

from .session import SuperpowersSession


def main():
    parser = argparse.ArgumentParser(
        prog="superpowers",
        description="Superpowers - Structured AI Development Methodology",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # bootstrap command
    bootstrap_parser = subparsers.add_parser("bootstrap", help="Initialize a Superpowers session")
    bootstrap_parser.add_argument("--workspace", default="devdep/workspace", help="Workspace directory")

    # check command (1%% Rule)
    check_parser = subparsers.add_parser("check", help="Run 1%% Rule skill check")
    check_parser.add_argument("context", help="Context to check against skills")
    check_parser.add_argument("--workspace", default="devdep/workspace", help="Workspace directory")

    # gate command
    gate_parser = subparsers.add_parser("gate", help="Evaluate a development gate")
    gate_parser.add_argument("gate_name", choices=["hard-gate", "tdd-gate", "review-gate"], help="Gate to evaluate")
    gate_parser.add_argument("--workspace", default="devdep/workspace", help="Workspace directory")

    # skills command
    skills_parser = subparsers.add_parser("skills", help="List all available skills")
    skills_parser.add_argument("--workspace", default="devdep/workspace", help="Workspace directory")

    # state command
    state_parser = subparsers.add_parser("state", help="Show current session state")
    state_parser.add_argument("--workspace", default="devdep/workspace", help="Workspace directory")

    # invoke command
    invoke_parser = subparsers.add_parser("invoke", help="Invoke a skill and show its content")
    invoke_parser.add_argument("skill_slug", help="Skill slug to invoke")
    invoke_parser.add_argument("--workspace", default="devdep/workspace", help="Workspace directory")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    session = SuperpowersSession(workspace=args.workspace)

    if args.command == "bootstrap":
        session.bootstrap()
        print(f"\nRecommended next skill: {session.get_recommended_skill() or 'None'}")

    elif args.command == "check":
        session.bootstrap()
        applicable = session.run_skill_check(args.context)
        if applicable:
            print(f"\nInvoke with: uv run python -m devdep.superpowers invoke {applicable[0].slug}")

    elif args.command == "gate":
        session.bootstrap()
        passed = session.evaluate_gate(args.gate_name)
        sys.exit(0 if passed else 1)

    elif args.command == "skills":
        session.bootstrap()
        print("\nAll available skills:")
        for skill in session.skills.list_skills():
            print(f"  {skill.slug:20s} - {skill.name}")

    elif args.command == "state":
        session.bootstrap()
        print(f"\nCurrent state: {session.state}")
        print(f"Recommended skill: {session.get_recommended_skill() or 'None'}")

    elif args.command == "invoke":
        session.bootstrap()
        content = session.invoke_skill(args.skill_slug)
        print(f"\n{'='*60}")
        print(f"SKILL: {args.skill_slug}")
        print(f"{'='*60}")
        print(content)


if __name__ == "__main__":
    main()
