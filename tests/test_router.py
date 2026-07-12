from src.agentic_studio.router import classify_task


def test_documentation_route():
    assert classify_task("Create a report with introduction and conclusion", "runbooks/documentation/x.md") == "documentation"


def test_coding_route():
    assert classify_task("Create index.html style.css and script.js", "runbooks/coding/x.md") == "coding"


def test_design_route():
    assert classify_task("Create UI design, color palette and layout", "runbooks/design/x.md") == "web_design"
