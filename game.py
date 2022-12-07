__import__("sys", globals(), locals(), ["path"], 0).path.append("../")
base = __import__(".base", globals(), locals(), ["*"], 0)

###################################################### FUNCTIONS ######################################################

def analyze_sole(guess, answer, flag):
	step = len(answer)
	res_list = []
	chk_list = [False] * step

	for i in range(step):
		if guess[i] == answer[i]:
			res_list.append({
				"msg": "Character is correct.",
				"code": 2
			} if flag else 2)
			chk_list[i] = True
		else:
			for j in range(step):
				if (guess[i] == answer[j] and (not chk_list[j] or guess[j] != answer[j])):
					chk_list[j] = True
					break
			else:
				res_list.append({
					"msg": "Character incorrect.",
					"code": 0
				} if flag else 0)
				continue
			res_list.append({
				"msg": "Character exists somewhere in word.",
				"code": 1
			} if flag else 1)
	
	return res_list

def analyze_many(garr, ans, flag):
	res = []

	for curr in garr:
		res.append({
			"word": curr["word"],
			"check": analyze_sole(curr["word"], ans, flag)
		})

	return res

###################################################### DATABASES ######################################################

word_db = base.d.Database(base.WORD_DB_PATH, factory=base.ForeignKeyConnection)
game_db = base.d.Database(base.GAME_DB_PATH, factory=base.ForeignKeyConnection)

wordle_game_table = base.make_table(
	"wordle_game",
	base.s.Column("game_id", base.s.String(length=36), primary_key=True, nullable=False),
	base.s.Column("username", base.s.Text, primary_key=True, nullable=False),
	base.s.Column("word", base.s.Text, nullable=False) # The answer for the word
	# s.Column("count", s.BigInteger, nullable=False) # Total guesses so far (Probably not needed)
)

wordle_guess_table = base.make_table(
	"wordle_guess",
	base.s.Column("game_id", base.s.String(length=36), base.s.ForeignKey("wordle_game.game_id", ondelete="CASCADE"), primary_key=True, nullable=False),
	base.s.Column("word", base.s.Text, nullable=False), # The guess for the word
	base.s.Column("order", base.s.BigInteger, primary_key=True, nullable=False) # Order of the guesses (higher = later)
)

wordle_word_table = base.make_table(
	"wordle_word",
	base.s.Column("valid", base.s.Integer, nullable=False),
	base.s.Column("word", base.s.Text, nullable=False)
)

###################################################### API ######################################################

app = base.q.Quart(__name__)

@app.route("/start", strict_slashes=False, methods=["POST"])
async def game_start():
	# Start a new game

	auth_data = base.auth_decode(base.q.request.headers.get("Authorization"))

	# Get random word from wordle_word_table using word.db
	query_str = wordle_word_table.select() \
		.where(wordle_word_table.c.valid == 1) \
		.order_by(base.s.sql.expression.func.random()) \
		.limit(1)

	curr_word = await word_db.fetch_one(query=query_str)

	base.print_sql(app, query_str)

	curr_game_id = base.random_id()

	await game_db.execute(
		query=wordle_game_table.insert(),
		values={
			"game_id": curr_game_id,
			"username": auth_data[0],
			"word": curr_word["word"]
		}
	)

	return base.q.jsonify({
		"game_id": curr_game_id
	}), 200

@app.route("/list", strict_slashes=False, methods=["GET"])
async def game_list():
	# List all available games that are associated with the given account_id
	
	auth_data = base.auth_decode(base.q.request.headers.get("Authorization"))

	query_str = wordle_game_table.select().where(wordle_game_table.c.username == auth_data[0])

	games = await game_db.fetch_all(query=query_str)

	base.print_sql(app, query_str)

	return base.q.jsonify(
		[game["game_id"] for game in games]
	), 200

@app.route("/state", strict_slashes=False, methods=["POST"])
async def game_state():
	# List the wordle_game and wordle_guesses given username

	data = await base.q.request.get_json()

	try:

		if "game_id" not in data:
			return base.q.jsonify({
				"error": "Missing game_id.",
				"fix": "Resubmit with game_id."
			}), 400

		query_str = wordle_game_table.select().where(wordle_game_table.c.game_id == data["game_id"])

		answer = await game_db.fetch_one(query=query_str)

		base.print_sql(app, query_str)

		if answer is None:
			raise base.sl.NoResultFound

		query_str = wordle_guess_table.select() \
			.where(wordle_guess_table.c.game_id == data["game_id"]) \
			.order_by(wordle_guess_table.c.order.asc())

		guess_list = await game_db.fetch_all(query=query_str)

		base.print_sql(app, query_str)

		return base.q.jsonify(
			analyze_many(guess_list, answer["word"], False)
		), 200

	except:
		pass

	return base.q.jsonify({
		"error": "Game id does not exist.",
		"fix": "Create a new game."
	}), 400

