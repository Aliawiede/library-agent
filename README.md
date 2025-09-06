# Agentic-Ai-Challange

this is Ai Agent with local chat interface for Library desk agent.

## Setup Enviroment 

create new enviroment 

'''bash
 python3 -m venv name_of_environment 



then to activate this environment

'''bash 
 source name_of_environment/bin/activate


## Install Library

all requirements in file requirements.txt to install that you need to check you are in env and then in terminal write 

pip install -r requirements.txt

## Secret key 

 make a new file from .env. example and put your keys

 open cli and write 

 '''bash 
  cp .env.example .env
 
## 

### Make DATABASE and seed 

go to db file write 

'''bash 
 sqlite3 db/library.db < db/schema.sql
 sqlite3 db/library.db < db/seed.sql


### Start the FastAPI backend
'''bash
 uvicorn api:app --reload --host 0.0.0.0 --port 8000

### Start the Gradio interface
then

'''bash
 python3 app.py
