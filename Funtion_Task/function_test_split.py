import os
import pydub
from pydub import AudioSegment, silence


def export_audio(audio, count):
    audios = audio.set_frame_rate(16000)
    audios.export(os.path.join('./ConvertAudio/file_{}.wav'.format(str(count))), format='wav')

# hashDict: {speaker: (start, stop)}
def split_silence(audio, speaker):
    os.makedirs('ConvertAudio', exist_ok=True)
    myaudio = AudioSegment.from_file(audio, "wav")
    dbfs = myaudio.dBFS
    duration_in_sec = len(myaudio) / 1000
    mydict = {}
    t_dict = {}

    # Lấy các khoảng silence trong audio
    silences = silence.detect_silence(myaudio,
                                      min_silence_len= 300,
                                      silence_thresh=dbfs-10)
    silences = [((start/1000),(stop/1000)) for start,stop in silences]

    print(silences)

    if len(silences) > 0:
        n_silence = []
        if silences[0][0] == 0.0:
            n_silence.append(silences[0])
            silences.pop(0)

        # Chỉnh lại, làm tròn sec
        for i in silences:
            if round(i[0]) < i[0]:
                temp= (i[0]+0.5, i[1])
            else:
                temp= (round(i[0]), i[1])
            n_silence.append(temp)
        print(n_silence)

        count = 1
        for i in silences:
            temp= './ConvertAudio/file_'+str(count)+'.wav' # vị trí file: lưu file ở thư mục nào thì địa chỉ tới thư mục đó
            t_dict[temp]= i
            count +=1

        # export_file_audio
        start = 0.0
        end = duration_in_sec
        s_audio = myaudio[start*1000:n_silence[0][0]*1000]
        export_audio(s_audio, 1)
        count = 2
        for i in range(len(n_silence)-1):
            s= n_silence[i][1]
            e= n_silence[i+1][0]
            n_audio = myaudio[s*1000:e*1000]
            export_audio(n_audio, count)
            count += 1
        if n_silence[len(n_silence)-1][1] != end:
            e_audio = myaudio[n_silence[len(n_silence)-1][1]*1000:end*1000]
            export_audio(e_audio, count)
            temp= './ConvertAudio/file_'+str(count)+'.wav'
            t_dict[temp] = []

    # final
    mydict[speaker] = t_dict

    # return: {speaker: {file_split_1: (start, stop)}, {file_split_2: (start, stop)}, ...}
    return mydict

speaker = "SPEAKER_1"
audio = "Splited_speaker/23-06-2022 14 12 36/2.wav"
mydict = split_silence(audio, speaker)
print(mydict)

