
const API_BASE = "http://localhost:8123"; // change if different

async function ask(question) {
    try {
        const response = await fetch(`${API_BASE}/ask`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: question })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        debugger;

        //const data = await response.json();
        //console.log("Ask result:", data);



        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let result = [];

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            // NLWeb SSE format usually starts with "data: {...}"
            const lines = chunk.split("\n").filter(l => l.startsWith("data:"));
            for (const line of lines) {
                const jsonStr = line.replace(/^data: /, "");
                try {
                    const data = JSON.parse(jsonStr);
                    console.log("Chunk:", data);
                    result.push(data);
                } catch (e) {
                    console.warn("Invalid JSON chunk:", line);
                }
            }
        }

        console.log("Final result:", result);

        dataResults = []

        result.forEach(x => {
            if (x.message_type == "result_batch") {
                dataResults.push(x.results[0]);
            }
        });
        return dataResults;
    } catch (err) {
        console.error("Error calling /ask:", err);
    }
}

// --- Example usage ---
ask("how to display data from a grid in a chart");