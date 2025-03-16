import streamlit as st
from streamlit_ace import st_ace

st.title("Streamlit Ace Code Editor")

# Add the Ace editor
content = st_ace(
    value="print('Hello, World!')",  # Default code
    language="plain_text",               # Language mode
    theme="monokai",                 # Editor theme
    keybinding="vscode",             # Keybindings
    font_size=14,                     # Font size
    tab_size=4,                        # Tab size
    show_gutter=True,                  # Show line numbers
    wrap=True,                          # Enable line wrapping
    auto_update=True,                   # Auto update output
    min_lines=5,                        # Min number of lines
    max_lines=20                        # Max number of lines
)

# Display the code output
st.write("You wrote:")
st.code(content, language="python")
