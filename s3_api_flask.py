import json
from s3_model import S3Model
from flask_restful import Resource
from flask import request, jsonify


class S3FlaskResource(Resource):
    s3_model_class = S3Model

    @classmethod
    def get(cls, obj_id):
        return cls.s3_model_class.load(obj_id)

    @classmethod
    def put(cls, obj_id):
        obj = cls.s3_model_class.load(obj_id)

        updates = json.loads(request.data)
        obj.update(updates)

        return cls.s3_model_class.save(obj)

    @classmethod
    def post(cls, ):
        obj = json.loads(request.data)
        if 'id' in obj:
            raise Exception('Do not specify id in resource creation')
        return cls.s3_model_class.save(obj)

    @classmethod
    def delete(cls, obj_id):
        return cls.s3_model_class.delete_obj(obj_id)

    @classmethod
    def all(cls):
        return jsonify(cls.s3_model_class.list_objs())
