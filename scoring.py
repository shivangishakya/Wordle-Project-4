__import__("sys", globals(), locals(), ["path"], 0).path.append("../")
base = __import__(".base", globals(), locals(), ["*"], 0)

import redis, ast

app = base.q.Quart(__name__)
r = redis.Redis("localhost", 6379)
	
################################################################### API
###################################################################
		
@app.route("/submitScore", strict_slashes=False, methods=["POST"])
async def submit_score():
	auth_header = base.q.request.headers.get("Authorization")

	if auth_header is None:
		return base.auth_error()	
		
	auth_data = base.auth_decode(auth_header)
	
	data = await base.q.request.get_json()
	try:
		if "guess_number" not in data or "win" not in data:
			return base.q.jsonify({
				"error": "Missing game_id or guess_number.",
				"fix": "Resubmit with game_id and guess_number."
			}), 400
		if data["win"] == "False" and int(data["guess_number"]) < 6:
			return base.q.jsonify({
				"msg": "You have chances left to play",
			}), 200
			
		score = 0
		if data["win"] == "True":
			if int(data["guess_number"]) == 1:
				score = 6
			elif int(data["guess_number"]) == 2:
				score = 5
			elif int(data["guess_number"]) == 3:
				score = 4
			elif int(data["guess_number"]) == 4:
				score = 3
			elif int(data["guess_number"]) == 5:
				score = 2
			else:
				score = 1
		else:
			score = 0
			
		games = 1
		if r.exists(auth_data[0]):
			score_data = ast.literal_eval((r.get(auth_data[0])).decode("UTF-8"))
			games = int(score_data["games"])
			score = (score + (int(score_data["score"])*games)) / (games + 1)
		res = {
			auth_data[0]: str({
				"score": score,
				"games": games + 1
			})
		}
		data_added = r.mset(res)
		
		if data_added:
			return base.q.jsonify({
				"msg": "Score is submitted.",
			}), 200
			
	except base.sl.IntegrityError:

		return base.q.jsonify({
			"error": "Game score is submitted.",
			"fix": "Create a new game."
		}), 400

@app.route("/leaderboard", strict_slashes=False, methods=["GET"])
async def leaderboard():
	player_list = {}
	for key in r.keys():
		player_list[key.decode("UTF-8")] = ast.literal_eval((r.get(key)).decode("UTF-8"))["score"]
	sorted_player_list = dict(sorted(player_list.items(), key=lambda item: item[1], reverse=True))

	res = {}
	for k, val in enumerate(sorted_player_list):
		res[int(k)+1] = val+" => "+str(sorted_player_list[val])
	while len(res) > 10:
		res.popitem()
	return base.q.jsonify(res), 200
	
		
@app.route("/")
async def main():
	# Return jsonified list of all routes
	return base.q.jsonify({
		"/submitScore": {
			"desc": "Submit game score to redis.",
			"params": {
				"guess_number": "Current guess number.",
				"win": "True if win, False if lose"
			}
		},
		"/leaderboard": {
			"desc": "Get leaderboard.",
		},
	}), 200

if __name__ == "__main__":
	app.run()

