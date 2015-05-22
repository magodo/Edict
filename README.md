##Git Used

##Dpendency:

1. kivy
2. numpy
3. audiostream



##PROBLEM:

Audio:
    Since using "kivy/audiostream" to do the recording. Don't know why could not create a thread and do the record in parallel. 
    So changed to record for a fix duration: 1 seconds.

edict.ini(Removed):
    Should be removed before compile. (Should overcome this issue!)

Match process:
    Importve

Word Imagin:
    Improve

DTW:
    Algorithm modify

If personal_dict.pkl doesn't exist, android will crash: because open("", "wb") didn't create file in android, maybe permission issue.

##Build:
./distribute.sh -m "numpy kivy"
./build.py --dir <dir> --name Edict --package org.edict --version 1.0 --orientation portrait --permission RECORD_AUDIO debug installd




