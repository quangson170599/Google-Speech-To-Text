import sys
## Library
import os
from pydub import AudioSegment, silence
import wave
from pyannote.audio import Pipeline
from google.cloud import speech
from google.cloud import storage
from underthesea import pos_tag as pot
import re


print(sys.executable)

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'Speech2Text.json'

## Tạo thư mục cho từng tác vụ
Thu_muc_cho_audio_cat_theo_giong_noi = 'Splited_speaker'
Thu_muc_cho_audio_cat_theo_silence   = 'Splited_Silence'

os.makedirs(Thu_muc_cho_audio_cat_theo_giong_noi ,exist_ok= True)
os.makedirs(Thu_muc_cho_audio_cat_theo_silence   ,exist_ok= True)


# Split Speaker
def Split_speaker(audio_file):
    Audio = AudioSegment.from_file(audio_file)
    name = Thu_muc_cho_audio_cat_theo_giong_noi + '/' + audio_file.split('/')[-1].replace('.wav', '')

    os.makedirs(name, exist_ok=True)
    hashDict = {}
    diarization = pipeline(audio_file)

    i, start, end, lab = 0, 0, 0, 0
    for segment, track, label in diarization.itertracks(yield_label=True):
        if label != lab:
            Audio_speaker_i = Audio[start * 1000: end * 1000]
            Audio_speaker_i.export(name + '/' + str(i) + '.wav', format='wav')
            hashDict[name + '/' + str(i) + '.wav'] = lab
            i += 1
            start = segment.start
            end = segment.end
            lab = label
        elif label == lab:
            end = segment.end
    # chạy vòng cuối
    Audio_speaker_i = Audio[start * 1000: end * 1000]
    Audio_speaker_i.export(name + '/' + str(i) + '.wav', format='wav')
    hashDict[name + '/' + str(i) + '.wav'] = lab

    os.remove(name + '/' + str(0) + '.wav')
    hashDict.pop(name + '/' + str(0) + '.wav')
    return hashDict


# Split Silence
def export_audio(audio, count, name):
    audios = audio.set_frame_rate(16000)
    audios.export(os.path.join(name + '/file_{}.wav'.format(str(count))), format='wav')


# hashDict: {speaker: (start, stop)}
def split_silence(audio, speaker):
    folder = Thu_muc_cho_audio_cat_theo_silence
    os.makedirs(folder, exist_ok=True)
    name = audio.split('/')
    name = name[-2] + "/" + name[-1].replace('.wav', '')
    name = os.path.join(folder, name)
    os.makedirs(name, exist_ok=True)

    myaudio = AudioSegment.from_file(audio, "wav")
    dbfs = myaudio.dBFS
    duration_in_sec = len(myaudio) / 1000

    mydict = {}
    t_dict = {}

    # Lấy các khoảng silence trong audio
    silences = silence.detect_silence(myaudio,
                                      min_silence_len=300,
                                      silence_thresh=dbfs - 10)
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
        # print(n_silence)

        count = 1
        for start, end in silences:
            temp = name + '/file_' + str(
                count) + '.wav'  # vị trí file: lưu file ở thư mục nào thì địa chỉ tới thư mục đó
            t_dict[temp] = end - start
            count += 1

        # export_file_audio
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
    # final
    mydict[speaker] = t_dict
    return mydict
    # return: {speaker: {file_split_1: (silence_time)}, {file_split_2: (silence_time)}, ...}


# tổng hợp bucket hiện có
def list_buckets():
    """Lists all buckets."""

    storage_client = storage.Client()
    buckets = storage_client.list_buckets()

    for bucket in buckets:
        print(bucket.name)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

# Một số Function hỗ trợ xử lý văn bản đầu ra
def is_digit(word):
    try:
        int(word)
        return True
    except ValueError:
        pass
    return False


def ConvertDate(text):
    month=' tháng '
    year=' năm '
    for index in range(0,len(text)):
        try:
            if (text.index(month,index)==index):
                dateNum = text[index -1]
                monthNum = text[index + len(month)]
                if is_digit(dateNum) and is_digit(monthNum):
                    text=text[:index] + text[index+len(month)-1:]
                    temp = list(text)
                    temp[index]='/'
                    text = "".join(temp)
        except Exception as e:
            if str(e) in 'substring not found':
                pass
            else:
                raise e
        try:
            if (text.index(year,index)==index):
                monthNum = text[index -1]
                yearNum = text[index + len(year)]
                if is_digit(monthNum) and is_digit(yearNum):
                    text=text[:index] + text[index+len(year)-1:]
                    temp = list(text)
                    temp[index]='/'
                    text = "".join(temp)
        except Exception as e:
            if str(e) in 'substring not found':
                pass
            else:
                raise e
    return text


