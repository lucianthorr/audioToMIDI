import urllib
import logging
import Live
import time
from _Framework.ControlSurface import ControlSurface
from _Framework.Task import FuncTask

LOG = logging.getLogger("audioToMidi")
PATH = "/Users/jasonaylward/Music/iTunes/iTunes Music/"  # The path that you want to iterate through
DESTINATION = "/Users/jasonaylward/Desktop/audioToMIDI"
APP = Live.Application.get_application()
BROWSER = APP.browser
CONVERSIONS = {"harmony": Live.Conversions.AudioToMidiType.harmony_to_midi,
               "melody": Live.Conversions.AudioToMidiType.melody_to_midi,
               "drums": Live.Conversions.AudioToMidiType.drums_to_midi}
CURRENT_CONVERSION = ""
CURRENT_CLIP_PATH = ""
WAITING = False
MAX_WAIT = 15

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

def get_track_index(song, track):
    for i, t in enumerate(song.tracks):
        if t == track:
            return i
    return -1

def get_track(song, index):
    if index >= 0:
        return song.tracks[index]
    return None

def new_track_created():
    LOG.info("enter callback")
    song = APP.get_document()
    view = song.view
    track = view.selected_track
    idx = get_track_index(song, track)
    for clip_slot in track.clip_slots:
        if clip_slot.has_clip:
            clip = clip_slot.clip
            start = clip.start_time
            end = clip.end_time
            LOG.info("creating notes")
            notes = Live.Clip.Clip.get_notes(clip, start, 0, end ,96)
            path = DESTINATION+"/"+CURRENT_CLIP_PATH[len(PATH):]+"_"+CURRENT_CONVERSION+".notes"
            LOG.info("path")
            # save_notes(clip.file_path, notes)  #filepath only good for audio clips
    WAITING = False

def save_notes(path, notes):
    pass

def convert_clips(song, clips, conversions=CONVERSIONS.values()):
    song.view.add_selected_track_listener(new_track_created)
    for clip in clips:
        for i, conversion in enumerate(conversions):
            track = clip.canonical_parent.canonical_parent
            song = track.canonical_parent
            Live.Conversions.audio_to_midi_clip(song, clip, conversion)
            WAITING = True
            CURRENT_CONVERSION = conversion
            CURRENT_CLIP_PATH = clip.file_path
            total_wait = 0
            while WAITING:
                LOG.info("waiting...")
                total_wait += 0.1
                time.sleep(0.1)
                if total_wait >= MAX_WAIT:
                    break
            new_track = song.tracks[-1]
            track_index = get_track_index(song, new_track)
            song.delete_track(track_index)


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
        clips = load_clips(song, track, 1)
        convert_clips(song, clips, [CONVERSIONS["drums"]])


def create_instance(c_instance):
    return AudioToMIDI(c_instance=c_instance)

# def create_instance(c):
#     print("hi")