// Temporary verify-app flow: home and analysis pages after the service area narrowed to rainfall districts.
export default async ({ page, baseUrl, screenshot }) => {
  await page.goto(baseUrl);
  await page.getByText('서비스 지역 5개 구').first().waitFor({ timeout: 90000 });
  await page.getByText('주변 주차장 4개').first().waitFor({ timeout: 60000 });
  await screenshot('home');
  await page.getByRole('button', { name: '분석 데이터 결과' }).click();
  await page.getByText('분석 대상 주차장').first().waitFor({ timeout: 60000 });
  await page.waitForTimeout(3000);
  await screenshot('analysis');
  const text = await page.locator('body').innerText();
  const svgText = await page.locator('svg text').evaluateAll((nodes) => nodes.map((node) => node.textContent || ''));
  console.log('analysis svg labels: ' + svgText.filter(Boolean).join(','));
  const hits = [text, ...svgText].filter((value) => value.includes('미산정'));
  if (hits.length) throw new Error('analysis page still shows 미산정: ' + hits.map((value) => value.slice(Math.max(0, value.indexOf('미산정') - 60), value.indexOf('미산정') + 20)).join(' | '));
};
