module.exports = async (page, scenario, vp) => {
  await page.evaluateOnNewDocument(() => {
    window.sessionStorage.setItem('cherenkov_token', 'dummy-token');
  });
};
