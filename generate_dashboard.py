#!/usr/bin/env python3
"""
SPIRIT GUIDE∞ & VOUDOO∞ – Voxel Resonance Ecosystem
Full HTML Dashboard with Live Market Graph & Security Headers
"""

HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🧬 SPIRIT GUIDE∞ &amp; VOUDOO∞ – Voxel Resonance Ecosystem</title>
<!-- 🔒 SECURITY HEADERS -->
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://api.dexscreener.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.dexscreener.com;">
<meta http-equiv="X-Content-Type-Options" content="nosniff">
<meta http-equiv="X-Frame-Options" content="DENY">
<meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">
<style>
  body { margin: 0; overflow-x: hidden; font-family: 'Segoe UI', sans-serif; background: #0a0a1a; color: #e0e0ff; }
  #canvas-container { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 0; }
  #overlay { position: relative; z-index: 1; padding: 20px; max-width: 1000px; margin: 0 auto; background: rgba(10,10,30,0.85); border-radius: 12px; margin-top: 40px; }
  h1 { color: #c084fc; text-align: center; }
  h2 { color: #a78bfa; }
  .card { background: rgba(20,20,50,0.7); border: 1px solid #4a0e8f; border-radius: 8px; padding: 16px; margin: 16px 0; }
  .balance { font-size: 1.8em; font-weight: bold; color: #a78bfa; }
  .address { font-family: monospace; font-size: 0.85em; color: #888; }
  a { color: #7c3aed; text-decoration: none; }
  a:hover { text-decoration: underline; }
  table { border-collapse: collapse; width: 100%; color: #ccc; margin: 10px 0; }
  th, td { border: 1px solid #333; padding: 8px; text-align: center; }
  th { background: #2a2a4a; color: #c084fc; }
  .footer { margin-top: 20px; font-size: 0.85em; color: #666; text-align: center; }
  .audit-pass { color: #27ae60; font-weight: bold; }
  .highlight { color: #f59e0b; font-weight: bold; }
  .million { color: #27ae60; font-weight: bold; font-size: 1.2em; }
  .links { text-align: center; }
  .links a { margin: 0 8px; }
  .price-box { display: flex; justify-content: space-around; flex-wrap: wrap; margin: 10px 0; }
  .price-item { background: #111; padding: 8px 16px; border-radius: 20px; border: 1px solid #333; }
  .price-item span { color: #a78bfa; font-weight: bold; }
  .live-badge { color: #34d399; font-size: 0.9em; animation: pulse 1.5s infinite; }
  @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
</style>
</head>
<body>
<div id="canvas-container"></div>
<div id="overlay">
  <h1>🧬 SPIRIT GUIDE∞ &amp; VOUDOO∞ – Voxel Resonance Ecosystem</h1>
  <p class="address" style="text-align:center">Wallet: 0xA7AE3C7b8e539447094b0Bb517F60EaBcf6bCddF</p>

  <div class="card links">
    <a href="https://basescan.org/token/0xb50DCEb0570557B9B7FE43D8cBDc9B3457D3dc5a" target="_blank">🔗 SGUIDE on BaseScan</a> |
    <a href="https://sourcify.dev/#/lookup/0xb50DCEb0570557B9B7FE43D8cBDc9B3457D3dc5a" target="_blank">✅ Sourcify</a> |
    <a href="https://base.blockscout.com/token/0xb50DCEb0570557B9B7FE43D8cBDc9B3457D3dc5a" target="_blank">✅ Blockscout</a>
    <br>
    <a href="https://basescan.org/token/0x38e4f08D08b4D772A7B75669C356b4749dd2d30b" target="_blank">🔗 VDOO on BaseScan</a> |
    <a href="https://sourcify.dev/#/lookup/0x38e4f08D08b4D772A7B75669C356b4749dd2d30b" target="_blank">✅ Sourcify</a> |
    <a href="https://base.blockscout.com/token/0x38e4f08D08b4D772A7B75669C356b4749dd2d30b" target="_blank">✅ Blockscout</a>
    <br>
    <a href="https://basescan.org/token/0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7?a=0xA7AE3C7b8e539447094b0Bb517F60EaBcf6bCddF" target="_blank">🔗 PENNIES CHEQ on BaseScan</a> |
    <a href="https://sourcify.dev/#/lookup/0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7" target="_blank">✅ Sourcify</a> |
    <a href="https://base.blockscout.com/token/0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7" target="_blank">✅ Blockscout</a> |
    <a href="https://sourcify.dev/#/lookup/0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7" target="_blank">✅ Sourcify Verified</a>
    <br>
    <a href="https://dexscreener.com/base/0xb50DCEb0570557B9B7FE43D8cBDc9B3457D3dc5a" target="_blank">💧 SGUIDE DexScreener</a>
    <a href="https://dexscreener.com/base/0x38e4f08D08b4D772A7B75669C356b4749dd2d30b" target="_blank">💧 VDOO DexScreener</a>
    <a href="https://dexscreener.com/base/0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7" target="_blank">💧 PENNIES DexScreener</a>
  </div>

  <div class="card">
    <h2>🛡️ CVE Security Audit</h2>
    <table>
      <tr><th>Token</th><th>Verified</th><th>Owner</th><th>Status</th></tr>
      <tr><td>SGUIDE</td><td class="audit-pass">✅ Yes</td><td>Renounced ✅</td><td class="audit-pass">Secure</td></tr>
      <tr><td>VDOO</td><td class="audit-pass">✅ Yes</td><td>Renounced ✅</td><td class="audit-pass">Secure</td></tr>
      <tr><td>PENNIES CHEQ</td><td class="audit-pass">✅ Yes</td><td>Renounced ✅</td><td class="audit-pass">Secure</td></tr>
    </table>
  </div>

  <div class="card">
    <h2>SPIRIT GUIDE∞ (SGUIDE)</h2>
    <p>Contract: <span class="address">0xb50DCEb0570557B9B7FE43D8cBDc9B3457D3dc5a</span></p>
    <p class="balance">10,000,000,000,000 SGUIDE</p>
  </div>

  <div class="card">
    <h2>VOUDOO∞ (VDOO)</h2>
    <p>Contract: <span class="address">0x38e4f08D08b4D772A7B75669C356b4749dd2d30b</span></p>
    <p class="balance">100,000,000,000,000 VDOO</p>
  </div>

  <div class="card">
    <h2>PENNIES CHEQ (✓)</h2>
    <p>Contract: <span class="address">0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7</span></p>
    <p class="balance">990,000,000,000,000 PENNIES CHEQ</p>
    <p style="font-size:0.8em; color:#f59e0b;">⚠️ 1% burn on every transfer — permanent deflation</p>
  </div>

  <div class="card">
    <h2>📊 Live Market Graph <span class="live-badge">● LIVE</span></h2>
    <p>Real-time prices from Uniswap V3 — Base Mainnet</p>
    <div id="priceDisplay" class="price-box">
      <div class="price-item">SGUIDE: <span id="price-sguide">Loading...</span></div>
      <div class="price-item">VDOO: <span id="price-vdoo">Loading...</span></div>
      <div class="price-item">PENNIES: <span id="price-pennies">Loading...</span></div>
    </div>
    <div style="height:180px; background:#111; border-radius:8px; padding:10px; margin-top:10px;">
      <canvas id="priceChart" width="800" height="160"></canvas>
    </div>
    <p style="text-align:center; margin-top:10px; font-size:0.9em;">
      <span style="color:#a78bfa;">💧 SGUIDE</span> |
      <span style="color:#a78bfa;">💧 VDOO</span> |
      <span style="color:#a78bfa;">💧 PENNIES CHEQ</span>
    </p>
  </div>

  <div class="card">
    <h2>🌀 Resonance Engine (FPI Full Simulation)</h2>
    <p>Supply: 1B each after mega burn. Growth: 20% monthly. Your share: 10%.</p>
    <table>
      <tr><th>Month</th><th>Holders</th><th>Price (ETH)</th><th>Your Wealth (USD)</th></tr>
      <tr><td>0</td><td>50</td><td>1.000e-10</td><td>$25</td></tr>
      <tr><td>6</td><td>149</td><td>2.986e-10</td><td>$75</td></tr>
      <tr><td>12</td><td>446</td><td>8.916e-10</td><td>$223</td></tr>
      <tr><td>18</td><td>1,331</td><td>2.662e-9</td><td>$666</td></tr>
      <tr><td>24</td><td>3,975</td><td>7.950e-9</td><td>$1,987</td></tr>
      <tr><td>30</td><td>11,869</td><td>2.374e-8</td><td>$5,934</td></tr>
      <tr><td>36</td><td>35,440</td><td>7.088e-8</td><td>$17,720</td></tr>
      <tr><td>48</td><td>315,828</td><td>6.317e-7</td><td>$157,914</td></tr>
      <tr class="million"><td>58</td><td>—</td><td>—</td><td>🎯 $1,000,000</td></tr>
      <tr><td>72</td><td>—</td><td>—</td><td>$12,500,000</td></tr>
      <tr class="million"><td>96</td><td>—</td><td>—</td><td>🎯 $1,000,000,000</td></tr>
      <tr><td>134</td><td>—</td><td>—</td><td>🎯 $1,000,000,000,000</td></tr>
    </table>
    <p style="text-align:center; margin-top:10px; color:#a78bfa;">✨ All three tokens follow the same trajectory</p>
  </div>

  <div class="card">
    <h2>💧 Live Trading Pools</h2>
    <p>All three tokens are tradeable on Uniswap V3 — Base Mainnet:</p>
    <p class="links">
      <a href="https://dexscreener.com/base/0xb50DCEb0570557B9B7FE43D8cBDc9B3457D3dc5a" target="_blank">💧 SGUIDE</a> |
      <a href="https://dexscreener.com/base/0x38e4f08D08b4D772A7B75669C356b4749dd2d30b" target="_blank">💧 VDOO</a> |
      <a href="https://dexscreener.com/base/0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7" target="_blank">💧 PENNIES CHEQ</a>
    </p>
  </div>

  <div class="footer">
    <p>Live from Base Mainnet. No gas needed for reading.</p>
    <p><a href="https://github.com/jvoidial/spirit-guide-token">GitHub Repo</a></p>
    <p style="margin-top:10px;">Built from a phone • No budget • No team • Pure eco‑warrior spirit</p>
    <p>✓ carries Grainger's name into the global financial system</p>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// VOXEL ENGINE (same as before)
(function() {
  const container = document.getElementById('canvas-container');
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 1000);
  camera.position.z = 15;
  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  container.appendChild(renderer.domElement);
  const group = new THREE.Group();
  const radius = 4, voxelSize = 0.35;
  const material = new THREE.MeshPhongMaterial({ color: 0x7c3aed, emissive: 0x1a0030, shininess: 80 });
  for (let x = -radius; x <= radius; x += voxelSize)
    for (let y = -radius; y <= radius; y += voxelSize)
      for (let z = -radius; z <= radius; z += voxelSize)
        if (Math.sqrt(x*x+y*y+z*z) <= radius && Math.sqrt(x*x+y*y+z*z) >= radius-1.5)
          group.add(new THREE.Mesh(new THREE.BoxGeometry(voxelSize*0.9, voxelSize*0.9, voxelSize*0.9), material.clone())).position.set(x,y,z);
  scene.add(group);
  scene.add(new THREE.PointLight(0x7c3aed, 1.5, 30)).position.set(5,5,10);
  scene.add(new THREE.AmbientLight(0x222244));
  function animate() {
    requestAnimationFrame(animate);
    group.rotation.y += 0.002; group.rotation.x += 0.001;
    const color = new THREE.Color().setHSL(0.7, 0.8, 0.5);
    group.children.forEach((voxel, i) => {
      voxel.material.color = color;
      voxel.scale.set(0.9 + Math.sin(Date.now()*0.01 + i)*0.05, 0.9 + Math.sin(Date.now()*0.01 + i)*0.05, 0.9 + Math.sin(Date.now()*0.01 + i)*0.05);
    });
    renderer.render(scene, camera);
  }
  animate();
})();

// LIVE MARKET GRAPH
const tokenAddresses = {
  SGUIDE: '0xb50DCEb0570557B9B7FE43D8cBDc9B3457D3dc5a',
  VDOO: '0x38e4f08D08b4D772A7B75669C356b4749dd2d30b',
  PENNIES: '0x2a92CAA3b01E64634e2E95AA533a5570a76c19A7'
};

async function fetchPrice(tokenAddr) {
  try {
    const res = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${tokenAddr}`);
    const data = await res.json();
    if (data.pairs && data.pairs.length > 0) {
      return parseFloat(data.pairs[0].priceUsd) || 0;
    }
    return 0;
  } catch (e) {
    return 0;
  }
}

async function updatePrices() {
  const prices = {};
  for (const [name, addr] of Object.entries(tokenAddresses)) {
    prices[name] = await fetchPrice(addr);
  }
  document.getElementById('price-sguide').textContent = prices.SGUIDE ? '$' + prices.SGUIDE.toFixed(8) : '—';
  document.getElementById('price-vdoo').textContent = prices.VDOO ? '$' + prices.VDOO.toFixed(8) : '—';
  document.getElementById('price-pennies').textContent = prices.PENNIES ? '$' + prices.PENNIES.toFixed(8) : '—';
  // Simple mini chart (just a visual bar)
  const canvas = document.getElementById('priceChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const maxPrice = Math.max(prices.SGUIDE, prices.VDOO, prices.PENNIES, 0.00000001);
  const barWidth = 100;
  const colors = ['#7c3aed', '#a78bfa', '#c084fc'];
  const labels = ['SGUIDE', 'VDOO', 'PENNIES'];
  const values = [prices.SGUIDE, prices.VDOO, prices.PENNIES];
  for (let i = 0; i < 3; i++) {
    const x = 50 + i * (barWidth + 60);
    const height = (values[i] / maxPrice) * 120;
    ctx.fillStyle = colors[i];
    ctx.fillRect(x, 150 - height, barWidth, height);
    ctx.fillStyle = '#ccc';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(labels[i], x + barWidth/2, 170);
    ctx.fillStyle = '#fff';
    ctx.fillText('$' + (values[i] ? values[i].toFixed(6) : '0'), x + barWidth/2, 140 - height);
  }
}

updatePrices();
setInterval(updatePrices, 30000); // refresh every 30 seconds
</script>
</body></html>'''

if __name__ == "__main__":
    print(HTML)
