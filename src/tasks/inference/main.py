"""App Engine app to serve as an endpoint for App Engine queue samples."""

# [START cloud_tasks_appengine_quickstart]
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/example_task_handler", methods=["POST"])
def example_task_handler():
    """Log the request payload."""
    payload = request.get_data(as_text=True) or "(empty payload)"
    print("Received task with payload: {}".format(payload))
    return render_template("index.html", payload=payload)


@app.route("/")
def hello():
    """Basic index to verify app is serving."""
    return "Hello World!"


if __name__ == "__main__":
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)
