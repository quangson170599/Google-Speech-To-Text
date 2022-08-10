import os


def write_Speaker_txt(odict,audio_addr,txt=None):
    if txt == None:
        os.makedirs('Txt_dir/Speaker',exist_ok=True)
        if '/' in audio_addr:
            name = audio_addr.split('/')[-1]
        elif '\\' in audio_addr:
            name = audio_addr.split('\\')[-1]
        else:
            name = audio_addr.split(os.sep)[-1]
        txt = 'Txt_dir/Speaker/' + name.replace('.wav','.txt')
    with open(txt,'w+') as f:
        f.write(str(odict))
def read_Speaker_txt(audio_addr,txt=None):
    if txt == None:
        os.makedirs('Txt_dir/Speaker',exist_ok=True)
        if '/' in audio_addr:
            name = audio_addr.split('/')[-1]
        elif '\\' in audio_addr:
            name = audio_addr.split('\\')[-1]
        else:
            name = audio_addr.split(os.sep)[-1]
        txt = 'Txt_dir/Speaker/' + name.replace('.wav','.txt')
    if not os.path.exists(txt):
        return False
    with open(txt,'r+') as f:
        a = f.read()
        return eval(a)