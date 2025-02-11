from flask import Flask, render_template, request, Response
from ollama import Client

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
        srs_output= ""
        for chunk in response_generator_srs:
            srs_output += chunk['response']
            yield chunk['response']

        yield "[SRS_END]\n"  # Mark the end of Mini SRS

        yield "[PLAN_START]\n"

        response_generator_plan = client.generate(
            model="phi4-planner",
            prompt=f"Below is a detailed description of a software project. Please transform this paragraph into a comprehensive, step-by-step implementation plan that includes requirements analysis, environment setup, architectural design, detailed coding steps, testing/debugging strategies, and suggestions for documentation and future enhancements.\n\n{srs_output}",
            stream=True
            )
        plan_output=""
        for chunk in response_generator_plan:
            plan_output += chunk['response']
            yield chunk['response']

        yield "[PLAN_END]\n"

        # Signal the start of Generated Code
        yield "[CODE_START]\n"

        response_generator_code = client.generate(
            model="deepseek-dev",
            prompt=f"Generate fully working code based on the following software implementation plan:\n\n{plan_output}",
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