# Các Function xử dụng GCP API thực hiện speech to text
def frame_rate_channel(audio_file_name):
    print(audio_file_name)
    with wave.open(audio_file_name, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate, channels


## Config_GGC_model_before_Transcribe
def Config_GGC(sample_rate_hertz=44100,
               audio_channel_count=1,
               model=None,
               enable_automatic_punctuation=True):
    if model != None:
        config_wav_enhanced = speech.RecognitionConfig(
            sample_rate_hertz=sample_rate_hertz,
            enable_automatic_punctuation=enable_automatic_punctuation,
            language_code='vi-VN',
            audio_channel_count=audio_channel_count,
            model=model,
        )
    else:
        config_wav_enhanced = speech.RecognitionConfig(
            sample_rate_hertz=sample_rate_hertz,
            enable_automatic_punctuation=True,
            language_code='vi-VN',
            audio_channel_count=audio_channel_count
        )
    return config_wav_enhanced


## Config_GGC that doesn't have punctuation
def Config_noPunc(sample_rate_hertz=44100,
                  audio_channel_count=1,
                  model=None,
                  enable_automatic_punctuation=True):
    if model != None:
        config_wav_enhanced = speech.RecognitionConfig(
            sample_rate_hertz=sample_rate_hertz,
            language_code='vi-VN',
            audio_channel_count=audio_channel_count,
            model=model,
        )
    else:
        config_wav_enhanced = speech.RecognitionConfig(
            sample_rate_hertz=sample_rate_hertz,
            language_code='vi-VN',
            audio_channel_count=audio_channel_count
        )
    return config_wav_enhanced


### This function is main on stranscribe
def Transcribe_Long_Audio(Audio_wav, config_wav_enhanced,
                          bucket_name='speech_to_text_stech',
                          Name='Audio_wav'):
    client = speech.SpeechClient()
    Audio_name = Audio_wav.split('/')[-1].split('.')[0]

    upload_blob(bucket_name, Audio_wav, Name)

    media_uri = "gs://{}/{}".format(bucket_name, Name)
    long_audi_wav = speech.RecognitionAudio(uri=media_uri)

    operations = client.long_running_recognize(
        config=config_wav_enhanced,
        audio=long_audi_wav
    )

    response = operations.result(timeout=90)

    text = []

    for i, result in enumerate(response.results):
        alternative = result.alternatives[0]
        alter = ConvertDate(alternative.transcript)
        #             print("-" * 20)
        #             print("First alternative of result {}".format(i))
        #             print("Transcript: {}".format(alternative.transcript))
        text.append(alter)
    return text


##Take audio to text+punc
def AudioToText(path):
    # Audio_wav="../Example/12_no_music.wav"
    #Audio_wav=LoadAudio()
    rate,channel=frame_rate_channel(path)
    config = Config_GGC(sample_rate_hertz = rate,
                 audio_channel_count = channel)
    text = Transcribe_Long_Audio(path,config)
    return text

##Take audio to text, but no punc
def AudioToNoPuncText(path):
    rate,channel=frame_rate_channel(path)
    #lái máy bay già?
    print('chanel: ',channel)
    config_nopunc = Config_noPunc(sample_rate_hertz = rate,
                audio_channel_count = channel)
    text_nopunc = Transcribe_Long_Audio(path,config_nopunc)
    return text_nopunc


# Sử dụng Google API để dịch từng Audio sang text
def GCP_s2t(alist):
    result_dict = {'Speaker': [], 'co dau': [], 'khong dau': [], 'silence': []}
    for adict in alist:
        for speaker, value in adict.items():
            for file_addr, silent_time in adict[speaker].items():
                text = AudioToText(file_addr)
                text_noPunc = AudioToNoPuncText(file_addr)

                result_dict['Speaker'].append(speaker)
                result_dict['co dau'].append(text)
                result_dict['khong dau'].append(text_noPunc)
                result_dict['silence'].append(silent_time)
    return result_dict


# Function Kết hợp Text có dấu theo Google API và silence

def Handle_Text_Dict(adict, S_Punc_ok=False):
    adict = list(adict.values())
    Spr, SL = 0, 0
    ReDict = {'Speaker': [], 'co dau': [], 'khong dau': []}
    Silent_Punc = []
    for Speaker, Punc, NoPunc, Silent in zip(*adict):
        # Vì Punc,NoPunc là list
        new_Punc = ''
        for i in Punc:
            new_Punc += i
        new_NoPunc = ''
        for i in NoPunc:
            new_NoPunc += i

        if Speaker != Spr:
            # Làm gì đó
            Spr = Speaker
            SL = Silent
            ReDict['Speaker'].append(Speaker)

            ReDict['khong dau'].append(new_NoPunc)
            if S_Punc_ok == True:
                ReDict['co dau'].append(new_NoPunc + '. ')
            else:
                ReDict['co dau'].append(new_Punc)
        else:
            # print(ReDict['khong dau'])
            ReDict['khong dau'][-1] += ' ' + new_NoPunc
            ReDict['co dau'][-1] += ' ' + new_Punc
            # # Xét Silence để thêm dấu
            # if S_Punc_ok == True:
            #     if Silent < Giới_hạn:
            #         Silent_Punc[-1] += ', ' + new_NoPunc
            #     else
            #         Silent_Punc[-1] += '. ' + new_NoPunc
    return ReDict


def add_punc(final, final_with_punc):
    # x = recognize(final)
    x = final
    y = final_with_punc
    new = []
    for i in range(len(x)):
        if ':' in x[i]:
            t = x[i].split(':')[1].strip()
            new.append(x[i].replace(t, y[i]))
        else:
            new.append(y[i])
    return new


def recognize(conser):

    def capital(noun):
        return ' '.join([str(wordx).capitalize() for wordx in noun.split()])

    final = conser
    military_rank = ['đại tướng', 'trung tướng', 'thiếu tướng', 'đại tá','thượng tá', 'trung tá', 'thiếu tá', 'đại úy', 'thượng úy', 'trung úy', 'thiếu úy']
    start_para = [ 'xin trân trọng kính','tôi xin kính','xin kính','tôi xin', 'xin', 'kính','tôi']
    vocative = ['đồng chí', 'đại biểu']
    checkpoint_start = ['phát biểu','đặt câu hỏi','trả lời','cho ý kiến','nêu ý kiến']
    end_para = ['tôi xin báo cáo hết', 'xin phép báo cáo hết' ,'xin báo cáo hết'
               , 'xin phép hết','báo cáo hết','tôi xin hết', 'xin hết']
    thank_full = ['tôi xin cảm ơn','tôi cảm ơn','cảm ơn']
    end_co=[]
    for i in end_para:
        for j in thank_full:
            end = i+' '+j
            end_co.append(end)

    pos = pot(final)
    #nhận diện chỉ tử mời
    for i, (wor, tag) in enumerate(pos):
        if wor == 'mời' and i != len(pos)-1 and i != 0:
            if pos[i+1][0] in vocative and str(pos[i-1][0]).lower() not in start_para:
                original = pos[i-1][0] + ' mời'
                subtitute = pos[i-1][0] + ' xin mời'
                final = final.replace( original, subtitute)
            elif pos[i+1][0] in military_rank and str(pos[i-1][0]).lower() not in start_para:
                original = pos[i-1][0] + ' mời ' + pos[i+1][0]
                subtitute = pos[i-1][0] + ' xin mời đồng chí'
                final = final.replace(original, subtitute)
    words = []
    tags = []
    # Thay thế tất cả start bằng xin_mời
    for start in start_para:
        find = re.compile(start+' mời')
        for m in find.finditer(final.lower()):
            sta_in , end_in = m.start(), m.end()
            final = final[0:sta_in] + 'xin_mời' + final[end_in:]
    #Thay thế các end_co bằng báo cáo hết
    for end in end_co:
        find = re.compile(end)
        for m in find.finditer(final.lower()):
            sta_in, end_in = m.start(), m.end()
            final = final[0:sta_in] + 'báo_cáo_hết' + final[end_in:]
    #Thay thế tất cả end bằng báo_cáo_hết
    for end in end_para:
        find = re.compile(end)
        for m in find.finditer(final.lower()):
            sta_in, end_in = m.start(), m.end()
            final = final[0:sta_in] + 'báo_cáo_hết' + final[end_in:]


    # Lưu từ và phân loại vào list words, tags
    postag = pot(final)
    for text, tag in postag:
        words.append(text)
        tags.append(tag)
    # Xử lý văn bản
    for i, word in enumerate(words):
        # Xét trường hợp không phải những từ cuối câu
        if i != len(words)-1 and i != len(words)-2:
            # xét từ đồng chí và không có rank
            if word in vocative and words[i+1].lower() not in military_rank:
                # từ liền trước là xin mời
                if words[i-1] == 'xin_mời':
                    # nếu từ liền sau là N hoặc Np
                    if tags[i+1] in ['N', 'Np', 'V'] or len(words[i+1]) > 5:
                        print( 'MĐ: xin mời k có rank '+ words[i+1] + ' TH1' )
                        ori_sta = 'xin_mời '+word+' '+ words[i+1]
                        sub_sta = '==Đồng chí ' + capital(words[i+1]) + ': '
                        final = final.replace(ori_sta, ori_sta + sub_sta)
                    # nếu từ liền sau tiếp là N hoặc Np
                    elif tags[i+2] in ['N', 'Np', 'V']  or len(words[i+2]) > 5:
                        print( 'MĐ: xin mời k có rank '+ words[i+1] + ' TH2' )
                        ori_sta = 'xin_mời '+word+' '+ str(words[i+1]) + ' ' + words[i+2]
                        sub_sta = '==Đồng chí ' + capital(words[i+1]) + ' ' + words[i+2] +':'
                        final = final.replace(ori_sta, ori_sta + sub_sta)
            # xét từ rank
            if word in vocative and words[i+1].lower() in military_rank:
                if words[i-1] == 'xin_mời':
                    # nếu từ liền sau là N hoặc Np
                    if tags[i+2] in ['N','Np','V'] or len(words[i+2]) > 5:
                        print( 'MĐ: xin mời '+ words[i+1] + ' TH1' )
                        ori_sta = 'xin_mời '+word+' '+ words[i+1] + ' ' + words[i+2]
                        sub_sta = '=='  + str(words[i+1]) + ' ' + capital(words[i+2]) + ': '
                        final = final.replace(ori_sta, ori_sta + sub_sta)
                    # nếu từ liền sau tiếp là N hoặc Np
                    elif tags[i+3] == 'N' or tags[i+3] == 'Np'  or len(words[i+3]) > 5:
                        print( 'MĐ: xin mời '+ words[i+1] + ' TH2' )
                        ori_sta = 'xin_mời '+word+' '+ words[i+1] +' ' + str(words[i+2]) + ' ' + words[i+3]
                        sub_sta = '==' + words[i+1] + ' ' + capital(words[i+2]) + ' ' + capital(words[i+3]) +':'
                        final = final.replace(ori_sta, ori_sta + sub_sta)
            if word in military_rank:
                if words[i-1] == 'xin_mời':
                    if tags[i+1] in ['N','Np','V'] or len(words[i+1]) > 5:
                        print('MĐ không có từ đồng chí TH1')
                        ori_sta = 'xin_mời '+word+' '+ words[i+1]
                        sub_sta = '=='+ word + ' ' + capital(words[i+1])+': '
                        final = final.replace(ori_sta, ori_sta + sub_sta)
                    # nếu từ liền sau tiếp là N hoặc Np
                    elif tags[i+2] == 'N' or tags[i+2] == 'Np'  or len(words[i+2]) > 5:
                        print('MĐ không có từ đồng chí TH1')
                        ori_sta = 'xin_mời '+word+' '+ words[i+1] +' ' + str(words[i+2])
                        sub_sta = '==' + capital(words[i+1]) + ' ' + capital(words[i+2]) + ':'
                        final = final.replace(ori_sta, ori_sta + sub_sta)

    final = final.replace('báo_cáo_hết','==')
    final = final.replace('xin_mời','xin mời')
    for check in checkpoint_start:
        find = re.compile(': '+ check)
        for m in find.finditer(final.lower()):
            sta_in, end_in = m.start(), m.end()
            final = final[0:sta_in] + ': cho_ý_kiến' + final[end_in:]
    final = final.replace(': cho_ý_kiến', ':')

    paragraph =[ para.strip() for para in final.split('==')]
    return paragraph

# input_1 with file json
def process_input(input_1):
    text_no_punc = input_1['khong dau']
    text_punc =input_1['co dau']
    text_done = []
    index_replace =[]
    text_process = '/n '.join(text_no_punc)
    #print(text_process)
    text_reg = recognize(text_process)
    for text in text_reg:
        if '/n ' in text:
            a = text.split('/n ')
            for para in a:
                text_done.append(para)
        if '/n ' not in text:
            text_done.append(text)
    for i in range(len(text_done)):
        if ':' in text_done[i] and text_done[i] != len(text_done)-1:
            x = text_done[i] + ' ' + text_done[i+1]
            index_replace.append(i+1)
            text_done[i] = x
    minus=0
    for i in index_replace:
        i -= minus
        del text_done[i]
        minus += 1
    for i in range(len(text_done)-1):
        if text_done[i] == '':
            del text_done[i]
    print(len(text_done), len(text_punc))
    if len(text_done) == len(text_punc):
        final_text = add_punc(text_done, text_punc)
        a = 'Success'
    else:
        final_text = text_done
        a = 'Fail'
    return a, final_text


# input_2 = {'Speaker':['Speaker_1','Speaker_2','Speaker_1',
#                       'Speaker_3','Speaker_1','Speaker_1'],
#            'co dau': ['gdfgfd xin mời, thiếu tá Hồ Đức thanh.',
#          'ngày 13 tháng 6, Bộ Chỉ huy Bộ đội biên phòng Bà Rịa Vũng Tàu cho biết qua hai ngày 11 và 12 tháng 6 Thực hiện kế hoạch tuần tra bảo vệ chủ quyền vùng biển và phối hợp bảo vệ an ninh an toàn đường ống dẫn khí Nam Côn Sơn lực lượng Biên phòng và công ty đường ống khí Nam Côn Sơn đã phát hiện 12 Vụ việc với 17 phân tử đang Neo Đậu khai thác đánh bắt thủy hải sản và cận kề hành lang an toàn đường ống dẫn khí dưới biển theo đó tổ tuần tra tàu biên phòng 13801 thuộc Hải đội biên phòng 2 bộ đội biên phòng Bà Rịa Vũng Tàu đã tuần tra dọc hành lang an toàn đường ống dẫn khí Nam Côn Sơn từ km 22 đến km 90k b75 và ngược lại báo cáo hết',
#          'xin mời đồng chí Lê, Tuyết Mai.',
#          'quá trình tuần tra tổ công tác phát hiện 12. Vụ việc với 17 Phương tiện đang Neo Đậu khai thác đánh bắt thủy sản trong và cận kề hành lang an toàn đường ống dẫn khí trong đó đã lập biên bản 4 vụ việc với 6 tàu cá của tỉnh Bà Rịa Vũng Tàu 6 vụ với 8 tàu cá tỉnh Bình Thuận và một vụ hai tàu cá của tỉnh Bến Tre tuyên truyền nhắc nhở Một tàu cá đồng thời phát tờ rơi in bản đồ tọa độ các tuyến ống dẫn khí dưới đáy biển tuyên truyền về Nghị định 99 2020 Nghị định Chính phủ quy định xử phạt vi phạm hành chính trong lĩnh vực dầu khí kinh doanh xăng dầu và khí những hoạt động đó giúp ngư dân Nâng cao nhận thức đầy đủ về các quy định của nhà nước và những mối nguy hiểm khi hoạt động trong hành lang an toàn đường ống dẫn khí.',
#          'xin mời đồng chí trung tá Nguyễn Trung Tín.',
#          'ngày 13 tháng 6 của ban nhân dân tỉnh Bình Định, cho biết đã có báo cáo gửi bộ nông nghiệp và phát triển nông thôn về kết quả điều tra xử lý các tàu cá vi phạm vùng biển nước ngoài khai thác hải sản trái phép năm 2022 theo đó từ đầu năm đến nay trên địa bàn tỉnh Bình Định vẫn còn 5 tàu cá và 30 lao động vi phạm vùng biển nước ngoài bị lực lượng chức năng Malaysia bắt giữ 2 tàu cả với người lao động bị kiểm soát tài nguyên rồi thảo trên biển trong đó 6 tàu vi phạm đều ở huyện Phù Cát địa phương liên tục xảy ra tình trạng tàu cá vi phạm hoạt động đánh cá trái phép xin hết'
#                       ],
#            'khong dau' : ['gdfgfd xin mời thiếu tá Hồ Đức thanh',
#          'ngày 13 tháng 6 Bộ Chỉ huy Bộ đội biên phòng Bà Rịa Vũng Tàu cho biết qua hai ngày 11 và 12 tháng 6 Thực hiện kế hoạch tuần tra bảo vệ chủ quyền vùng biển và phối hợp bảo vệ an ninh an toàn đường ống dẫn khí Nam Côn Sơn lực lượng Biên phòng và công ty đường ống khí Nam Côn Sơn đã phát hiện 12 Vụ việc với 17 phân tử đang Neo Đậu khai thác đánh bắt thủy hải sản và cận kề hành lang an toàn đường ống dẫn khí dưới biển theo đó tổ tuần tra tàu biên phòng 13801 thuộc Hải đội biên phòng 2 bộ đội biên phòng Bà Rịa Vũng Tàu đã tuần tra dọc hành lang an toàn đường ống dẫn khí Nam Côn Sơn từ km 22 đến km 90k b75 và ngược lại báo cáo hết',
#          'xin mời đồng chí Lê Tuyết Mai',
#          'quá trình tuần tra tổ công tác phát hiện 12 Vụ việc với 17 Phương tiện đang Neo Đậu khai thác đánh bắt thủy sản trong và cận kề hành lang an toàn đường ống dẫn khí trong đó đã lập biên bản 4 vụ việc với 6 tàu cá của tỉnh Bà Rịa Vũng Tàu 6 vụ với 8 tàu cá tỉnh Bình Thuận và một vụ hai tàu cá của tỉnh Bến Tre tuyên truyền nhắc nhở Một tàu cá đồng thời phát tờ rơi in bản đồ tọa độ các tuyến ống dẫn khí dưới đáy biển tuyên truyền về Nghị định 99 2020 Nghị định Chính phủ quy định xử phạt vi phạm hành chính trong lĩnh vực dầu khí kinh doanh xăng dầu và khí những hoạt động đó giúp ngư dân Nâng cao nhận thức đầy đủ về các quy định của nhà nước và những mối nguy hiểm khi hoạt động trong hành lang an toàn đường ống dẫn khí',
#          'xin mời đồng chí trung tá Nguyễn Trung Tín',
#          'ngày 13 tháng 6 của ban nhân dân tỉnh Bình Định cho biết đã có báo cáo gửi bộ nông nghiệp và phát triển nông thôn về kết quả điều tra xử lý các tàu cá vi phạm vùng biển nước ngoài khai thác hải sản trái phép năm 2022 theo đó từ đầu năm đến nay trên địa bàn tỉnh Bình Định vẫn còn 5 tàu cá và 30 lao động vi phạm vùng biển nước ngoài bị lực lượng chức năng Malaysia bắt giữ 2 tàu cả với người lao động bị kiểm soát tài nguyên rồi thảo trên biển trong đó 6 tàu vi phạm đều ở huyện Phù Cát địa phương liên tục xảy ra tình trạng tàu cá vi phạm hoạt động đánh cá trái phép xin hết',
#                      ]}
#
# input_1={ 'Speaker':['Speaker_1', 'Speaker_2','Speaker_3','Speaker_1'],
#           'co dau': ["tôi mời đồng chí Nguyễn Hữu Lợi cho ý kiến.","tôi là Lợi ,hôm nay tôi xin báo cáo gggsg xin báo cáo hết.",
#                      "tôi mời đồng chí Nguyễn Văn Lợi cho ý kiến.", "tôi báo cáo không có nhiều, xin hết"],
#          'khong dau':["tôi mời đồng chí Nguyễn Hữu Lợi cho ý kiến","tôi là Lợi hôm nay tôi xin báo cáo gggsg xin báo cáo hết",
#                       "tôi mời đồng chí Nguyễn Văn Lợi cho ý kiến", "tôi báo cáo không có nhiều xin hết"]}

# Phần ghép các Function
def merge_code(path):
    Audio_Input = path

    # Đưa các lệnh dưới đây của cell này vô Function là ta có Pipeline

    # splited speaker
    hashDict = Split_speaker(Audio_Input)

    # splited Silence
    My_info = []
    for audio, speaker in hashDict.items():
        my_dict = split_silence(audio, speaker)
        My_info.append(my_dict)

    # Chuyển từng audio thành text có dấu và không dấu
    Text_Dict = GCP_s2t(My_info)

    # Chuyển thành Dict theo yêu cầu của Tín và để cho phần tìm silent
    Result = Handle_Text_Dict(Text_Dict)
    #Result2 = Handle_Text_Dict(Text_Dict, S_Punc_ok=True)

    output,final_text = process_input(Result)
    print(output)
    return final_text