@app.route("/submit", strict_slashes=False, methods=["POST"])
async def game_submit():
	# Attempt to submit guesses

	data = await base.q.request.get_json()

	try:

		if "game_id" not in data or "word" not in data:
			return base.q.jsonify({
				"error": "Missing game_id or word.",
				"fix": "Resubmit with game_id and word."
			}), 400

		query_str = wordle_guess_table.select() \
			.where(wordle_guess_table.c.game_id == data["game_id"]) \
			.order_by(wordle_guess_table.c.order.asc())

		guess_list = await game_db.fetch_all(query=query_str)

		base.print_sql(app, query_str)

		res = {}
		res["left"] = 6 - (1 if len(guess_list) == 0 else (guess_list[-1]["order"] + 2))

		# Check if data["word"] inside wordle_word_table in word.db
		query_str = wordle_word_table.select().where(wordle_word_table.c.word == data["word"])

		check = await word_db.fetch_one(query=query_str)

		base.print_sql(app, query_str)

		if check is None:
			res["msg"] = "Invalid word."
			return base.q.jsonify(res), 200

		await game_db.execute(
			query=wordle_guess_table.insert(),
			values={
				"game_id": data["game_id"],
				"word": data["word"],
				"order": 5 - res["left"]
			}
		)

		query_str = wordle_game_table.select().where(wordle_game_table.c.game_id == data["game_id"])

		answer = await game_db.fetch_one(query=query_str)

		base.print_sql(app, query_str)

		if data["word"] != answer["word"]:
			if res["left"] > 0:
				res["msg"] = "Incorrect guess."
				res["check"] = analyze_sole(data["word"], answer["word"], True)

				return base.q.jsonify(res), 200
			else:
				res["msg"] = "Game ended. You lost."
		else:
			res["msg"] = "Game ended. You guessed correctly."

		guess_list.append({"word": data["word"]})

		res["state"] = analyze_many(guess_list, answer["word"], False)
		res["answer"] = answer["word"]

		# Delete associated wordle_game
		await game_db.execute(
			query=wordle_game_table.delete().where(wordle_game_table.c.game_id == data["game_id"])
		)

		return base.q.jsonify(res), 200

	except base.sl.IntegrityError:

		return base.q.jsonify({
			"error": "Game id does not exist.",
			"fix": "Create a new game."
		}), 400

@app.route("/delete", strict_slashes=False, methods=["DELETE"])
async def game_delete():
	# Delete a game

	data = await base.q.request.get_json()

	try:

		if "game_id" not in data:
			return base.q.jsonify({
				"error": "Missing game_id.",
				"fix": "Resubmit with game_id."
			}), 400

		await game_db.execute(
			query=wordle_game_table.delete().where(wordle_game_table.c.game_id == data["game_id"])
		)

		return base.q.jsonify({
			"msg": "Game deleted."
		}), 200

	except base.sl.IntegrityError:

		return base.q.jsonify({
			"error": "Game id does not exist.",
			"fix": "Create a new game."
		}), 400

@app.route("/")
async def main():
	# Return jsonified list of all routes
	return base.q.jsonify({
		"/start": {
			"desc": "Start a new game.",
			"params": {
				"username": "Username of the player."
			}
		},
		"/list": {
			"desc": "List all available games.",
			"params": {
				"username": "Username of the player."
			}
		},
		"/state": {
			"desc": "Show game state given game_id.",
			"params": {
				"username": "Username of the player.",
				"game_id": "Game id."
			}
		},
		"/submit": {
			"desc": "Submit a guess.",
			"params": {
				"username": "Username of the player.",
				"game_id": "Game id.",
				"word": "Word to guess."
			}
		},
		"/delete": {
			"desc": "Delete a game.",
			"params": {
				"username": "Username of the player.",
				"game_id": "Game id."
			}
		}
	}), 200

if __name__ == "__main__":
	app.run()

# hypercorn.exe game --bind app.local.gd:5679
