This package uses:
- python 3.6 AWS Lamdba
- boto3
- the [schema package](https://github.com/keleshev/schema) for schema validation

# Prerequirements

- **Python 3.6**

- **Serverless toolkit** ([documentation here](https://serverless.com/framework/docs/providers/aws/guide/installation/))


- **AWS credentials** : ([documentation here](https://serverless.com/framework/docs/providers/aws/guide/credentials/))



# Installation

```bash
# clone the repo
git clone https://github.com/quentinf00/serverless-rest.git

# install the dependencies
cd serverless-rest
npm install

# deploy your first api
sls deploy
```

# Usage:

- create a class that's inherit S3Model:

```python
from s3_model import S3Model

class User(S3Model):
    pass
```

- Define the validation schema of the class:

```python
from s3_model import S3Model
from schema import Schema

class User(S3Model):
    SCHEMA = Schema({
        'id': str,
        'first_name': str,
        'last_name': str,
        'birthday': str,
    })
```

- import the Lambda handlers

```
get, post, put, delete, all = User.get_api_methods()
init_schema = User.get_athena_init_schema_handler()
```

- Define the Lambdas in the `serverless.yml`

**API routes**

```yml
  #lambda name
  user_get:
    # python function to be executed
    handler: user.get
    # HTTP route config that will trigger the lambda (HTTP GET on /user/{id})
    events:
      - http:
          path: user/{id}
          method: GET
  user_post:
    handler: user.post
    events:
      - http:
          path: user
          method: POST
  user_delete:
    handler: user.delete
    events:
      - http:
          path: user/{id}
          method: DELETE
  user_put:
    handler: user.put
    events:
      - http:
          path: user/{id}
          method: PUT
  user_list:
    handler: user.all
    events:
      - http:
          path: user/list
          method: GET
```

**Athena table creation setup** (only necessary for the all)

```yml
  user_init_athena_schema:
    handler: user.init_schema
```

- Create the athena table:
```bash
sls invoke local -f user_init_athena_schema
```

- Deploy the api:

```
sls deploy
```

- Bonus: if you want to deploy on multiple environment:

```
sls deploy --stage prod
```

# Api spec:

- GET:
 - takes and id as path parameter and returns the json object


- POST:
 - takes a json object (as body params and  
