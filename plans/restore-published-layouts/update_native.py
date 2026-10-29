"""Prepare native assets and forward pack revisions without touching old packs."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import unicodedata

root = Path(__file__).resolve().parents[3] / 'kala'
research = root.parent / 'kala-layout'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
aliases = {}
for name, style, ident in [('KalaGoti','A','A-18fe73cb912ae3f1'),('KalaJhor','D','D-e4a6be48881da590')]:
    dest = root / f'kala/layout/bn/{name}.json'
    shared = root / f'kala.BaselineTests/Fixtures/SharedKalaLayouts/{name}.json'
    shared.parent.mkdir(parents=True,exist_ok=True)
    shared.write_bytes(dest.read_bytes())
    original = root / f'kala.BaselineTests/Fixtures/OriginalKalaLayouts/{name}.json'
    data = read(original)
    export = research / f'results/kala-keyboards/kala-{name[4:].lower()}.json'
    source = read(export)
    for layer in ['normal','shift']:
        for key in range(65,91):
            assert unicodedata.normalize('NFC',data['layers'][layer][str(key)]) == unicodedata.normalize('NFC',source['layers'][layer][str(key)])
    data['about']['publication'] = 'kala-separate-publication-v1'
    data['about']['arrangementId'] = ident
    data['about']['sourceExportSha256'] = sha(export)
    data['about']['status'] = 'best found under frozen mixed-training J1'
    data['comment'] = f'{data["name"]}: published separate arrangement; native vowel rules. Map CC0-1.0; see NOTICE-KALA-LAYOUTS.txt.'
    write(dest,data)
    # Prove full typing semantics equal before establishing a metadata-only alias.
    before=read(original)
    assert {k:v for k,v in before.items() if k not in ('about','comment')} == {k:v for k,v in data.items() if k not in ('about','comment')}
    aliases[sha(dest)]=sha(original)
    teaching=read(root/f'kala/learning-packs/kala.bn-literature/1.1.0/teaching-paths/{name}.json')
    teaching['layoutHash']=sha(dest)
    teaching['version']='1.1.2'
    write(root/f'tools/bangla-literature/teaching-paths/{name}.json',teaching)

pack=root/'kala/learning-packs/kala.bn-literature/1.1.2'
assert not pack.exists()
shutil.copytree(root/'kala/learning-packs/kala.bn-literature/1.1.0',pack)
for name in ['KalaGoti','KalaJhor']:
    shutil.copyfile(root/f'tools/bangla-literature/teaching-paths/{name}.json',pack/f'teaching-paths/{name}.json')
manifest=read(pack/'manifest.json');manifest['version']='1.1.2'
for item in manifest['files']: item['sha256']=sha(pack/item['path'])
write(pack/'manifest.json',manifest)
bank=root/'kala/learning-packs/kala.bn-typing-check/1.4.2'
assert not bank.exists()
shutil.copytree(root/'kala/learning-packs/kala.bn-typing-check/1.4.1',bank)
data=read(bank/'prompts.json');data['version']='1.4.2';data['variants']=[]
write(root/'artifacts/published-layouts/prompts.json',data)
write(root/'plans/published-layouts/map-aliases.json',{'publication':'kala-separate-publication-v1','validatedMetadataOnlyAliases':aliases})

# Reapply the original physical strokes; keep historical-bank fixture safeguards.
for f in ['BijoyEncodingTests.cs','CollectionV2Tests.cs','CompatibilityTypingTests.cs','ExternalEditorOutputTests.cs','FixedStyleActivationTests.cs','FixedStyleCompositionTests.cs','KalaJhor.tests.json','LearningBlockerTests.cs']:
    p=root/'kala.BaselineTests'/f
    prior=subprocess.check_output(['git','show','1d7a622^:kala.BaselineTests/'+f],cwd=root)
    if f=='KalaJhor.tests.json':
        assert [x['expected'] for x in json.loads(prior)] == [x['expected'] for x in read(p)]
    p.write_bytes(prior)
p=root/'kala.BaselineTests/FixedStyleNativePreservationTests.cs'
s=p.read_text(encoding='utf-8')
prior=subprocess.check_output(['git','show','1d7a622^:kala.BaselineTests/FixedStyleNativePreservationTests.cs'],cwd=root).decode('utf-8-sig')
# Keep test-only OriginalPathFor while restoring original physical examples.
start=s.index('    // Frozen prompt-bank')
end=s.index('    internal static IKeyboardLayoutManager Native',start)
alias_helper=s[start:end]
prior=prior.replace('    internal static IKeyboardLayoutManager Native',alias_helper+'    internal static IKeyboardLayoutManager Native')
p.write_text(prior,encoding='utf-8')
for f in ['kala/Resources/Localization/UiStrings.resx','kala/Resources/Localization/UiStrings.bn.resx']:
    # Only four shared-position strings were changed by the migration.
    p=root/f;p.write_bytes(subprocess.check_output(['git','show','1d7a622^:'+f],cwd=root))
for f in ['kala/Learning/Study/PromptBank.cs','tools/typing-check-prompts/Program.cs','kala.BaselineTests/ContinuousResearchTests.cs','kala.BaselineTests/LiteratureSuccessorTests.cs']:
    p=root/f;s=p.read_text(encoding='utf-8-sig').replace('1.1.1','1.1.2')
    if f.endswith('PromptBank.cs'):
        s=s.replace('CurrentVersion = "1.4.1"','CurrentVersion = "1.4.2"').replace('"1.4.0" or CurrentVersion','"1.4.0" or "1.4.1" or CurrentVersion')
    p.write_text(s,encoding='utf-8')
p=root/'AGENTS.md';s=p.read_text(encoding='utf-8');a=s.index('- Since 29 October');b=s.index('\n- Kala Goti',a)
s=s[:a]+'- Supplied Kala Goti and Kala Jhor use their separate published arrangements `A-18fe73cb912ae3f1` and `D-e4a6be48881da590`. Preserve all 52 positions against immutable original fixtures and their distinct native vowel rules. Native schema remains `1.0`; publication identity lives in `about`. Shared B01 assets remain test-only history. See `plans/published-layouts/VALIDATION.md`.\n'+s[b:];p.write_text(s,encoding='utf-8')
print(json.dumps(aliases,indent=2))
