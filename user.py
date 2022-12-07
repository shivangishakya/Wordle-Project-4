__import__("sys", globals(), locals(), ["path"], 0).path.append("../")
base = __import__(".base", globals(), locals(), ["*"], 0)

app = base.q.Quart(__name__)

###################################################### FUNCTIONS ######################################################

def hash_password(password, salt=None, iterations=260000):
	if salt is None:
		salt = base.secrets.token_hex(16)
	assert salt and isinstance(salt, str) and "$" not in salt
	assert isinstance(password, str)
	pw_hash = base.hashlib.pbkdf2_hmac(
		"sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
	)
	b64_hash = base.base64.b64encode(pw_hash).decode("ascii").strip()
	return "{}${}${}${}".format("pbkdf2_sha256", iterations, salt, b64_hash)

def verify_password(password, password_hash):
	if (password_hash or "").count("$") != 3:
		return False
	algorithm, iterations, salt, b64_hash = password_hash.split("$", 3)
	iterations = int(iterations)
	assert algorithm == "pbkdf2_sha256"
	compare_hash = hash_password(password, salt, iterations)
	return base.secrets.compare_digest(password_hash, compare_hash)

async def auth_check(usr):
	# Check if usr dict has key "username"
	if usr is None or "username" not in usr:
		return None

	query_str = account_table.select().where(account_table.c.username == usr["username"])

	chk = await user_db.fetch_one(query=query_str)

	base.print_sql(app, query_str)

	# Only need to check if username exist as the prof said
	# if chk is None or chk["expire"] is None or \
	# 	datetime.datetime.now(datetime.timezone.utc) > \
	# 	chk["expire"].replace(tzinfo=datetime.timezone.utc):
	# 	return None
	
	return chk

###################################################### DATABASES ######################################################

user_db = base.d.Database(base.USER_DB_PATH, factory=base.ForeignKeyConnection)

account_table = base.make_table(
	"account",
	base.s.Column("acct_id", base.s.String(length=36), primary_key=True, nullable=False),
	base.s.Column("username", base.s.Text, primary_key=True, nullable=False), # Username can have any length
	base.s.Column("expire", base.s.DateTime, nullable=True),
	base.s.Column("password", base.s.String(length=98), nullable=False) # Hash always have length of 98
)

###################################################### API ######################################################

# http POST http://asd:asd123@127.0.0.1:5678/regist

@app.route("/regist", strict_slashes=False, methods=["POST"])
async def auth_regist():
	# Create new account (also check for existing username)
	# Only returns 200 if success or 400 if error (for existing username or other errors)

	auth_header = base.q.request.headers.get("Authorization")

	if auth_header is None:
		return base.auth_error()

	data = base.auth_decode(auth_header)

	if data[0] == "" or data[1] == "":
		return base.q.jsonify({
			"error": "Username or password is empty.",
			"fix": "Resubmit with username and password."
		}), 400

	try:

		query_str = account_table.select().where(account_table.c.username == data[0])

		check = await user_db.fetch_val(query=query_str, column="username")

		base.print_sql(app, query_str)

		if check is None:

			await user_db.execute(
				query=account_table.insert(),
				values={
					"acct_id": base.random_id(),
					"username": data[0],
					"password": hash_password(data[1]),
					"expire": None
				}
			)

			return base.q.jsonify({
				"msg": "Account created. Please use /auth/login to login."
			}), 200

		else:
			
			return base.q.jsonify({
				"error": "Username already exists.",
				"fix": "Resubmit with different username."
			}), 400

	except base.sl.IntegrityError:

		return base.q.jsonify({
			"error": "Account id already exists.",
			"fix": "Resubmit."
		}), 400

# http POST http://asd:asd123@127.0.0.1:8000/login

@app.route("/login", strict_slashes=False, methods=["POST"])
async def auth_login():
	# Returns 200 if success or 400/401 if error (for wrong username or password)
	# Have return body to be account_id and authenticated per the docs said

	auth_header = base.q.request.headers.get("Authorization")

	if auth_header is None:
		return base.auth_error()

	data = base.auth_decode(auth_header)

	if data[0] == "" or data[1] == "":
		return base.q.jsonify({
			"error": "Username or password is empty.",
			"fix": "Resubmit with username and password."
		}), 400

	query_str = account_table.select().where(account_table.c.username == data[0])

	check = await user_db.fetch_one(query=query_str)

	base.print_sql(app, query_str)

	if (check is None) or not verify_password(data[1], check["password"]):
		resp = base.q.jsonify({
			"error": "Username or password is incorrect.",
			"fix": "Resubmit."
		})

		base.auth_invalid(resp)

		return resp

	await user_db.execute(
		query=account_table.update().where(account_table.c.username == data[0]),
		values={
			"expire": base.datetime.datetime.now(base.datetime.timezone.utc) + base.datetime.timedelta(days=1)
		}
	)

	return base.q.jsonify({
		"authenticated": True
	}), 200

# DELETE allow json body: https://stackoverflow.com/questions/299628/

@app.route("/delete", strict_slashes=False, methods=["DELETE"])
async def auth_delete():
	# Delete account (also delete all games associated with this account)
	# Only returns 200 if success or 400 if error (for wrong username or password)

	auth_header = base.q.request.headers.get("Authorization")

	if auth_header is None:
		return base.auth_error()

	data = base.auth_decode(auth_header)

	if data[0] == "" or data[1] == "":
		return base.q.jsonify({
			"error": "Username or password is empty.",
			"fix": "Resubmit with username and password."
		}), 400

	query_str = account_table.select().where(account_table.c.username == data[0])

	check = await user_db.fetch_one(query=query_str)

	base.print_sql(app, query_str)

	if (check is None) or not verify_password(data[1], check["password"]):
		resp = base.q.jsonify({
			"error": "Username/password is incorrect.",
			"fix": "Resubmit."
		})

		base.auth_invalid(resp)

		return resp

	# await user_db.execute(
	# 	query=wordle_game_table.delete().where(wordle_game_table.c.acct_id == check["acct_id"])
	# )

	await user_db.execute(
		query=account_table.delete().where(account_table.c.username == data[0])
	)

	return base.q.jsonify({
		"msg": "Account deleted."
	}), 200

@app.route("/")
async def main():
	# Return jsonified list of all routes
	return base.q.jsonify({
		"/login": {
			"desc": "Login to an account.",
			"headers": {
				"Authorization": "Basic <base64 encoded username:password>"
			}
		},
		"/regist": {
			"desc": "Create a new account.",
			"headers": {
				"Authorization": "Basic <base64 encoded username:password>"
			}
		},
		"/delete": {
			"desc": "Delete an account.",
			"headers": {
				"Authorization": "Basic <base64 encoded username:password>"
			}
		},
	}), 200

if __name__ == "__main__":
	app.run()

# hypercorn.exe user --bind app.local.gd:5678
