""" Iterates through a library of music (SOURCE_FOLDER) and converts tracks to midi and saves the files to DEST_FOLDER """
import os
import urllib
import logging
import time
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.Task import FuncTask, TaskGroup
import to_midi

PLACE_NAME = "iTunes Music"
SOURCE_FOLDER = "/Users/jasonaylward/Music/iTunes/iTunes Music/Genesis/"  # The path that you want to iterate through
DEST_FOLDER = "/Users/jasonaylward/Desktop/midis/Genesis/"
MAX_CONVERSIONS = 200
CONVERSIONS = ["melody", "harmony", "drums"]


LOG = logging.getLogger("audioToMidi")  # Logged to ~/Library/Preferences/Ableton/Live <version>/Log.txt
CONVERSION_DICT = {"melody": Live.Conversions.AudioToMidiType.melody_to_midi,
               "harmony": Live.Conversions.AudioToMidiType.harmony_to_midi,
               "drums": Live.Conversions.AudioToMidiType.drums_to_midi}


class AudioToMIDI(ControlSurface):
    def __init__(self, c_instance=None, publish_self=True, *args, **kwargs):
        super(AudioToMIDI, self).__init__(c_instance, publish_self, *args, **kwargs)
        self.c_instance = c_instance
        self.app = Live.Application.get_application()
        self.browser = self.app.browser
        self.song = self.app.get_document()
        self.song.create_audio_track(-1)
        self.song.tempo = 120.0
        self.audio_track = self.song.tracks[-1]
        self.audio_track_idx = len(self.song.tracks) - 1
        self.items = self.get_items_from_path(SOURCE_FOLDER)
        self.conversions = CONVERSIONS
        self.gen = self.next(max_conversions=MAX_CONVERSIONS)
        self.song.add_tracks_listener(self.new_track_created)
        task = FuncTask(func=self.load_clip)
        self._task_group.add(task)

    def next(self, max_conversions=0):
        cnt = 0
        for item in self.items:
            for conversion in self.conversions:
                path = item.uri.replace("userfolder:", "")
                path = urllib.unquote(path).replace("#", "").replace(":", "/")
                dest = self.get_destination(path, conversion)
                LOG.info("dest = %s", dest)
                if not os.path.exists(dest+".mid"):
                    cnt += 1
                    yield item, conversion
            if cnt >= max_conversions:
                break
        yield None

    def load_clip(self, _):
        LOG.info("loading clip")
        self.song.view.selected_track = self.audio_track
        self.song.view.selected_scene = self.song.scenes[0]
        resp = next(self.gen)
        if resp != None:
            item, conversion = resp
            self.browser.load_item(item)
            self.conversion = conversion
            task = FuncTask(func=self.convert)
            self._task_group.clear()
            self._task_group.add(task)

    def convert(self, _):
        slots = self.audio_track.clip_slots
        clip = slots[0].clip
        clip.warping = False
        Live.Conversions.audio_to_midi_clip(self.song, clip, CONVERSION_DICT[self.conversion])

    def new_track_created(self):
        new_track = self.song.view.selected_track
        if get_track_index(self.song, new_track) > self.audio_track_idx:
            selected_scene = self.song.view.selected_scene
            self.midi_clip = get_clip(self.song, new_track, selected_scene)
            task = FuncTask(func=self.save_conversion)
            self._task_group.clear()
            self._task_group.add(task)

    def save_conversion(self, _):
        orig_clip = get_clip(self.song, self.audio_track, self.song.view.selected_scene)
        orig_path = orig_clip.file_path
        LOG.info("clip = %s", orig_path)
        destination = self.get_destination(orig_path, self.conversion)
        notes = Live.Clip.Clip.get_notes(self.midi_clip, self.midi_clip.start_time, 0,
                                         self.midi_clip.end_time, 96)
        to_midi.save(destination, self.song.tempo, notes)
        task = FuncTask(func=self.delete_track)
        self._task_group.clear()
        self._task_group.add(task)

    def get_destination(self, orig_path, conversion):
        dest = DEST_FOLDER+orig_path[len(SOURCE_FOLDER):]
        dest = dest.replace("..", "")
        path, raw_filename = dest.rsplit("/", 1)
        if not os.path.exists(path):
            os.makedirs(path)
        filename = raw_filename.rsplit(".")[0] if "." in raw_filename else raw_filename
        filename += "." + conversion
        return path+"/"+filename

    def delete_track(self, _):
        self.song.delete_track(len(self.song.tracks)-1)
        task = FuncTask(func=self.load_clip)
        self._task_group.clear()
        self._task_group.add(task)


    def get_items_from_path(self, path):
        for item in self.browser.user_folders:
            if item.name == PLACE_NAME:
                return get_items(item)
        LOG.info("no items found")
        return []

def get_items(base):
    items = []
    path_uri = "userfolder:" + urllib.quote(SOURCE_FOLDER)
    for child in base.iter_children:
        decoded = "userfolder:" + child.uri[11:].replace("#", "").replace(":", "/")
        if child.is_folder:
            items += get_items(child)
        if child.is_loadable and path_uri in decoded:
            items.append(child)
    return items

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

