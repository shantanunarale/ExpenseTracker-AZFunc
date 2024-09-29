import azure.functions as func
from function_blueprints import bp

app = func.FunctionApp()
app.register_blueprint(bp)
