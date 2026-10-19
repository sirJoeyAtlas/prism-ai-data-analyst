# Local AI Data Intelligence 🔮

A privacy-first, natural language data analysis tool. Upload a dataset, ask questions in plain English, and get automated Pandas code, interactive Plotly charts, and plain-English explanations. 

**All AI inference runs 100% locally** using Ollama. Data history is saved to a local Microsoft SQL Server database. No data ever leaves the machine.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **AI Engine:** Ollama (`qwen2.5-coder`, `qwen2.5`)
- **Data Processing:** Pandas, Plotly
- **Database:** Microsoft SQL Server (via `pyodbc`)

## 🚀 Setup Instructions (Local)

### 1. Prerequisites
- Python 3.10+
- [Ollama installed and running](https://ollama.com/)
- Microsoft SQL Server Express & SSMS installed
- ODBC Driver 18 for SQL Server installed

### 2. Pull the AI Models
```bash
ollama pull qwen2.5-coder:3b
ollama pull qwen2.5:3b