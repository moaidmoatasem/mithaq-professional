module.exports = async (page, scenario, vp) => {
  console.log('SCENARIO > ' + scenario.label);

  // Custom interaction handling for clicking selectors if defined
  if (scenario.clickSelector) {
    if (scenario.clickSelector === "INITIATE_NEW_SCAN") {
      await page.evaluate(() => {
        const buttons = Array.from(document.querySelectorAll('button'));
        const initBtn = buttons.find(b => b.textContent && b.textContent.includes('INITIATE NEW SCAN'));
        if (initBtn) {
          initBtn.click();
        } else {
          console.error('Could not find INITIATE NEW SCAN button!');
        }
      });
      // Wait for modal animation to settle
      await new Promise(resolve => setTimeout(resolve, scenario.postInteractionWait || 1000));
    } else {
      await page.waitForSelector(scenario.clickSelector);
      await page.click(scenario.clickSelector);
      if (scenario.postInteractionWait) {
        await new Promise(resolve => setTimeout(resolve, scenario.postInteractionWait));
      }
    }
  }
};
