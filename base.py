import quart as q
import sqlalchemy as s
import sqlalchemy.dialects.sqlite as sq
import databases as d
import sqlite3 as sl

import base64
import hashlib
import secrets
import datetime
import uuid
import logging
import textwrap

###################################################### FUNCTIONS ######################################################

def random_id():
	# return secrets.randbelow(9223372036854775807 - 1000000000000000000) + 1000000000000000000
	return str(uuid.uuid4())

def auth_decode(str):
	return base64.b64decode(str[6:]).decode("utf-8").split(":")

def print_sql(app, query):
	app.logger.info("\n" + textwrap.indent(str(query), "  "))
	

def auth_invalid(resp):
	resp.status_code = 401
	resp.headers["WWW-Authenticate"] = "Basic realm=\"wordle-webauth\""

def auth_error():
	response = q.jsonify({
		"error": "Invalid authorization header.",
		"fix": "Please provide username and password."
	})

	auth_invalid(response)

	return response

###################################################### VARIABLES ######################################################

# Parse ./etc/db.toml file and put the values into variables above
with open("etc/db.toml", "r") as f:
	import toml
	for key, value in toml.load(f)["DATABASES"].items():
		globals()[key] = value

# Should print everything as expected
# print(globals()["USER_DB_PATH"])
# print(globals()["GAME_DB_PATH"])
# print(globals()["WORD_DB_PATH"])

###################################################### DATABASES ######################################################

class ForeignKeyConnection(sl.Connection):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.execute("PRAGMA foreign_keys = ON")

def make_table (name, *cols):
	meta = s.MetaData()
	return s.Table(name, meta, *cols)

# q.logging.basicConfig(filename="db.log",level=q.logging.DEBUG)

logging.basicConfig(level=logging.INFO)
