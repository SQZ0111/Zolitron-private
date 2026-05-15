# Zolitron

The project is about ...



## Setup
Prerequisites: Python and node installed in maschine
- [**Node.js**](https://nodejs.org/)

- [**Python**](https://www.python.org/downloads/)

Verify then in a terminal with:

```bash
node --version
npm --version
python --version
```

1. `git clone <url>`
2. On your local maschine open the project with your editor of choice.
3. Recommended: Open at least  three shells from your terminal. One for running the front- & backend, one for workings on client and one for backend workings (installations).




### Windows

```bash
Run `npm i` in the root directory first.

# Create virtual environment and install all dependencies
npm run setup:win

# Start both client and server
# Run `npm run dev` to run the app. The client is on `http://localhost:5173/` the backend on `http://127.0.0.1:8000`
npm run dev

```

### Mac


```bash

#Run `npm i` in the root directory first.
npm i

#create virtualenv and activate virtualenv in backend
npm run venv:activate:mac

# Create virtual environment and install all dependencies
npm run setup:mac

# Start both client and server
# Run `npm run dev` to run the app. The client is on `http://localhost:5173/` the backend on `http://127.0.0.1:8000`

npm run dev

```


## Explaination App

### Overview
*Note that the backend is now updated to FastApi. Though the general flow still applies.*


![flowchart](./doc-imgs/flowchart.png)
*!TODO BE UPDATE! A perspective on the app from client request over the backend and database.*

<hr>



## Backend (Monolith)
Why repository pattern:
- abstract the data layer from the processing layer
- data sources can vary in future 
- diffrent queries from client to search (e.g city, postal code...)

An Example:
```python
class CityRepository:
    #initialise db session 
    def __init__(self, db: Session):
        self.db = db
    
    # Method that returns City by postal code (city will have foreign key to get corresponding images)
    def get_by_postal(self, code: int) -> City:
        return self.db.query(City).filter(City.postal == postal)

    #more query methods
```
A alternative consideration was to just use QueryBuilder and a DataRetriever singletons but that would result in violating open-closed.  

Everything regarding the actual business logic (ML-Model and actual processing) is similiar as [service layers](https://martinfowler.com/eaaCatalog/serviceLayer.html)

Technologies used:

- Python + FastAPI – web framework (request/response handling)

- SQLAlchemy – ORM and query builder 

- SQLite – database

- Pydantic – request/response validation

- TensorFlow – pre‑trained ML model for waste classification

- Pillow - Image loading


## Common problems

##### Installed modules can not be recognized in python code:
If you have problems regarding the import of the modules (does not recognize the module although you installed it prior with virtualenv activated) this will probably help you:
1. Check if you installed the package with `pip list`
2. Check which *python.exe* is used with `where python` (Windows) or `which python` (Linux/Mac). If you get multiple outputs than step 3 is necessary. 
3. Select the correct interpreter in IDE. 
    - Open the Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
    - Type Python: Select Interpreter
    - Type in the path from the output of step 2. Should be something like this `<other-paths>\Zolitron\backend\venv\Scripts\python.exe` 