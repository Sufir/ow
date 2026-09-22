import re

# HTML update
with open('/workspace/UniqueColonel/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

def replacer(match):
    title = match.group(1)
    flavor = match.group(2)
    illus = match.group(3)
    props = match.group(4)
    
    return f'<div class="safe-zone">\n            {illus}\n            {title}\n            {props}\n            {flavor}\n          </div>'

pattern = r'<div class="safe-zone">\s*(<div class="title">.*?</div>)\s*(<div class="flavor">.*?</div>)\s*(<div class="illustration-wrapper">.*?</div>)\s*(<div class="properties">.*?</div>)\s*</div>'
new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)

with open('/workspace/UniqueColonel/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

# CSS update
with open('/workspace/UniqueColonel/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

css = re.sub(r'\.flavor\s*\{[^}]*\}', '''.flavor {
  font-family: Arial, sans-serif;
  font-size: 5.4pt;
  font-style: italic;
  color: #aaaaaa;
  text-align: center;
  margin-top: auto;
  margin-bottom: 0;
  line-height: 1.1;
}''', css)

css = re.sub(r'\.illustration-wrapper\s*\{[^}]*\}', '''.illustration-wrapper {
  display: flex;
  justify-content: center;
  width: 100%;
  margin-bottom: 1.5mm;
}''', css)

css = re.sub(r'\.illustration\s*\{[^}]*\}', '''.illustration {
  width: 90%;
  aspect-ratio: 4 / 3;
  background-color: #111122;
  border: 0.5mm solid #25a4ee;
}''', css)

with open('/workspace/UniqueColonel/style.css', 'w', encoding='utf-8') as f:
    f.write(css)

print("Done")
