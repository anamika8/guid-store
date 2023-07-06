# guid-store
RESTful web API to maintain a database of GUIDs (Globally Unique Identifier) and associated metadata.

## Project Setup

### Create virtual environment
`pip3 install virtualenv`

`virtualenv venv`

`source venv/bin/activate`

### Install dependencies

Option 1. Using 'requirements.txt'

`venv/bin/pip3 install -r requirements.txt`

Option 2. Install manually

```
# Install tornado
venv/bin/pip3 install tornado

# Install pymongo
venv/bin/pip3 install pymongo

# Install redis
venv/bin/pip3 install redis
```

### Starting the server

```
(venv) (base) anamika@Anamikas-Air-36 guid-store % python3 main.py                                                                                  
Starting the webserver

```

### Example Requests & Response

GET /

```
> curl --location 'localhost:8081'
Welcome to guid-store

```

GET /

```
> curl --location 'localhost:8081'
Welcome to guid-store

```