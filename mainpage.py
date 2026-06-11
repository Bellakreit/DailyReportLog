import gradio as gr

with gr.Blocks() as demo:
    gr.HTML(value="<h1>Daily report log</h1>")

if __name__ == "__main__":
    demo.launch()