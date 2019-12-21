from flask import Flask
from model import *

# Create a flask app
app = Flask(__name__)
app.url_map.strict_slashes = False

# Regist flask blueprint
app.register_blueprint(auth_api, url_prefix='/auth')
app.register_blueprint(test_api, url_prefix='/test')
app.register_blueprint(profile_api, url_prefix='/profile')
app.register_blueprint(course_api, url_prefix='/course')
app.register_blueprint(submission_api, url_prefix='/submission')
app.register_blueprint(hw_api, url_prefix='/homework')
app.register_blueprint(inbox_api, url_prefix='/inbox')
app.register_blueprint(annn_api, url_prefix='/annn')

if __name__ == '__main__':
    app.run()
