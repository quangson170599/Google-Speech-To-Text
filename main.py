from Process_Function import *
from time import time

# Phần ghép các Function
Audio_Input = 'Input/hoinghi.wav'

# Đưa các lệnh dưới đây của cell này vô Function là ta có Pipeline

now = time()
# splited speaker
hashDict = Split_speaker(Audio_Input)
#'Input/hoinghi.wav' 581.2819s
print('Splited Speaker: ',time()-now)

now = time()
# splited Silence
My_info = []
for audio,speaker in hashDict.items():
    my_dict = split_silence(audio,speaker)
    My_info.append(my_dict)
#'Input/hoinghi.wav' 262.1806s
print('Splited Silence: ',time()-now)

now = time()
# Chuyển từng audio thành text có dấu và không dấu
Text_Dict=GCP_s2t(My_info)
#'Input/hoinghi.wav' 248.8864
print('Audios to text: ',time()-now)


# Chuyển thành Dict theo yêu cầu của Tín và để cho phần tìm silent
Result = Handle_Text_Dict(Text_Dict)
Result2 = Handle_Text_Dict(Text_Dict,S_Punc_ok=True)

now = time()
output,final_text=process_input(Result)
#'Input/hoinghi.wav'  261.9262
print('Handle Syntax: ',time()-now)

now = time()
Create_Word(Audio_Input,final_text)
print('Print Word: ',time()-now)

def write_dict_txt(dict,key)

# Split Silence
# hashDict: {speaker: (start, stop)}
def split_silence(audio, speaker):
    def export_audio(audio, count, name):
        audios = audio.set_frame_rate(16000)
        audios.export(os.path.join(name + '/file_{}.wav'.format(str(count))), format='wav')

    folder = Thu_muc_cho_audio_cat_theo_silence
    os.makedirs(folder, exist_ok=True)
    name = audio.split('/')
    name = name[-2] + "/" + name[-1].replace('.wav', '')
    name = os.path.join(folder, name)
    os.makedirs(name, exist_ok=True)

    myaudio = AudioSegment.from_file(audio, "wav")
    dbfs = myaudio.dBFS
    duration_in_sec = len(myaudio) / 1000

    mydict = dict()
    t_dict = dict()

    Bien = (myaudio.max_dBFS - dbfs)
    threshold = dbfs - Bien / 2

    # Lấy các khoảng silence trong audio
    silences = silence.detect_silence(myaudio,
                                      min_silence_len=300,
                                      silence_thresh=threshold)
    silences = [((start / 1000), (stop / 1000)) for start, stop in silences]
    # print(silences)

    if len(silences) > 0:
        n_silence = []
        if silences[0][0] == 0.0:
            n_silence.append(silences[0])
            silences.pop(0)

        # Chỉnh lại, làm tròn sec
        for i in silences:
            if round(i[0]) < i[0]:
                temp = (i[0] + 0.5, i[1])
            else:
                temp = (round(i[0]), i[1])
            n_silence.append(temp)

        count = 1
        for start, end in silences:
            temp = name + '/file_' + str(
                count) + '.wav'  # vị trí file: lưu file ở thư mục nào thì địa chỉ tới thư mục đó
            t_dict[temp] = end - start
            count += 1

        start = 0.0
        end = duration_in_sec
        s_audio = myaudio[start * 1000:n_silence[0][0] * 1000]
        export_audio(s_audio, 1, name)
        count = 2
        for i in range(len(n_silence) - 1):
            s = n_silence[i][1]
            e = n_silence[i + 1][0]
            n_audio = myaudio[s * 1000:e * 1000]
            export_audio(n_audio, count, name)
            count += 1
        if n_silence[len(n_silence) - 1][1] != end:
            e_audio = myaudio[n_silence[len(n_silence) - 1][1] * 1000:end * 1000]
            export_audio(e_audio, count, name)
            temp = name + '/file_' + str(count) + '.wav'
            t_dict[temp] = 0
    else:
        temp = name + '/file_' + str(0) + '.wav'
        export_audio(myaudio, 0, name)
        t_dict[temp] = 0
    mydict[speaker] = t_dict
    return mydict