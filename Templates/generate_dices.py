html = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <title>Dices Print Sheet</title>
  <link rel="stylesheet" href="./dices/dices.css" />
</head>
<body>

<div class="sheet">
"""

html += "  <!-- KILL START -->\n"
for i in range(20):
    html += '  <div class="cell"><img src="./dices/kill.png" alt="kill"></div>\n'

html += "\n  <!-- RETREAT START -->\n"
for i in range(40):
    html += '  <div class="cell"><img src="./dices/retreat.png" alt="retreat"></div>\n'

html += "\n  <!-- NUMBERS START -->\n"
html += "  <!-- 1 -->\n"
for i in range(20):
    html += '  <div class="cell face--num">1</div>\n'

html += "\n  <!-- 2 -->\n"
for i in range(20):
    html += '  <div class="cell face--num">2</div>\n'

html += "\n  <!-- 3 -->\n"
for i in range(20):
    html += '  <div class="cell face--num">3</div>\n'

html += """
</div>

</body>
</html>
"""

with open("/workspace/Dices.html", "w", encoding="utf-8") as f:
    f.write(html)
