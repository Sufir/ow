const fs = require('fs');

let css = fs.readFileSync('Factory/factory-new.css', 'utf-8');

// Replace .token and .token::after blocks
const newCss = css.replace(/\.token \{\s*width: 50mm;\s*height: 50mm;\s*position: relative;[\s\S]*?z-index: -1;\s*\}/, `.token {
  width: 50mm;
  height: 50mm;
  position: relative;
  /* z-index is managed by the grid and pseudo-elements */
}

/* Слой с иллюстрацией жетона */
.token::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: var(--bg-img);
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 1;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
  /* Обрезка под нужную форму */
  clip-path: var(--shape-clip, none);
}

/* Динамический bleed вокруг жетонов (слой фона) */
.token::after {
  content: "";
  position: absolute;
  top: -2mm;
  left: -2mm;
  right: -2mm;
  bottom: -2mm;
  background-color: #191b1c;
  z-index: -1;
  /* Обрезка bleed'а под ту же форму */
  clip-path: var(--shape-clip, none);
}

/* Формы жетонов */
.shape-circle {
  --shape-clip: circle(50% at 50% 50%);
}

.shape-pentagon {
  --shape-clip: polygon(50% 0%, 100% 38%, 81% 100%, 19% 100%, 0% 38%);
}

.shape-hexagon {
  --shape-clip: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
}

.shape-octagon {
  --shape-clip: polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%);
}`);

// Add z-index to .special-symbol
const finalCss = newCss.replace(/\.token \.special-symbol \{([\s\S]*?)position: absolute;/, '.token .special-symbol {$1position: absolute;\n  z-index: 2;');

fs.writeFileSync('Factory/factory.css', finalCss);
console.log('CSS Updated!');
