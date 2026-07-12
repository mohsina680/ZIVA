from src.agentic_studio.tools.files import extract_file_blocks


def test_extract_file_blocks():
    text = """Here is file:\n```file path=my_site/index.html\n<h1>Hello</h1>\n```"""
    blocks = extract_file_blocks(text)
    assert blocks == [("my_site/index.html", "<h1>Hello</h1>")]
