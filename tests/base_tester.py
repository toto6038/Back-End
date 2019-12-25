from mongoengine import connect
from mongo import *
from mongo import engine, add_problem
from .conftest import *


class BaseTester:
    MONGO_HOST = 'mongomock://localhost'
    DB = 'normal-oj'
    USER_CONFIG = 'tests/user.json'

    @classmethod
    def drop_db(cls):
        conn = connect(cls.DB, host=cls.MONGO_HOST)
        conn.drop_database(cls.DB)

    @classmethod
    def setup_class(cls):
        cls.drop_db()

        with open(cls.USER_CONFIG) as f:
            import json
            config = json.load(f)
            users = {}
            tcls = cls
            while True:
                users.update(config.get(tcls.__name__, {}))
                if tcls.__name__ == 'BaseTester':
                    break
                tcls = tcls.__base__

            for name, role in users.items():
                cls.new_user(name, role)

        if Number("serial_number").obj is None:
            engine.Number(name="serial_number").save()

        for i in range(5):
            cls.new_problem()

    @classmethod
    def teardown_class(cls):
        cls.drop_db()

    @classmethod
    def new_user(cls, username, role):
        USER = {
            'username': username,
            'password': f'{username}_password',
            'email': f'i.am.{username}@noj.tw'
        }

        user = User.signup(**USER)
        user.update(active=True,
                    role=role,
                    profile={
                        'displayedName': '',
                        'bio': ''
                    })

    @classmethod
    def new_problem(cls):
        add_problem(
            user = User("admin"),
            status = 0,
            type = 1,
            problem_name = 'Test problem name',
            description = 'Test description.',
            tags = ['TestTag01', 'TestTag02'],
            test_case = {
                'language': 2,
                'fillInTemplate': 'Test f__l in t__pl__e.',
                'cases': [{
                    'input': 'TestInput01',
                    'output': 'TestOutput01',
                    'caseScore': 1,
                    'memoryLimit': 1,
                    'timeLimit': 1
                }]})

    @staticmethod
    def request(client, method, url, **ks):
        func = getattr(client, method)
        rv = func(url, **ks)
        rv_json = rv.get_json()
        rv_data = rv_json['data']

        return rv, rv_json, rv_data
