import gradio as gr

import mainpage, secondpage

with gr.Blocks() as demo:
    mainpage.demo.render()
with demo.route("Second Page"):
    secondpage.demo.render()

if __name__ == "__main__":
    demo.launch()