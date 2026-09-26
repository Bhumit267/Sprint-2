import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({ 
    headless: true,
    executablePath: 'C:\\Users\\bhumi\\.cache\\puppeteer\\chrome\\win64-154.0.8037.57\\chrome-win64\\chrome.exe'
  });
  const page = await browser.newPage();
  
  try {
    console.log("Navigating to login page...");
    await page.goto('http://localhost:3000/login');
    
    // Login as Admin A
    console.log("Logging in as Admin A...");
    await page.type('input[type="email"]', 'admin@orga.com');
    await page.type('input[type="password"]', 'Password1!');
    await page.click('button[type="submit"]');
    
    // Wait for redirect to /chat
    await page.waitForNavigation();
    let url = page.url();
    console.log(`Redirected to: ${url}`);
    if (!url.includes('/chat')) throw new Error("Admin did not redirect to /chat");

    // Navigate to /documents
    console.log("Navigating to /documents as Admin A...");
    await page.goto('http://localhost:3000/documents');
    await page.waitForSelector('table', { timeout: 5000 });
    
    // Evaluate table contents
    let docsText = await page.evaluate(() => {
      const rows = Array.from(document.querySelectorAll('tbody tr'));
      return rows.map(r => r.innerText).join(' | ');
    });
    console.log(`Admin A Documents: ${docsText}`);
    
    // Clear Local Storage
    await page.evaluate(() => localStorage.clear());
    
    // Login as Admin B
    console.log("Logging in as Admin B...");
    await page.goto('http://localhost:3000/login');
    await page.type('input[type="email"]', 'admin@orgb.com');
    await page.type('input[type="password"]', 'Password1!');
    await page.click('button[type="submit"]');
    
    await page.waitForNavigation();
    url = page.url();
    console.log(`Redirected to: ${url}`);
    if (!url.includes('/chat')) throw new Error("Admin B did not redirect to /chat");

    // Navigate to /documents
    console.log("Navigating to /documents as Admin B...");
    await page.goto('http://localhost:3000/documents');
    
    await page.waitForSelector('table', { timeout: 5000 });
    docsText = await page.evaluate(() => {
      const rows = Array.from(document.querySelectorAll('tbody tr'));
      return rows.map(r => r.innerText).join(' | ');
    });
    console.log(`Admin B Documents: ${docsText}`);

    // Check maintainer redirect
    await page.evaluate(() => localStorage.clear());
    console.log("Logging in as Maintainer...");
    await page.goto('http://localhost:3000/login');
    await page.type('input[type="email"]', 'maintainer_test@docdrift.internal');
    await page.type('input[type="password"]', 'Password1!');
    await page.click('button[type="submit"]');

    await page.waitForNavigation();
    url = page.url();
    console.log(`Redirected to: ${url}`);
    if (!url.includes('/admin/organizations')) throw new Error("Maintainer did not redirect to /admin/organizations");
    
    console.log("✅ All Frontend Authentication flows successful!");

  } catch (error) {
    console.error("Test failed:", error);
  } finally {
    await browser.close();
  }
})();
