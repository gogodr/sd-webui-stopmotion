import modules.scripts as scripts
from modules.processing import process_images, Processed
from modules.shared import cmd_opts, opts
from modules import errors
from PIL import Image
import numpy as np
import gradio as gr
import os
import io
import importlib
import modules.images
controlnet_module = importlib.import_module(
    'extensions.sd-webui-controlnet.scripts.external_code', 'external_code')
cn_models = controlnet_module.get_models()
max_models = opts.data.get("control_net_max_models_num", 1)

controlsMap = {
    "CN_SELECTOR": None,
    "TAB-1": {
    },
    "TAB-2": {
    },
    "TAB-3": {
    },
    "TAB-4": {
    },
    "TAB-5": {
    },
}


def convertDataUriToImage(data_uri):
    from urllib import request
    with request.urlopen(data_uri) as response:
        data = response.read()
        img = Image.open(io.BytesIO(data))
        return img


def merge_frames(files):
    frames = [Image.open(file.name) for file in files]
    print(f"GIF duration: {len(files)*5}")
    frames[0].save('aux_cn.gif', format='GIF', save_all=True,
                   append_images=frames[1:], optimize=False, duration=len(files)*5, loop=0)
    yield gr.Image.update(value='aux_cn.gif')
    os.remove('aux_cn.gif')

def save_gif(p, frames):
    outpath = os.path.join(p.outpath_samples, "cn_stopmotion")    
    gif_filename = (modules.images.save_image(frames[0], outpath, "gif2gif", extension = 'gif')[0])    
    frames[0].save(gif_filename,
        save_all = True, append_images = frames[1:], loop = 0,
        optimize = False, duration = len(frames)*5)
    return gif_filename


def createTab(i):
    with gr.Tab(label=f"ControlNet ({i})", elem_id=f"smcn-tab-{i}", id=f"tab-{i}") as tab:
        controlsMap[f"TAB-{i}"]["TAB"] = tab
        files = None
        animation = None

        dropwdown = gr.Dropdown(choices=cn_models,
                                value=cn_models[0], label="ControlNet Model", interactive=True)
        controlsMap[f"TAB-{i}"]["CN_MODEL"] = dropwdown

        with gr.Row():

            cn_guidance_start = gr.Slider(label="Guidance Start", value=0, step=0.1, minimum=0,
                                          maximum=1,  interactive=True, elem_classes="cn_controls")
            controlsMap[f"TAB-{i}"]["CN_G_START"] = cn_guidance_start

            cn_guidance_end = gr.Slider(label="Guidance End", value=1, step=0.1, minimum=0,
                                        maximum=1,  interactive=True, elem_classes="cn_controls")
            controlsMap[f"TAB-{i}"]["CN_G_END"] = cn_guidance_end

            cn_weight = gr.Slider(label="Weight", value=1, step=0.1, minimum=0,
                                  maximum=2,  interactive=True, elem_classes="cn_controls")
            controlsMap[f"TAB-{i}"]["CN_WEIGHT"] = cn_weight

        with gr.Row():
            with gr.Column(elem_classes="column"):
                files = gr.File(label="Upload Frames", visible=True, file_types=[
                                '.png', '.jpg', '.jpeg'], file_count="multiple")
                controlsMap[f"TAB-{i}"]["FILES"] = files
            with gr.Column(elem_classes="column"):
                animation = gr.Image(
                    interactive=False, label="Animation", shape=(None, 400))
                controlsMap[f"TAB-{i}"]["PREVIEW"] = animation

    files.upload(fn=merge_frames,
                 inputs=controlsMap[f"TAB-{i}"]["FILES"], outputs=controlsMap[f"TAB-{i}"]["PREVIEW"])
    return tab


def createTabs(amount):
    tab_components = []
    for i in range(1, amount+1):# Creating a tab for each control net module.    
        tab_components.append(createTab(i))
    return tab_components


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

css = ""
with open(os.path.join(__location__, 'style.css')) as f:
    css = "\n".join(f.readlines())

js = ""
with open(os.path.join(__location__, 'script.js')) as f:
    js = "\n".join(f.readlines())


