import obspython as obs
import threading, queue, requests, tempfile, base64, io
from PIL import Image

class ControlnetRequest:
    def __init__(self, prompt, neg_prompt):
        self.url = "http://localhost:7860/sdapi/v1/txt2img"
        self.prompt = prompt
        self.neg_prompt = neg_prompt
        self.body = None

    def build_body(self):
        self.body = {
            "prompt": self.prompt,
            "negative_prompt": self.neg_prompt,
            "batch_size": 1,
            "steps": 15,
            "cfg_scale": 7,
            "width": 768,
            "height": 512,
            # "seed": 1992241092
            # "subseed": -1,
            # "subseed_strength": 0,
        }

    def send_request(self):
        response = requests.post(url=self.url, json=self.body)
        return response.json()

def call_stable_diffusion(queue, stop_signal):
    while not stop_signal.is_set():
        try:
            # with tempfile.TemporaryDirectory() as temp_dir:
            control_net = ControlnetRequest(prompt, neg_prompt)
            control_net.build_body()
            output = control_net.send_request()

            result = output['images'][0]
            # print(f'Parameters: {output["parameters"]}')
            # print(f'Info: {output["info"]}')
            
            
            # TODO: Find a better way to translate results to QPixmap without saving file
            # self.current_info = json.loads(output["info"])
            pil_image = Image.open(io.BytesIO(base64.b64decode(result.split(",", 1)[0])))
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            try:
                # Write some data to the temporary file
                # temp_file.write(b"Hello, World!")

                # Close the temporary file explicitly
                # print("Temporary file has been deleted.")
                pil_image.save(temp_file)
                temp_file.close()

                # Now you can use the temporary file for reading, for example:

                # Don't forget to delete the temporary file when you're done with it
                # Note that you can't delete it while it's open
                ############################################################################################################
                # import os
                # os.remove(temp_file.name)

            except Exception as e:
                print("An error occurred:", str(e))

            
            
        except Exception as e:
            print(f"Error: {e}")
            break   
        queue.put(temp_file.name)
    print('thread stopping')
    
def check_queue():
    if not queue.empty():
        item = queue.get()
        print(f"Got item from the queue: {item}")
        set_image(item)
        switch_scenes()
    else:
        # print("The queue is empty.")
        pass
    
def set_image(file_name):
    current_scene = obs.obs_frontend_get_current_scene()
    if obs.obs_source_get_name(current_scene) == "Background Flip":
        source_name = "Image_Flop"
    else:
        source_name = "Image_Flip"
    print('etting image')
    imageSource = obs.obs_get_source_by_name(source_name)
    settings = obs.obs_source_get_settings(imageSource)
    obs.obs_data_set_string(settings, 'file', file_name)
    # data = obs.obs_data_get_json(settings)
    obs.obs_source_update(imageSource, settings)
    obs.obs_source_release(imageSource)

def script_description():
    return """<center><h2>Image Source Swapper</h2></center>
            <p>Changes the image for the source</p>"""
            
def script_load(settings):
    print("Script loaded")
    global queue
    queue = queue.Queue(maxsize=1)
    global stop_signal
    stop_signal = threading.Event()
    stop_signal.set()
    obs.timer_add(check_queue, 1000)
    
    
    
def script_unload():
    print("Script unloaded")
            
def script_properties():
    properties = obs.obs_properties_create()
    # obs.obs_properties_add_button(properties, 'test button', "Test", test_button)
    # obs.obs_properties_add_button(properties, 'enable button', "Enable", enable_button)
    obs.obs_properties_add_button(properties, 'toggle thread button', "Toggle Thread", toggle_thread_button)
    # current_scene = obs.obs_frontend_get_current_scene()
    obs.obs_properties_add_text(properties, 'prompt', 'Prompt', obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(properties, 'neg_prompt', 'Neg Prompt', obs.OBS_TEXT_DEFAULT)
    return properties

def script_update(settings):
    """
    Called when the script’s settings (if any) have been changed by the user.
    """
    
    global prompt
    prompt = obs.obs_data_get_string(settings, 'prompt')
    global neg_prompt
    neg_prompt = obs.obs_data_get_string(settings, 'neg_prompt')

    
# def test_button(properties, property):
#     # prompt = obs.obs_properties_get(properties, 'prompt')
#     print(prompt)
    
def switch_scenes():
    current_scene = obs.obs_frontend_get_current_scene()
    if obs.obs_source_get_name(current_scene) == "Background Flip":
        change_scene("Background Flop")
    else:
        change_scene("Background Flip")

# def enable_button(properties, property):
#     obs.timer_add(switch_scenes, 10000)

def toggle_thread_button(properties, property):
    if not stop_signal.is_set():
        stop_signal.set()
    else:
        print("start the thread")
        stop_signal.clear()
        # TODO: Find way to close this gracefully
        stable_diffusion_thread = threading.Thread(target=call_stable_diffusion, args=(queue, stop_signal))
        stable_diffusion_thread.start()
    
def change_scene(scene_name):
    for scene in obs.obs_frontend_get_scenes():
        if obs.obs_source_get_name(scene) == scene_name:
            # current_scene = obs.obs_frontend_get_current_scene()
            # scenes.remove(current_scene)
            obs.obs_frontend_set_current_scene(scene)

