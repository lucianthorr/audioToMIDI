import urllib
import logging
import Live
from ableton.v2.control_surface import ControlSurface

LOG = logging.getLogger("audioToMidi")
PATH = "/Users/jasonaylward/Music/iTunes/iTunes Music/"  # The path that you want to iterate through
BROWSER = Live.Application.get_application().browser
CONVERSIONS = [Live.Conversions.AudioToMidiType.harmony_to_midi,
               Live.Conversions.AudioToMidiType.melody_to_midi,
               Live.Conversions.AudioToMidiType.drums_to_midi]

def get_items_from_path(path):
    path_uri = "userfolder:" + urllib.quote(PATH)
    for item in BROWSER.user_folders:
        if item.uri == path_uri:
            return get_items(item)
    LOG.info("no items found")
    return []

def get_items(base):
    items = []
    for child in base.iter_children:
        if child.is_folder:
            items += get_items(child)
        if child.is_loadable:
            items.append(child)
    return items

def load_clips(song, track, num_clips=10):
    scenes = [scene for scene in song.scenes]
    song.view.selected_track = track
    items = get_items_from_path(PATH)
    clips = []
    for i, item in enumerate(items):
        if i >= num_clips or i >= len(items):
            break
        if i >= len(scenes):
            scenes.append(song.create_scene(-1))
        song.view.selected_scene = scenes[i]
        slots = track.clip_slots
        BROWSER.load_item(item)
        clip = slots[i].clip
        clip.warping = False
        clips.append(clip)
    return clips

def convert_clips(song, clips, conversions=CONVERSIONS):
    for clip in clips:
        for conversion in conversions:
            Live.Conversions.audio_to_midi_clip(song, clip, conversion)

class AudioToMIDI(ControlSurface):
    def __init__(self, *args, **kwargs):
        super(AudioToMIDI, self).__init__(*args, **kwargs)
        self.c_instance = kwargs.get("c_instance", None)
        self.run()

    def run(self):
        song = self.c_instance.song()
        song.create_audio_track(-1)
        track = song.tracks[-1]
        clips = load_clips(song, track)
        convert_clips(song, clips)


def create_instance(c_instance):
    return AudioToMIDI(c_instance=c_instance)

# def create_instance(c_instance):
#     pass
