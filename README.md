## Ableton "Control Surface" Script to automate audio-to-midi conversions in bulk.

#### HOWTO:
1. In your terminal, cd to the MIDI Remote Scripts folder of your Ableton Application and clone the repo.
  ```
  cd "/Applications/Ableton Live 10 Suite.app/Contents/App-Resources/MIDI Remote Scripts/"
  git clone git@github.com:lucianthorr/audioToMIDI.git
  cd audioToMIDI
  ```
2. Edit the PATH constant to the absolute path of the base of the folders of music you would like to converted to MIDI.  I currently have it set to my iTunes library.
3. Edit the `num_clips` keyword variable to the # of mp3 files you would like converted.
4. Setup Ableton Live
  * In Ableton Live, go to Preferences>Link/MIDI
  * Select the audioToMIDI Control Surface
5. Conversions should start immediately.


#### Things to note:
* Once finished, disable audioToMIDI as a Control Surface.  If Live boots with it enabled, it will crash.  If it crashes, comment out the entire `__init__.py` and uncomment out the last two lines.  This allows Live to successfully load audioToMIDI upon booting.

#### TODO:
 * Convert MIDI clips to MIDI files.
 * Save off MIDI clips as files.
 * Remove MIDI tracks after the clips have been saved.
 * Figure out why Live crashes if started with audioToMIDI enabled and fix the issue, if possible.
 
 #### Resources:
  * https://julienbayle.studio/ableton-live-midi-remote-scripts/
  * https://github.com/styk-tv/4bars
  * http://koaning.io.s3-website.eu-west-2.amazonaws.com/python-able-ton.html
