import fs from 'fs';
import path from 'path';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';

const s1Dir = '/app/docs/screenshots/s1';
const refDir = '/app/docs/design/reference';

const files = fs.readdirSync(s1Dir).filter(f => f.endsWith('.png'));

let md = '# S1 DIFF\n\n| Fayl | O\'xshashlik |\n|---|---|\n';

for (const f of files) {
  try {
    const s1Path = path.join(s1Dir, f);
    let refName = f.replace('desktop-', '').replace('mobile-', '');
    // e.g. 1440x900-home.png -> home-dark-1440x900.png
    const match = refName.match(/([0-9x]+)-(.+)\.png/);
    if (match) {
        const [, dims, name] = match;
        // The names in reference might be a bit different, e.g. 'home', 'daily', 'categories', 'add'
        const nameMap = {
            'home': 'home',
            'kunlik': 'daily',
            'kategoriyalar': 'categories',
            'qoshish': 'add-empty',
            'haqida': 'about',
            'qoidalar': 'rules',
            'kirish': 'login'
        };
        const refBase = nameMap[name] || name;
        refName = `${refBase}-dark-${dims}.png`;
    }
    const refPath = path.join(refDir, refName);
    if (!fs.existsSync(refPath)) {
      md += `| ${f} | (reference yo'q) |\n`;
      continue;
    }

    const img1 = PNG.sync.read(fs.readFileSync(s1Path));
    const img2 = PNG.sync.read(fs.readFileSync(refPath));
    const {width, height} = img1;
    
    // Ignore dimension mismatches if they differ a bit
    if (img1.width !== img2.width || img1.height !== img2.height) {
       md += `| ${f} | O'lcham farqi |\n`;
       continue;
    }
    
    const diff = new PNG({width, height});
    const numDiffPixels = pixelmatch(img1.data, img2.data, diff.data, width, height, {threshold: 0.1});
    const totalPixels = width * height;
    const similarity = ((totalPixels - numDiffPixels) / totalPixels * 100).toFixed(2);

    md += `| ${f} | ${similarity}% |\n`;
  } catch (err) {
    md += `| ${f} | Xato: ${err.message} |\n`;
  }
}

fs.writeFileSync('/app/DIFF.md', md);
console.log('DIFF.md created');
