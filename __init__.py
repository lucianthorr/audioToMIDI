import urllib
import logging
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.Task import FuncTask

LOG = logging.getLogger("audioToMidi")
PATH = "/Users/jasonaylward/Music/iTunes/iTunes Music/"  # The path that you want to iterate through
APP = Live.Application.get_application()
BROWSER = APP.browser
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
        for i, conversion in enumerate(conversions):
            track = clip.canonical_parent.canonical_parent
            song = track.canonical_parent
            Live.Conversions.audio_to_midi_clip(song, clip, conversion)

class AudioToMIDI(ControlSurface):
    def __init__(self, c_instance=None, publish_self=True, *args, **kwargs):
        super(AudioToMIDI, self).__init__(c_instance, publish_self, *args, **kwargs)
        self.c_instance = c_instance
        t = FuncTask(func=self.run)
        self._task_group.add(t)


    def run(self, thing):
        song = APP.get_document()
        song.create_audio_track(-1)
        track = song.tracks[-1]
        clips = load_clips(song, track, 3)
        convert_clips(song, clips, CONVERSIONS)


def create_instance(c_instance):
    return AudioToMIDI(c_instance=c_instance)
