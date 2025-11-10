from __future__ import annotations
import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List
import logging
import sys

#!/usr/bin/env python3
"""
samplenew.py - Simple file-backed TODO manager (sample Python code).
Usage:
    python samplenew.py add "Buy milk"
    python samplenew.py list
    python.samplenew.py complete 1
"""


STORE_PATH = Path.home() / ".samplenew_todos.json"
logging.basicConfig(level=logging.INFO, format="%(message)s")


@dataclass
class Todo:
        id: int
        title: str
        done: bool = False


class TodoStore:
        def __init__(self, path: Path = STORE_PATH):
                self.path = path
                self._todos: List[Todo] = []
                self._load()

        def _load(self):
                if not self.path.exists():
                        self._todos = []
                        return
                try:
                        data = json.loads(self.path.read_text(encoding="utf-8"))
                        self._todos = [Todo(**item) for item in data]
                except Exception as e:
                        logging.error("Failed to load store: %s", e)
                        self._todos = []

        def _save(self):
                self.path.write_text(json.dumps([asdict(t) for t in self._todos], indent=2), encoding="utf-8")

        def list(self) -> List[Todo]:
                return list(self._todos)

        def add(self, title: str) -> Todo:
                next_id = max((t.id for t in self._todos), default=0) + 1
                todo = Todo(id=next_id, title=title)
                self._todos.append(todo)
                self._save()
                return todo

        def complete(self, todo_id: int) -> bool:
                for t in self._todos:
                        if t.id == todo_id:
                                t.done = True
                                self._save()
                                return True
                return False

        def remove(self, todo_id: int) -> bool:
                for i, t in enumerate(self._todos):
                        if t.id == todo_id:
                                del self._todos[i]
                                self._save()
                                return True
                return False

        def clear(self):
                self._todos = []
                self._save()


def cmd_add(args, store: TodoStore):
        todo = store.add(args.title)
        logging.info("Added: [%d] %s", todo.id, todo.title)


def cmd_list(args, store: TodoStore):
        todos = store.list()
        if not todos:
                logging.info("No todos.")
                return
        for t in todos:
                status = "x" if t.done else " "
                logging.info("[%d] [%s] %s", t.id, status, t.title)


def cmd_complete(args, store: TodoStore):
        ok = store.complete(args.id)
        logging.info("Completed: %s", ok)


def cmd_remove(args, store: TodoStore):
        ok = store.remove(args.id)
        logging.info("Removed: %s", ok)


def cmd_clear(args, store: TodoStore):
        store.clear()
        logging.info("Cleared all todos.")


def build_parser() -> argparse.ArgumentParser:
        p = argparse.ArgumentParser(description="Sample TODO manager")
        sub = p.add_subparsers(dest="cmd", required=True)

        a = sub.add_parser("add", help="Add a todo")
        a.add_argument("title", help="Todo title")
        a.set_defaults(func=cmd_add)

        l = sub.add_parser("list", help="List todos")
        l.set_defaults(func=cmd_list)

        c = sub.add_parser("complete", help="Mark todo complete")
        c.add_argument("id", type=int, help="Todo id")
        c.set_defaults(func=cmd_complete)

        r = sub.add_parser("remove", help="Remove todo")
        r.add_argument("id", type=int, help="Todo id")
        r.set_defaults(func=cmd_remove)

        cl = sub.add_parser("clear", help="Remove all todos")
        cl.set_defaults(func=cmd_clear)

        return p


def main(argv=None):
        argv = argv or sys.argv[1:]
        parser = build_parser()
        args = parser.parse_args(argv)
        store = TodoStore()
        args.func(args, store)


if __name__ == "__main__":
        main()