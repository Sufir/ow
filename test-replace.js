const fs = require('fs');
let css = fs.readFileSync('Factory/factory.css', 'utf-8');

// Replace all background-image: url(...) with --bg-img: url(...)
css = css.replace(/background-image:\s*(url\('[^']+'\));/g, '--bg-img: $1;');

fs.writeFileSync('Factory/factory-new.css', css);
console.log('Replaced bg-image to --bg-img');
