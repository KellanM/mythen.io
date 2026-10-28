// The jungle's layers drift at their own speeds as the page scrolls (far slow, near
// fast), and a thicker layer grows in towards the bottom: the page evolving as you
// go deeper. Off for anyone who asks the system for less motion.
const layers = [...document.querySelectorAll('.layer[data-speed]')];
const root = document.documentElement;
const still = matchMedia('(prefers-reduced-motion: reduce)');
let queued = false;
function update() {
  queued = false;
  const y = scrollY, room = Math.max(1, root.scrollHeight - innerHeight);
  const grow = Math.min(1, y / room);
  root.style.setProperty('--grow', still.matches ? 0.5 : grow.toFixed(3));
  if (still.matches) return;
  for (const el of layers) el.style.backgroundPositionY = `${(-y * el.dataset.speed).toFixed(1)}px`;
}
addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(update); } }, { passive: true });
addEventListener('resize', update);
update();
