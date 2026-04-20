import re

with open('/workspace/UniqueColonel/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Mapping exact card titles to image filenames
img_map = {
    "Полковник Морроу": "Полковник Морроу.jpeg",
    "Полковник Сигэру Исии": "Сигэру Исии.jpeg",
    "Полковник Амелия Кейн": "Амелия Кейн.jpeg",
    "Полковник Кассий Рэйвен": "Кассий Рэйвен.jpeg",
    "Распутин-2": "Виктор Распутин.jpeg", # Assuming "Виктор Распутин" matches "Распутин-2" based on naming
    "Полковник Эвелина Тайрелл": "Эвелина Тайрелл.jpeg",
    "Полковник Джон Крамер": "Джон Крамер.jpeg",
    "Полковник Роберт Клоуз": "Роберт Клоуз.jpeg",
    "Полковник Виктор “Шайн” Ковач": "Виктор Ковач.jpeg",
    "Полковник Ной Гарднер": "Ной Гарднер.jpeg",
    "Полковник Генри Брут": "Генри Брут.jpeg"
}

def replacer(match):
    title_div = match.group(1)
    title_text = re.search(r'<div class="title">(.*?)</div>', title_div).group(1)
    
    img_filename = img_map.get(title_text)
    
    illus_div = f'<div class="illustration" style="background-image: url(\'images/{img_filename}\'); background-size: cover; background-position: center;"></div>'
    
    return f'<div class="illustration-wrapper">\n              {illus_div}\n            </div>\n            {title_div}'

pattern = r'<div class="illustration-wrapper">\s*<div class="illustration"></div>\s*</div>\s*(<div class="title">.*?</div>)'
new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)

with open('/workspace/UniqueColonel/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Images inserted.")
