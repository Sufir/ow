import re
with open('/workspace/UniqueColonel/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the specific sequence of closing tags
new_content = content.replace('          </div>\n          </div>\n        </div>', '          </div>\n        </div>')

with open('/workspace/UniqueColonel/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
