import graphviz

# Create a directed graph
dot = graphviz.Digraph(format="png")

# Define nodes
dot.node("Start", "User Starts Quiz", shape="ellipse", style="filled", fillcolor="lightblue")
dot.node("User_ID", "Enter User ID", shape="parallelogram", style="filled", fillcolor="lightgrey")
dot.node("Fetch_Skills", "Fetch Skills from DB", shape="box", style="filled", fillcolor="lightgrey")
dot.node("Find_Weak", "Identify Weak Areas", shape="box", style="filled", fillcolor="lightgrey")
dot.node("Generate_Q", "Generate Question\n(LLM based on Weak Areas)", shape="diamond", style="filled", fillcolor="lightcoral")
dot.node("Show_Q", "Show Question to User", shape="ellipse", style="filled", fillcolor="lightblue")
dot.node("Get_Answer", "User Submits Answer", shape="parallelogram", style="filled", fillcolor="lightgrey")
dot.node("Evaluate", "LLM Evaluates Answer", shape="box", style="filled", fillcolor="lightcoral")
dot.node("Store_Result", "Store Quiz History in DB", shape="box", style="filled", fillcolor="lightgrey")
dot.node("Update_Weak", "Update Weak Areas", shape="box", style="filled", fillcolor="lightgrey")
dot.node("Find_Similar", "Find Similar Questions\n(PGVector Search)", shape="box", style="filled", fillcolor="lightgrey")
dot.node("Next_Q", "Generate Next Question", shape="diamond", style="filled", fillcolor="lightcoral")
dot.node("End", "End of Quiz", shape="ellipse", style="filled", fillcolor="lightblue")

# Define edges (process flow)
dot.edge("Start", "User_ID")
dot.edge("User_ID", "Fetch_Skills")
dot.edge("Fetch_Skills", "Find_Weak")
dot.edge("Find_Weak", "Generate_Q")
dot.edge("Generate_Q", "Show_Q")
dot.edge("Show_Q", "Get_Answer")
dot.edge("Get_Answer", "Evaluate")
dot.edge("Evaluate", "Store_Result")
dot.edge("Store_Result", "Update_Weak")
dot.edge("Update_Weak", "Find_Similar")
dot.edge("Find_Similar", "Next_Q")
dot.edge("Next_Q", "Show_Q", label="Loop Until Exit")
dot.edge("Next_Q", "End", label="User Stops")

# Render the graph
dot_path = "/mnt/data/ai_quiz_flow"
dot.render(dot_path)
dot_path + ".png"
