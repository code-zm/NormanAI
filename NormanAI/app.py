from flask import Flask, render_template, request, Response
from ollama import Client
import markdown

app = Flask(__name__)
client = Client(host="http://192.168.1.138:11434")

def stream_response(user_input):
    """
    Streams the Mini SRS and Code Generation output in real-time, ensuring correct section separation.
    """

    def generate():
        # Signal the start of Mini SRS
        yield "[SRS_START]\n"

        response_generator_srs = client.generate(
            model="phi4-miniSRS",
            prompt=f"Transform the following user request into a single-paragraph mini SRS:\n\n{user_input}",
            stream=True
        )

        for chunk in response_generator_srs:
            yield chunk['response']

        yield "[SRS_END]\n"  # Mark the end of Mini SRS

        # Signal the start of Generated Code
        yield "[CODE_START]\n"

        response_generator_code = client.generate(
            model="deepseek-dev",
            prompt=f"Generate fully working code based on the following software specification:\n\n{user_input}",
            stream=True
        )

        for chunk in response_generator_code:
            yield chunk['response']

        yield "[CODE_END]\n"  # Mark the end of Generated Code

    return Response(generate(), content_type='text/plain')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["user_input"]
        return stream_response(user_input)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
