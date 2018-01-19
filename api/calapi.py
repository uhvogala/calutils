from flask import Flask, Response, request, render_template, abort, send_from_directory
from flask_restful import reqparse, Api, Resource
from werkzeug.datastructures import FileStorage
from tempfile import TemporaryFile
from jinja2.exceptions import TemplateNotFound

from calrepair.caleditor import CalEditor

import os

app = Flask(__name__, template_folder='../app')
api = Api(app)

caled = CalEditor()

class LoadCalendar(Resource):
    
    parser = reqparse.RequestParser()
    parser.add_argument('file', type=FileStorage, location='files')
    
    
    def post(self):
        args = self.parser.parse_args()
        if args['file']:
            try:
                caled.load_calendar_file(args['file'])
                caled.fix_calendar()
                caled.merge_recurring_events()
                return {'upload':'success'}, 201
            except Exception as e:
                print(e)
        return {'upload': 'fail'}, 400
    
    def get(self):
        if not caled.is_empty():
            json_str = caled.export_json_str(caled.cal)
            return Response(json_str, mimetype='application/json')
        return None, 204

class ExportCalendar(Resource):
    
    parser = reqparse.RequestParser()
    
    def post(self):
        user_json = request.get_json()
        if user_json:
            try:
                caled.json_to_ical(str(user_json).replace("'", '"'))
                return {'upload': 'success'}, 201
            except Exception as e:
                print(e)
                raise
        return {'upload': 'fail'}, 400
    
    def get(self):
        if not caled.is_empty():
            return Response(caled.export_calendar_str(), 
                            mimetype='text/plain')
        return None, 204
        
api.add_resource(LoadCalendar, '/calapp/api/load')
api.add_resource(ExportCalendar, '/calapp/api/export')

@app.route("/calapp")
def main_page():
    return render_template('index.html')

@app.route("/calapp/<filename>")
@app.route("/calapp/<path>/<filename>")
def app_files(filename, path=None):
    if path:
        filename = os.path.join(path, filename)
    try:
        if filename.endswith('.css'):
            return send_from_directory('../app/', filename)
        return render_template(filename)
    except TemplateNotFound as e:
        print(e)
    abort(404)


