export function MainLayout({ header, content, sidebar }) {
  const container = document.createElement('div');
  container.appendChild(header);
  
  const grid = document.createElement('div');
  grid.className = 'dashboard-grid';
  
  const main = document.createElement('main');
  main.appendChild(content);
  
  const aside = document.createElement('aside');
  aside.appendChild(sidebar);
  
  grid.appendChild(main);
  grid.appendChild(aside);
  container.appendChild(grid);
  
  return container;
}
