document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("srs-form");
    const userInput = document.getElementById("user-input");
    const srsOutput = document.getElementById("srs-output");
    const planOutput = document.getElementById("plan-output");
    const codeOutput = document.getElementById("code-output");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        // Clear previous output
        srsOutput.innerHTML = "";
        planOutput.innerHTML = "";
        codeOutput.innerHTML = "";

        const formData = new FormData(form);
        
        // Start fetching the stream
        const response = await fetch("/", {
            method: "POST",
            body: formData
        });

        if (!response.body) return;

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let currentSection = null;
        let srsBuffer = "";
        let planBuffer = "";
        let codeBuffer = "";

        async function readStream() {
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                let textChunk = decoder.decode(value, { stream: true });

                // Identify sections based on markers
                if (textChunk.includes("[SRS_START]")) {
                    currentSection = "srs";
                    textChunk = textChunk.replace("[SRS_START]", "");
                }
                if (textChunk.includes("[SRS_END]")) {
                    currentSection = null;
                    textChunk = textChunk.replace("[SRS_END]", "");
                }
                if (textChunk.includes("[PLAN_START]")) {
                    currentSection = "plan";
                    textChunk = textChunk.replace("[PLAN_START]", "");
                }
                if (textChunk.includes("[PLAN_END]")) {
                    currentSection = null;
                    textChunk = textChunk.replace("[PLAN_END]", "");
                }
                if (textChunk.includes("[CODE_START]")) {
                    currentSection = "code";
                    textChunk = textChunk.replace("[CODE_START]", "");
                }
                if (textChunk.includes("[CODE_END]")) {
                    currentSection = null;
                    textChunk = textChunk.replace("[CODE_END]", "");
                }

                // Append the chunk to the correct buffer
                if (currentSection === "srs") {
                    srsBuffer += textChunk;
                    srsOutput.innerHTML = marked.parse(srsBuffer);
                } else if (currentSection === "plan") {
                    planBuffer += textChunk;
                    planOutput.innerHTML = marked.parse(planBuffer);
                } else if (currentSection === "code") {
                    codeBuffer += textChunk;
                    codeOutput.innerHTML = marked.parse(codeBuffer);
                }
            }
        }

        readStream();
    });
});

