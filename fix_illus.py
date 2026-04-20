with open('/workspace/UniqueColonel/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace <div class="illustration"></div> with <div class="illustration-wrapper"><div class="illustration"></div></div>
new_content = content.replace('<div class="illustration"></div>', '<div class="illustration-wrapper"><div class="illustration"></div></div>')

with open('/workspace/UniqueColonel/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
