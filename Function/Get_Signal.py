from pydub import AudioSegment
import numpy as np
def get_speaker_signal(Audio_addr,Speaker_dict):
    adict = Speaker_dict.copy()
    sound = AudioSegment.from_file(Audio_addr)

    samples = np.array(sound.get_array_of_samples())
    a = len(samples)/sound.duration_seconds
    keys = set(adict.values())
    result_dict = {key : [0] * len(samples) for key in keys if key != 0}
    result_dict['origin'] = samples 
    for t,speaker in adict.items():
        if speaker == 0:
            continue
        else:
            ti = [int(tt *a / 1000) for tt in t]
            result_dict[speaker][ti[0]:ti[1]] = samples[ti[0]:ti[1]]
    return result_dict

# def get_silent_signal()