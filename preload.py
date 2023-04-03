def preload(parser):    
    print("Stop Motion CN - Running Preload")
    print("Set Gradio Queue: True")
    parser.set_defaults(gradio_queue=True)