export function StatCard({ label, value, id }) {
  const card = document.createElement('div');
  card.className = 'stat-card';
  card.innerHTML = `
    <div class="small">${label}</div>
    <div class="stat-value" id="${id}">${value}</div>
  `;
  return card;
}
