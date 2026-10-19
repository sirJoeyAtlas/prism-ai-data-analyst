import re
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# Pre-inject everything the LLM might try to import
ALLOWED_GLOBALS = {
    "pd": pd,
    "pandas": pd,
    "np": np,
    "numpy": np,
    "px": px,
    "go": go,
}


def safe_builtins():
    import builtins
    allowed = [
        "len", "range", "min", "max", "sum", "abs", "round", "sorted",
        "list", "dict", "set", "tuple", "str", "int", "float", "bool",
        "enumerate", "zip", "map", "filter", "any", "all",
    ]
    builtins_dict = {name: getattr(builtins, name) for name in allowed}
    
    # Add a dummy print function to prevent NameError if the AI tries to use print()
    builtins_dict["print"] = lambda *args, **kwargs: None
    
    return builtins_dict


def strip_imports(code: str) -> str:
    """Remove any `import ...` or `from ... import ...` lines. All needed
    modules are already injected into globals."""
    lines = []
    for line in code.split("\n"):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            continue
        lines.append(line)

    # Remove leading blank lines that might confuse the parser
    while lines and not lines[0].strip():
        lines.pop(0)

    return "\n".join(lines)


def normalize_result(value):
    """Convert numpy/pandas types into Python-native types so they render safely."""
    import numpy as np
    import pandas as pd

    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, np.ndarray):
        return pd.Series(value)
    return value


def execute_code(code: str, df: pd.DataFrame) -> dict:
    clean = strip_imports(code)

    print("\n" + "=" * 60)
    print("EXECUTING CODE:")
    print("-" * 60)
    print(clean)
    print("=" * 60 + "\n")

    local_env = {"df": df.copy(), "result": None, "fig": None}
    globals_env = {"__builtins__": safe_builtins(), **ALLOWED_GLOBALS}

    try:
        exec(clean, globals_env, local_env)

        result = normalize_result(local_env.get("result"))
        fig = local_env.get("fig")

        return {
            "success": True,
            "result": result,
            "fig": fig,
            "error": None,
        }
    except SyntaxError as e:
        bad_line = ""
        if e.lineno and e.lineno <= len(clean.split("\n")):
            bad_line = clean.split("\n")[e.lineno - 1]
        return {
            "success": False,
            "result": None,
            "fig": None,
            "error": f"SyntaxError on line {e.lineno}: {e.msg}\n→ Offending line: {bad_line!r}",
        }
    except Exception as e:
        return {
            "success": False,
            "result": None,
            "fig": None,
            "error": f"{type(e).__name__}: {e}",
        }

def result_to_text(result) -> str:
    if result is None:
        return "No result returned."
    if isinstance(result, pd.DataFrame):
        return result.head(20).to_string()
    if isinstance(result, pd.Series):
        return result.head(20).to_string()
    return str(result)


def auto_chart(result, df):
    """If the LLM didn't produce a chart, try to make one from the result."""
    try:
        # Case 1: DataFrame with 2+ columns
        if isinstance(result, pd.DataFrame) and len(result.columns) >= 2:
            x_col = result.columns[0]
            y_col = result.columns[1]
            if pd.api.types.is_datetime64_any_dtype(result[x_col]):
                return px.line(result, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
            return px.bar(result, x=x_col, y=y_col, title=f"{y_col} by {x_col}")

        # Case 2: Series → bar chart
        if isinstance(result, pd.Series):
            s = result.reset_index()
            return px.bar(s, x=s.columns[0], y=s.columns[1], title="Result")

        # Case 3: Scalar (number or string) → show the relevant distribution
        if isinstance(result, (int, float, str)):
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            cat_cols = df.select_dtypes(include='object').columns.tolist()

            # Prefer a bar chart by category
            if numeric_cols and cat_cols:
                col = numeric_cols[0]
                cat = cat_cols[0]
                grouped = (
                    df.groupby(cat)[col].sum()
                    .reset_index()
                    .sort_values(col, ascending=False)
                    .head(10)
                )
                return px.bar(grouped, x=cat, y=col, title=f"{col.capitalize()} by {cat.capitalize()}")

            # If only numeric columns exist, show a histogram of the first one
            if numeric_cols:
                return px.histogram(df, x=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")

            # Absolute fallback: row count chart
            return px.bar(
                x=["Rows", "Columns"],
                y=[len(df), len(df.columns)],
                title="Dataset Size",
            )
    except Exception as e:
        print(f"auto_chart error: {e}")
        return None

    return None