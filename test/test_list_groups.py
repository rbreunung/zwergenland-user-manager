"""This class tests the use case to find all groups by the given prefixes."""

import json
from os import environ
import sys
from typing import Dict
from dotenv import dotenv_values
from authentication import authenticate
from group import GroupHandler


env: Dict[str, str | None] = dict(environ) | dotenv_values()


env_prefixes = env['GROUP_PREFIXES']
print(f"GROUP_PREFIXES={env_prefixes}")
assert env_prefixes is not None, "environment value GROUP_PREFIXES shall be set."

prefixes_list = [prefix.strip() for prefix in env_prefixes.split(',')]

if not input(f"Defined prefixes {prefixes_list}. Continue? (y/N)") == 'y':
    print("Exit on user request.")
    sys.exit()

token = authenticate(env)

group_handler = GroupHandler(token)

for group_prefix in prefixes_list:
    print(f"Reading group names for prefix {group_prefix}")
    groups = group_handler.get_groups(group_prefix)
    if groups:
        print(f"{json.dumps(groups, indent=2)}\n---")
