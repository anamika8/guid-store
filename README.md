# guid-store
RESTful web API to maintain a database of GUIDs (Globally Unique Identifier) and associated metadata.

# Technical Specification
- Tornado Web Framework
- MongoDB as permanent data store (hosted by https://account.mongodb.com/)
- Redis as the cache store (hosted by https://redis.com/redis-enterprise-cloud/overview/)

# Project Setup

### Clone Repo
```
git clone git@github.com:anamika8/guid-store.git
cd guid-store
```

### Create virtual environment
```
pip3 install virtualenv

virtualenv venv

source venv/bin/activate
```

### Install dependencies

**Option 1.** Using 'requirements.txt'

```
venv/bin/pip3 install -r requirements.txt
```

**Option 2.** Install manually

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

## Example Requests & Response

GET /

```
curl --location 'localhost:8081'
Welcome to guid-store

```

GET /guid/{guid}

```
curl --location 'localhost:8081/guid/5DEEE113949993C3B0BA781F3EEFC973'
{"_id": "64a27bb99bb3ad0cf9a10536", "user": "Byte, Inc.", "guid": "5DEEE113949993C3B0BA781F3EEFC973", "expire": 1690962105}

```


POST /guid
```
curl --location 'localhost:8081/guid' \
--header 'Content-Type: application/json' \
--data '{
    "user": "PSU",
    "expire": "1690962105"
}'
{"user": "PSU", "expire": "1690962105", "guid": "12EA18F97BFEAAC162035B7509BC90A2", "_id": "64a63b3630b34a3e429b9b6f"}

```

POST /guid/{guid}
```
curl --location 'localhost:8081/guid/9094E4C980C74043A4B586B420E69DDF' \
--header 'Content-Type: application/json' \
--data '{
    "expire": "1690962105",
    "user": "Cylance, Inc."
}'
{"expire": "1690962105", "user": "Cylance, Inc.", "guid": "9094E4C980C74043A4B586B420E69DDF", "_id": "64a63bc830b34a3e429b9b71"}

```


PUT /guid/{guid}

```
curl --location --request PUT 'localhost:8081/guid/9094E4C980C74043A4B586B420E69DDF' \
--header 'Content-Type: application/json' \
--data '{
    "expire": "1690964105",
    "user": "Portland State University"
}'
{"expire": "1690964105", "user": "Portland State University"}

```

DELETE /guid/{guid}

```
curl --location --request DELETE 'localhost:8081/guid/9094E4C980C74043A4B586B420E69DDF' \
--data ''

```