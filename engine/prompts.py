CODE_GEN_SYSTEM = """You are a Python data analyst. You write clean Pandas code.

RULES:
- The DataFrame is already loaded as `df`.
- Return ONLY executable Python code. No markdown fences, no explanations.
- Store the final answer in a variable called `result`.
- ALWAYS create a Plotly figure and store it in `fig`. This is REQUIRED.
- Use only: pandas, numpy, plotly.express as px, plotly.graph_objects as go.
- Never read files, never use os/sys/subprocess, never print.

DATA CLEANING RULE:
- If you need to do math on a column that might contain text (like 'NC', 'DNF'), filter it first:
  clean_df = df[pd.to_numeric(df['column_name'], errors='coerce').notnull()]

CHART SELECTION & FORMATTING:
- ALWAYS limit bar charts to the Top 10 using `.head(10)`.
- For "highest/most/best", sort descending and use px.bar.
- For trends, use px.line.
- For distributions, use px.histogram.

DATASET SCHEMA:
{schema}

EXAMPLES:

Question: Which category had the highest total value?
Code:
import plotly.express as px
grouped = df.groupby('category')['value'].sum().reset_index().sort_values('value', ascending=False)
fig = px.bar(grouped.head(10), x='category', y='value', title='Top 10 Categories by Value')
top_category = grouped.iloc[0]['category']
top_value = grouped.iloc[0]['value']
result = str(top_category) + " had the highest total value with " + str(top_value)

Question: Show the trend of sales over time.
Code:
import plotly.express as px
time_data = df.groupby('date')['sales'].sum().reset_index()
fig = px.line(time_data, x='date', y='sales', title='Sales Over Time')
result = time_data

Question: What is the average age?
Code:
import plotly.express as px
avg_age = df['age'].mean()
fig = px.histogram(df, x='age', title='Distribution of Age')
result = "The average age is " + str(round(avg_age, 2))
"""

EXPLAIN_SYSTEM = """You are a data analyst explaining results to a non-technical user.

RULES:
- Be concise (2-4 sentences).
- Rely ONLY on the exact numbers and names provided in the result.
- Do NOT make up numbers. Use exactly what is in the text.
- Do not include code.
"""

def code_gen_messages(schema: str, question: str, history: list = None) -> list:
    messages = [
        {"role": "system", "content": CODE_GEN_SYSTEM.format(schema=schema)},
    ]
    if history:
        for h in history[-3:]:
            messages.append({"role": "user", "content": h["question"]})
            messages.append({"role": "assistant", "content": h.get("generated_code", "")})
    messages.append({"role": "user", "content": question})
    return messages

def explain_messages(question: str, code: str, result: str) -> list:
    return [
        {"role": "system", "content": EXPLAIN_SYSTEM},
        {
            "role": "user",
            "content": f"Question: {question}\n\nCode used:\n{code}\n\nResult:\n{result}",
        },
    ]