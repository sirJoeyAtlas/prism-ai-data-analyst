import pandas as pd


def profile_dataframe(df: pd.DataFrame) -> dict:
    profile = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_info": {},
        "missing": df.isnull().sum().to_dict(),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
    }

    for col in df.columns:
        info = {"dtype": str(df[col].dtype), "missing": int(df[col].isnull().sum())}
        if pd.api.types.is_numeric_dtype(df[col]):
            info.update({
                "min": float(df[col].min()) if not df[col].isnull().all() else None,
                "max": float(df[col].max()) if not df[col].isnull().all() else None,
                "mean": float(df[col].mean()) if not df[col].isnull().all() else None,
            })
        else:
            info["unique"] = int(df[col].nunique())
            info["sample"] = df[col].dropna().unique()[:5].tolist()
        profile["column_info"][col] = info

    return profile


def profile_to_text(profile: dict) -> str:
    lines = [
        f"Rows: {profile['rows']}, Columns: {profile['columns']}",
        "",
        "Columns:",
    ]
    for col, info in profile["column_info"].items():
        line = f"- {col} ({info['dtype']}), missing: {info['missing']}"
        if "min" in info and info["min"] is not None:
            line += f", min: {info['min']:.2f}, max: {info['max']:.2f}, mean: {info['mean']:.2f}"
        elif "unique" in info:
            line += f", unique: {info['unique']}, sample: {info['sample']}"
        lines.append(line)
    return "\n".join(lines)