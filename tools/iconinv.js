// Lists the visible Steam icons (svg) in a window that tools/icons.py doesn't swap yet: count,
// class, the start of the first path's d (the matcher to use), size, where it sits, nearby text.
//   python3 tools/cef.py eval SP "$(cat tools/iconinv.js)"     (or QuickAccess_uid2, MainMenu_uid2)
(() => {
  const seen = new Map();
  document.querySelectorAll('svg').forEach(s => {
    if (s.parentElement && s.parentElement.closest('svg')) return;
    const r = s.getBoundingClientRect(); if (r.width < 4 || r.height < 4) return; if (getComputedStyle(s).maskImage !== 'none') return;
    const cls = (s.getAttribute('class') || '').trim();
    const p = s.querySelector('path,polygon,rect,circle');
    const d = p ? (p.getAttribute('d') || p.tagName).slice(0, 28) : '';
    const key = cls + '|' + d;
    if (seen.has(key)) { seen.get(key).n++; return; }
    let a = s.parentElement, ctx = [];
    for (let i = 0; i < 3 && a; i++) { const c = (a.className + '').split(' ')[0]; if (c) ctx.push(c.slice(0, 40)); a = a.parentElement; }
    const txt = (s.closest('.Focusable, button, [class*=Item]') || s.parentElement).textContent.trim().slice(0, 20);
    seen.set(key, {n: 1, line: `${cls || '(no class)'} | d=${d} | ${Math.round(r.width)}px | ${ctx.join(' < ')} | "${txt}"`});
  });
  return [...seen.values()].map(v => v.n + 'x ' + v.line).join('\n');
})()
