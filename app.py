from flask import Flask
from dotenv import load_dotenv
from auth_blueprint import authentication_blueprint
from user_plots_blueprint import user_plots_blueprint
from plants_blueprint import plants_blueprint
from plot_options_blueprint import plot_options_blueprint
from seed_blueprint import seed_blueprint
from shed_blueprint import shed_blueprint
from store_blueprint import store_blueprint

load_dotenv()

app = Flask(__name__)
app.register_blueprint(authentication_blueprint)
app.register_blueprint(user_plots_blueprint)
app.register_blueprint(plants_blueprint)
app.register_blueprint(plot_options_blueprint)
app.register_blueprint(seed_blueprint)
app.register_blueprint(shed_blueprint)
app.register_blueprint(store_blueprint)

app.run()
