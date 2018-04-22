from s3_api_flask import S3FlaskResource
from s3_model import S3Model
from flask import Flask
from flask_restful import Api
from schema import Schema

app = Flask(__name__)
api = Api(app)


class Book(S3Model):
    name = 'book'
    SCHEMA = Schema({
        'id': str,
        'title': str,
        'author': str,
        'publication_date': str,
    })

class BookResource(S3FlaskResource):
    s3_model_class = Book

api.add_resource(BookResource,
    '/book',
    '/book/<string:obj_id>')

app.add_url_rule(
    '/book/list',
    'book_list',
    BookResource.all,
    )

init_schema = Book.get_athena_init_schema_handler()