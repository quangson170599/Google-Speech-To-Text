import os
from re import A
os.makedirs('Txt_dir',exist_ok=True)

def write_dict_txt(adict,adict_name,audio,Txt_option= 'Basic'):
    auname = audio
    if '/' in audio:
        auname = audio.split('/')[-1]
    if '\\' in audio:
        auname = audio.split('\\')[-1]
    if '.wav' in auname:
        auname = auname.replace('.wav','')
    name = 'Txt_dir/{}_Option_{}'.format(auname,Txt_option)
    os.makedirs(name,exist_ok=True)
    name = '{}/{}.txt'.format(name,adict_name)
    with open(name,'w+',encoding='utf-8') as f:
        f.write(str(adict))

def read_dict_txt(audio,Txt_option = 'Basic'):
    auname = audio
    if '/' in audio:
        auname = audio.split('/')[-1]
    if '\\' in audio:
        auname = audio.split('\\')[-1]
    if '.wav' in auname:
        auname = auname.replace('.wav','')
    name = 'Txt_dir/{}_Option_{}'.format(auname,Txt_option)
    if not os.path.exists(name):
        return False
    n_dict = os.listdir(name)
    R_dict = dict()

    for i in n_dict:
        n_name = os.path.join(name,i)
        with open(n_name,'r',encoding='utf-8') as f:
            adict = eval(f.read())
        R_dict[i.replace('.txt','')] = adict
    print('find file : ',R_dict.keys())
    return R_dict

if __name__=='__main__':
    def transcribe_file(speech_file):
        """Transcribe the given audio file asynchronously."""
        from google.cloud import speech
            
        client = speech.SpeechClient()

        # [START speech_python_migration_async_request]
        with open(speech_file, "rb") as audio_file:
            content = audio_file.read()

        """
        Note that transcription is limited to a 60 seconds audio file.
        Use a GCS file for audio longer than 1 minute.
        """
        audio = speech.RecognitionAudio(content=content)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )

        # [START speech_python_migration_async_response]

        operation = client.long_running_recognize(config=config, audio=audio)
        # [END speech_python_migration_async_request]

        print("Waiting for operation to complete...")
        response = operation.result(timeout=90)

        # Each result is for a consecutive portion of the audio. Iterate through
        # them to get the transcripts for the entire audio file.
        for result in response.results:
            # The first alternative is the most likely one for this portion.
            print(u"Transcript: {}".format(result.alternatives[0].transcript))
            print("Confidence: {}".format(result.alternatives[0].confidence))
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'Speech_to_text_2.json'
    transcribe_file(r'Splited_Silence\04-08-2022 12 05 39\0\file_1.wav')
