## Ableton "Control Surface" Script to automate audio-to-midi conversions in bulk.

#### HOWTO:
1. In Ableton Live, add the folder of music you would like to convert to the "Places" Section in the leftmost sidebar.
2. In your terminal, cd to the MIDI Remote Scripts folder of your Ableton Application and clone the repo.
  ```
  cd "/Applications/Ableton Live 10 Suite.app/Contents/App-Resources/MIDI Remote Scripts/"
  git clone git@github.com:lucianthorr/audioToMIDI.git
  cd audioToMIDI
  ```
3. Edit the PLACE_NAME, SOURCE_FOLDER, DEST_FOLDER, MAX_CONVERSIONS, CONVERSIONS constants.
    *   PLACE_NAME is the name of the folder in the Places section of Ableton Live
    *   SOURCE_FOLDER is the full path to the folder you would like to iterate over to make conversions
    *   DEST_FOLDER is the folder in which you would like the midi files to be saved
    *   CONVERSIONS is the list of conversions you would like for each file.  Options are "melody", "harmony" and "drums"
    *   MAX_CONVERSIONS is the number of midi files you would like, remember it would be # of files * # of conversions
4. Setup Ableton Live
    *   In Ableton Live, go to Preferences>Link/MIDI
    *   Select the audioToMIDI Control Surface
5. Conversions should start immediately.


#### TODO:
 * Ableton does seem to crash after a while.  Usually after 5-6 hours of converting files.  Figure out why and fix it.


 #### Resources:
  * https://julienbayle.studio/ableton-live-midi-remote-scripts/
  * https://github.com/styk-tv/4bars
  * http://koaning.io.s3-website.eu-west-2.amazonaws.com/python-able-ton.html
