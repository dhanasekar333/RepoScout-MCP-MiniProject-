import sqlite3
from fastmcp import FastMCP
from pathlib import Path

# Create the server
mcp = FastMCP("reports")

# 1. Open (or create) the database file and make the table once
DB_PATH = Path(__file__).parent / "reports.db"
db = sqlite3.connect(DB_PATH, check_same_thread=False)
db.execute(
    "CREATE TABLE IF NOT EXISTS reports ("
    "id INTEGER PRIMARY KEY AUTOINCREMENT, repo TEXT, title TEXT, content TEXT)"
)
db.commit()

# 2. Tool: save a finished report
@mcp.tool()
def save_report(repo: str, title: str, content: str) -> str:
    """Save a finished research report about a GitHub repo. Returns the report id."""
    cursor = db.execute(
        "INSERT INTO reports (repo, title, content) VALUES (?, ?, ?)",
        (repo, title, content),
    )
    db.commit()
    return f"Saved report with id {cursor.lastrowid}"

# 3. Tool: list saved reports
@mcp.tool()
def list_reports() -> str:
    """List all saved reports (id, repo, title)."""
    rows = db.execute("SELECT id, repo, title FROM reports").fetchall()
    if not rows:
        return "No reports saved yet."
    return "\n".join(f"{r[0]}: {r[1]} - {r[2]}" for r in rows)

# 4. Tool: read one report
@mcp.tool()
def get_report(report_id: int) -> str:
    """Get the full text of a saved report by id."""
    row = db.execute(
        "SELECT title, content FROM reports WHERE id = ?", (report_id,)
    ).fetchone()
    if row is None:
        return "No report with that id."
    return f"{row[0]}\n\n{row[1]}"

if __name__ == "__main__":
    mcp.run()