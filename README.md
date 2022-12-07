# CPSC449-> Project3 Group8
## Wordle-cpsc449

Team Members:  
1. Shivangi Shakya. 
2. Carter Loya. 
3. Juan Sierra. 
4. Trung Tran. 

### DESCRIPTION.
In this project, our team was able to effectively build a back-end API for a game quite similar to the popular game "Wordle", with the exception of a few conditions that the original game is known for. Some of these features include allowing more than one game to be played per day per player, as well offering different games to different players. We have also implemented scoring and maintaing the leaderboard.

This web service has 3 microservices called userapp, gameapp and scoreapp, which leverage Python's Quart web framework, and utilize 9 main endpoints (described below) to simulate a user interacting with the game and submit the score of games and show leaderboard. Also, our web services makes use of NginX for effective HTTP Authentication, as well as load balancing (which all gets shown in the command line throughout execution). scoreapp uses REDIS for storing the scores for a particular user. Leaderboard is based on the average scores of all the games played by a particular user.

### GETTING STARTED:
1. TO LAUNCH THE SERVICE:  
From the command line of the project directory, simply run   
```bash
foreman start
```
  
if error: Already running process, run below steps:  
```bash
lsof -ti tcp:5000 | xargs kill
```
and
```bash
lsof -ti tcp:5100 | xargs kill
```
and
```bash
lsof -ti tcp:5200 | xargs kill
```
and
```bash
lsof -ti tcp:5300 | xargs kill
```
and
```bash
lsof -ti tcp:5400 | xargs kill
```

2. From the command line of the project directory, run the following commands to init/populate the database:  
```bash
./bin/start.sh
```


### ENDPOINT 1: Register a new user:  
- This endpoint is used for registering a user/creating an account for a user to authenticate themselves.
- ex:
```bash
http POST http://asd:asd123@tuffix-vm/auth/regist
```  

### ENDPOINT 2: Login:
- This endpoint is used for login a user for authentication.
- ex:
```bash
http POST http://asd:asd123@tuffix-vm/auth/login
```  

### ENDPOINT 3: Start a game:
- This endpoint is used to start a new game for an authenticated user.
- ex:
```bash
http POST http://asd:asd123@tuffix-vm/game/start
```  

### ENDPOINT 4: List games for a user:
- This endpoint is used to list all the games for a user.
- ex:
```bash
http POST http://asd:asd123@tuffix-vm/game/list
```  

### ENDPOINT 5: Guess word:
- This endpoint is used to guess the word for a game of a user.
- ex:
```bash
http POST http://asd:asd123@tuffix-vm/game/submit word=stuff game_id=<game_id>
```  

### ENDPOINT 6: Get the game status:
- This endpoint is used to get the status for a game of a user.
- ex:
```bash
http POST http://asd:asd123@tuffix-vm/game/state game_id=<game_id>
```  

### ENDPOINT 7: Delete a game:
- This endpoint is used to delete a game of a user.
- ex:
```bash
http POST http://asd:asd123@tuffix-vm/game/delete game_id=<game_id>
```  

### ENDPOINT 8: Submit Score:
- This endpoint is used to submit the score for a game of a user to REDIS.
- ex:
```bash
http POST http://asd:asd123@127.0.0.1:5400/submitScore guess_number=1 win="True"
``` 

### ENDPOINT 9: Show leaderboard:
- This endpoint is used to show the leaderboard of all the games.
- ex:
```bash
http GET http://127.0.0.1:5400/leaderboard
``` 

