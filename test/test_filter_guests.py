
import json
from os import environ
from typing import Dict

from dotenv import dotenv_values

from authentication import authenticate
from user import UserHandler


env: Dict[str, str | None] = dict(environ) | dotenv_values()
token = authenticate(env)

user_handler = UserHandler(token)
all_guests = user_handler.get_guests()
guests_without_group = user_handler.filter_users_without_group(all_guests)
for guest in guests_without_group:
    print(json.dumps(guest, indent=2))
