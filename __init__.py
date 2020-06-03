import urllib
import logging
import Live
import time
from _Framework.ControlSurface import ControlSurface
from _Framework.Task import FuncTask, TaskGroup

LOG = logging.getLogger("audioToMidi")
PATH = "/Users/jasonaylward/Music/iTunes/iTunes Music/"  # The path that you want to iterate through
APP = Live.Application.get_application()
BROWSER = APP.browser

class AudioToMIDI(ControlSurface):
    def __init__(self, c_instance=None, publish_self=True, *args, **kwargs):
        super(AudioToMIDI, self).__init__(c_instance, publish_self, *args, **kwargs)
        self.c_instance = c_instance
        self.song = APP.get_document()
        self.song.create_audio_track(-1)
        self.audio_track = self.song.tracks[-1]
        self.audio_track_idx = len(self.song.tracks) - 1
        self.items = get_items_from_path(PATH, max_files=11)
        self.item_idx = 0
        t = FuncTask(func=self.load_clip)
        self._task_group.add(t)

    def next_item(self):
        if self.item_idx < len(self.items):
            item = self.items[self.item_idx]
            self.item_idx += 1
            return item

    def load_clip(self, _):
        LOG.info("loading clip")
        self.song.view.selected_track = self.audio_track
        self.song.view.selected_scene = self.song.scenes[0]
        BROWSER.load_item(self.next_item())
        t = FuncTask(func=self.convert)
        self._task_group.clear()
        self._task_group.add(t)

    def convert(self, _):
        LOG.info("converting clip")
        self.song.add_tracks_listener(self.new_track_created)
        slots = self.audio_track.clip_slots
        clip = slots[0].clip
        clip.warping = False
        Live.Conversions.audio_to_midi_clip(self.song, clip, Live.Conversions.AudioToMidiType.drums_to_midi)

    def new_track_created(self):
        LOG.info("created!")
        new_track = self.song.view.selected_track
        if get_track_index(self.song, new_track) > self.audio_track_idx:
            selected_scene = self.song.view.selected_scene
            clip = get_clip(self.song, new_track, selected_scene)
            t = FuncTask(func=self.save_conversion)
            self._task_group.clear()
            self._task_group.add(t)

    def save_conversion(self, clip):
        orig_clip = get_clip(self.song, self.audio_track, self.song.view.selected_scene)
        LOG.info("pretend to save %s", orig_clip.file_path)
        t = FuncTask(func=self.delete_track)
        self._task_group.clear()
        self._task_group.add(t)


    def delete_track(self, _):
        self._task_group.clear()
        self.song.delete_track(len(self.song.tracks)-1)

def get_items_from_path(path, max_files=10):
    path_uri = "userfolder:" + urllib.quote(PATH)
    for item in BROWSER.user_folders:
        if item.uri == path_uri:
            return get_items(item, max_files)
    LOG.info("no items found")
    return []

def get_items(base, max_files=10):
    items = []
    for child in base.iter_children:
        if child.is_folder:
            items += get_items(child)
        if child.is_loadable:
            items.append(child)
        if len(items) >= max_files:
            break
    return items[:max_files]

def get_clip(song, track, scene):
    for i, s in enumerate(song.scenes):
        if s == scene:
            return track.clip_slots[i].clip
    return None

def get_track_index(song, track):
    for i, t in enumerate(song.tracks):
        if t == track:
            return i
    return -1


def create_instance(c_instance):
    return AudioToMIDI(c_instance=c_instance)