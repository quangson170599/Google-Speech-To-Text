from Process_Function import *
from time import time


def main(Audio_Input):
    Punc = False    # Có dấu theo gg hay k
    Downline =True  # Có xuống dòng k

    Audio_Input = Check_Audio_name(Audio_Input)


    process_time = [time()]
    '''Speaker'''
    _,hashDict = Split_speaker(Audio_Input, time_ok=True)
    process_time.append(time())

    '''Silent'''
    My_info = []
    My_info_list = []
    for audio,speaker in hashDict.items():
        my_dict,alist = split_silence(audio,speaker,silence_time=700,set_channel=True)
        My_info.append(my_dict)
        My_info_list.append(alist)
    # My_info = []
    # for key,value in hashDict.items():
    #     My_info.append({value:{key:(0,0)}})
    # process_time.append(time())

    '''Google'''
    if Punc == False and Downline == True:
        My_info = Process(My_info,My_info_list,time=20)
    Text_Dict=GCP_s2t(My_info,Punc=Punc)
    Result = Handle_Text_Dict(Text_Dict,XD=Downline)
    process_time.append(time())

    '''Syntax'''
    if Punc == False:
        final_text = process_input_no_punc(Result)
    else:
        final_text = process_input_punc(Result)
        

    process_time.append(time())
    '''Write Doc'''
    # Name = Audio_Input.split('/')[-1]
    # Name.replace('.wav','Xuong_dong')
    # downline(final_text)
    Create_Word(Audio_Input,final_text)

    process_time = [process_time[i+1]-process_time[i] for i in range(len(process_time[:-1]))]
    print(process_time,'\n')


if __name__== 'main':
    Audio_Input = 'Input/23-06-2022 14 12 36.wav'
    main(Audio_Input)