class Script(scripts.Script):
    def title(self):
        return "Stop Motion CN"

    def show(self, is_img2img):
        return True

    def ui(self, is_img2img):
        with gr.Blocks(css=css) as demo:
            gr.Markdown('''
            # ControlNet Stop Motion Animation
            ''')
            with gr.Column(elem_id="smcn-main_container"):
                with gr.Row():
                    cn_amount = gr.Slider(value=1, step=1, minimum=1,
                                          maximum=max_models, label="ControlNet Modules", interactive=True)
                    controlsMap[f"CN_SELECTOR"] = cn_amount

                    fps = gr.Slider(value=12, step=1, minimum=1,
                                    maximum=60, label="Frames per second", interactive=True)
                    controlsMap[f"FPS"] = fps
                with gr.Column(elem_id="smcn-tabs_container"):
                    with gr.Tabs(elem_id="smcn-tabs"):
                        createTabs(max_models)

            controlsMap[f"CN_SELECTOR"].change(fn=None,
                                               inputs=controlsMap[f"CN_SELECTOR"], outputs=None, _js="(index)=>window.smcn_updateTabs(index)")

            demo.load(_js="()=>{const css = `"+css+"`;\n"+js+"}")

        args = []
        cn_modules = controlsMap[f"CN_SELECTOR"]
        args.append(cn_modules)
        fps = controlsMap[f"FPS"]
        args.append(fps)
        for cn_mod in range(1, max_models+1):
            cn_model = controlsMap[f"TAB-"+str(cn_mod)]["CN_MODEL"]
            args.append(cn_model)
            guidance_start = controlsMap[f"TAB-"+str(cn_mod)]["CN_G_START"]
            args.append(guidance_start)
            guidance_end = controlsMap[f"TAB-"+str(cn_mod)]["CN_G_END"]
            args.append(guidance_end)
            weight = controlsMap[f"TAB-"+str(cn_mod)]["CN_WEIGHT"]
            args.append(weight)
            files = controlsMap[f"TAB-"+str(cn_mod)]["FILES"]
            args.append(files)
        return args

    def run(self, p, *args):
        frames = []
        gif_frames = []
        initial_seed = None
        initial_info = None
        args_map = {}
        args_map["cn_modules"] = args[0]
        args_map["fps"] = args[1]
        index = 0
        frame_count = None
        for cn_mod in range(1, args_map["cn_modules"]+1):
            args_map[f"cn-{cn_mod}"] = {}
            args_map[f"cn-{cn_mod}"]["model"] = args[2+(index*5)]
            args_map[f"cn-{cn_mod}"]["guidance_start"] = args[3+(index*5)]
            args_map[f"cn-{cn_mod}"]["guidance_end"] = args[4+(index*5)]
            args_map[f"cn-{cn_mod}"]["weight"] = args[5+(index*5)]
            args_map[f"cn-{cn_mod}"]["files"] = args[6+(index*5)]
            if(args_map[f"cn-{cn_mod}"]["files"] is None):
                raise ValueError(f"Frames missing")
            if frame_count is None:
                frame_count = len(args_map[f"cn-{cn_mod}"]["files"])
            else:
                if len(args_map[f"cn-{cn_mod}"]["files"]) != frame_count:
                    raise ValueError(f"Frames missmatch, make sure that you put the same number of frames on each module")
            index += 1  
        for frame_i in range(frame_count):
            cn_layers = [] 
            frame = Image.open(args_map[f"cn-{cn_mod}"]["files"][frame_i].name)
            nimg = np.array(frame.convert("RGB"))
            bimg = np.zeros((frame.width, frame.height, 3), dtype = np.uint8)
            for cn_mod in range(1, args_map["cn_modules"]+1):
                cn_unit = controlnet_module.ControlNetUnit(
                    enabled = True,
                    model = args_map[f"cn-{cn_mod}"]["model"],
                    module = "none",
                    image = [nimg, bimg],
                    weight = args_map[f"cn-{cn_mod}"]["weight"],
                    guidance_start =args_map[f"cn-{cn_mod}"]["guidance_start"],
                    guidance_end =args_map[f"cn-{cn_mod}"]["guidance_end"],
                    guess_mode = False
                )
                cn_layers.append(cn_unit)
            controlnet_module.update_cn_script_in_processing(p, cn_layers)
            if initial_seed:
                p.seed = initial_seed
            proc = process_images(p)            
            if initial_seed is None:
                initial_seed = proc.seed
                initial_info = proc.info
            frames.append(proc.images[0])      
            gif = save_gif(p, frames)  
        processed = Processed(p, [gif], initial_seed, initial_info)
        return processed
