import asyncio,json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'tests'))
import httpx
from generation_helpers import new_project,command
from opendirector.application.creation_generation import CreationGeneration
from opendirector.infrastructure.model_configs import ModelConfigs
from opendirector.integrations.voice_library import VoiceLibrary
from opendirector.domain.voice_library import voice_create_fields,voice_id
from opendirector.domain.creation.generation import AudioParameters
from opendirector.domain.projects import ProjectError
from opendirector.wiring import configure_runtime
configure_runtime()
with tempfile.TemporaryDirectory() as folder:
 root=Path(folder)
 configs=ModelConfigs(root)
 model=configs.save('audio','http://127.0.0.1:12345/v1','fishaudio/drama-3','',connection_type='self_hosted',protocol='openai',auth_mode='none')
 project=new_project(root)
 runner=CreationGeneration(project[0],configs)
 request=command(project,model,parameters={'voice':'alice','voiceConnectionId':'00000000-1111-4222-8333-444444444444','voiceProvider':'moss','voiceHasReference':False})
 receipt=runner.prepare(request,session=project[2])
 print('Maintainer P1: mismatched connection/provider/no transcript =>',receipt.status)
 assert receipt.status=='accepted'
 cfg=configs.resolve(model['id'],'audio')
 for name in ['my voice','x'*65]:
  fields=voice_create_fields(cfg,name=name,consent='fixture-consent',ref_text='fixture transcript',speaker_description='')
  assert fields['name']==name
  try: AudioParameters(voice=name)
  except ValueError: selection='rejected'
  else: selection='accepted'
  try: voice_id(name)
  except ProjectError: deletion='rejected'
  else: deletion='accepted'
  print('Maintainer P2:',len(name),'characters; creation accepted, selection',selection,'delete',deletion)
  assert selection==deletion=='rejected'
 nano=configs.save('audio','http://127.0.0.1:12345/v1','MOSS-TTS-Nano','',connection_type='self_hosted',protocol='openai',auth_mode='none')
 lib=VoiceLibrary(configs,httpx.MockTransport(lambda r:httpx.Response(200,json={'voices':['default'],'uploaded_voices':[]})))
 page=asyncio.run(lib.list(nano['id']))
 assert page['voices'][0]['id']=='default'
 req=command(project,nano,parameters={'voice':'default'})
 result=runner.prepare(req,session=project[2])
 print('Maintainer Nano: default is offered; direct submission =>',result.status)
 assert result.status=='accepted'
print('No real provider writes or inference executed')
