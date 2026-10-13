#!/usr/bin/env node

const url = process.argv[2] ?? 'https://loophole-one.vercel.app';
const canonical = (process.argv[3] ?? process.env.NEXT_PUBLIC_LOOPHOLE_ADDRESS ?? '0xb87353201cec791cc16c25e8ee1077076d90548e').toLowerCase();
const historical = [
  '0xa77a29c96c30b2a5db865a2ce35c8f396d504f26',
  '0xb14b08cd35fa64fe795e14931dda09999627785d',
];

const page = await fetch(url);
const html = await page.text();
const scripts = [...html.matchAll(/<script[^>]+src="([^"]+)/g)].map(match => new URL(match[1], url).href);
const bundles = await Promise.all(scripts.map(async script => ({script, text: await (await fetch(script)).text()})));
const result = {
  url,
  http_status: page.status,
  final_url: page.url,
  expected_address: canonical,
  html_bytes: Buffer.byteLength(html),
  script_count: scripts.length,
  canonical_address_bundle_hits: bundles.filter(bundle => bundle.text.toLowerCase().includes(canonical)).length,
  historical_address_hits: Object.fromEntries(historical.map(address => [address, bundles.filter(bundle => bundle.text.toLowerCase().includes(address)).length])),
};
console.log(JSON.stringify(result, null, 2));
if (page.status !== 200 || result.canonical_address_bundle_hits === 0) process.exitCode = 1;
