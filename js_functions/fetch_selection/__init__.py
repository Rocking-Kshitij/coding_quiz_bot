import os
import streamlit.components.v1 as components

_component_func = components.declare_component(
    "fetch_selection",  # component name
    path=os.path.join(os.path.dirname(__file__), "frontend")  # path to frontend folder
)

def fetch_selection():
    return _component_func(default="")
