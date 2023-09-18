
import obspython as obs
import threading, queue, time

def call_stable_diffusion(queue, stop_signal):
    while not stop_signal.is_set():
        queue.put("test")
        time.sleep(10)
    print('thread stopping')
    
def check_queue():
    if not queue.empty():
        item = queue.get()
        print(f"Got item from the queue: {item}")
        switch_scenes()
    else:
        # print("The queue is empty.")
        pass

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
    # obs.obs_properties_add_button(properties, 'switch button', "Switch", switch_button)
    # obs.obs_properties_add_button(properties, 'enable button', "Enable", enable_button)
    obs.obs_properties_add_button(properties, 'toggle thread button', "Toggle Thread", toggle_thread_button)
    # current_scene = obs.obs_frontend_get_current_scene()
    # obs.obs_properties_add_text(properties, 'scene', obs.obs_source_get_name(current_scene), obs.OBS_TEXT_DEFAULT)
    return properties

# def script_update(settings):
#     """
#     Called when the script’s settings (if any) have been changed by the user.
#     """

#     obs.timer_remove(cycle)
#     blink_rate = obs.obs_data_get_int(settings, "cycle_rate")
#     obs.timer_add(cycle, 10000)  # Change scene every cycle_rate ms
    
# def switch_button(properties, property):
#     switch_scenes()
    
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

imageSource = obs.obs_get_source_by_name("Image")
settings = obs.obs_source_get_settings(imageSource)
obs.obs_data_set_string(settings, 'file', "00005-2492970752.png")
# data = obs.obs_data_get_json(settings)
obs.obs_source_update(imageSource, settings)
obs.obs_source_release(imageSource)