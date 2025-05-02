from langchain.prompts import PromptTemplate

Evaluate_summary_prompt = """

You are an expert evaluator acting as an LLM-based judge. Your goal is to assess the quality of a generated **summary** based on a given **document** and a generic **instruction** such as "Summarize this document".

### Input:
- **Query**: usually a summarization instruction like "Summarize this document".
- **Context**: the source document content.
- **Summary**: the generated summary to be evaluated.

### Evaluation Metrics:

- **Faithfulness (Summary ↔ Context)**: Is all information in the summary supported by the context? No hallucination?
  - Avoid rewarding summaries that add information not present in the context or omit critical details.
  
- **Readability**: Is the summary clear, well-written, and easy to read?
  - The summary should flow logically, be well-structured, and maintain clarity throughout.

- **Coverage**: Does the summary cover the most important and relevant points of the context?
  - It should not skip over key information, such as numerical data, dates, or smaller yet important facts.

- **Noise Robustness**: Does the summary avoid irrelevant or low-quality parts of the context?
  - No inclusion of off-topic information, irrelevant facts, or redundancy.

Each metric should be scored from **0.0 (very poor)** to **1.0 (excellent)**.

### Rules:
{rules}

### Step-by-step Evaluation Guidelines:
{guidelines}


Evaluate the following:

Query: \"\"\"{query}\"\"\"  
Context: \"\"\"{context}\"\"\"  
Summary: \"\"\"{summary}\"\"\"  

### Return only the following JSON:

Output = {{
  "faithfulness_score": float (0.0 to 1.0),
  "readability_score": float (0.0 to 1.0),
  "coverage_score": float (0.0 to 1.0),
  "noise_robustness_score": float (0.0 to 1.0),
  "faithfulness_reasoning": "short justification (max 300 characters)",
  "readability_reasoning": "short justification (max 300 characters)",
  "coverage_reasoning": "short justification (max 300 characters)",
  "noise_robustness_reasoning": "short justification (max 300 characters)"
}}
"""

rules = """- Do not reward summaries that invent facts or omit critical details.
- All content must be verifiable in the context.
- The summary should be fluent and well-structured.
- Irrelevant or low-quality input segments must not pollute the summary.
- A good summary captures the core ideas without excessive detail."""

guidelines = """
1. Read the context (document) and extract the key facts and ideas.
2. Examine the summary and check if it matches the context (Faithfulness).
3. Evaluate grammar, clarity, and structure (Readability).
4. Assess if it covers the important parts of the context (Coverage).
5. Check if it ignores irrelevant or noisy content (Noise Robustness).
6. Assign a score from 0.0 to 1.0 for each metric.
7. Add a short explanation (max 300 characters) for each score.
"""

evaluate_summary_template = PromptTemplate(
    template=Evaluate_summary_prompt,
    input_variables=["rules", "guidelines", "query", "context", "summary"]
)
