"""
generate_standalone_viewer.py
Embeds cookie_shop_scene.glb as base64 into a completely standalone, offline-ready
HTML file: cookie_shop_standalone.html.
Can be opened directly with double-click in any browser without a web server or CORS issues!
"""

import base64
import os

def generate():
    glb_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_scene.glb"
    out_html_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_standalone.html"

    print("Reading GLB file...")
    with open(glb_path, "rb") as f:
        glb_bytes = f.read()

    print(f"Read {len(glb_bytes)} bytes. Converting to Base64...")
    b64_str = base64.b64encode(glb_bytes).decode("utf-8")

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cookie Shop 3D — Standalone Three.js Viewer</title>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
    }}
    body, html {{
      width: 100%;
      height: 100%;
      overflow: hidden;
      background-color: #0a1026;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #fff;
    }}
    #webgl-container {{
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      left: 0;
      z-index: 1;
    }}

    .ui-layer {{
      position: absolute;
      z-index: 10;
      pointer-events: none;
    }}

    header {{
      top: 16px;
      left: 20px;
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      padding: 10px 18px;
      border-radius: 14px;
      pointer-events: auto;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }}
    header h1 {{
      font-size: 16px;
      font-weight: 700;
      color: #ffd166;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    header span.badge {{
      font-size: 11px;
      font-weight: 600;
      padding: 3px 8px;
      background: rgba(162, 213, 198, 0.25);
      color: #a2d5c6;
      border-radius: 20px;
      border: 1px solid rgba(162, 213, 198, 0.3);
    }}

    .nav-panel {{
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 10px;
      background: rgba(15, 23, 42, 0.88);
      backdrop-filter: blur(14px);
      border: 1px solid rgba(255, 255, 255, 0.15);
      padding: 8px 12px;
      border-radius: 16px;
      pointer-events: auto;
      box-shadow: 0 10px 36px rgba(0, 0, 0, 0.5);
    }}
    .btn {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: #f1f5f9;
      padding: 9px 15px;
      border-radius: 10px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .btn:hover {{
      background: rgba(255, 209, 102, 0.2);
      border-color: #ffd166;
      color: #ffd166;
      transform: translateY(-2px);
    }}
    .btn.active {{
      background: #ffd166;
      border-color: #ffd166;
      color: #0f172a;
    }}

    .instructions-card {{
      top: 16px;
      right: 20px;
      width: 260px;
      background: rgba(15, 23, 42, 0.8);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      padding: 14px 16px;
      border-radius: 14px;
      pointer-events: auto;
      font-size: 12px;
      line-height: 1.6;
      color: #cbd5e1;
    }}
    .instructions-card h3 {{
      font-size: 13px;
      color: #f8fafc;
      margin-bottom: 8px;
      font-weight: 700;
    }}

    #loading-screen {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: #0a1026;
      z-index: 100;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      transition: opacity 0.5s ease;
    }}
    .spinner {{
      width: 54px;
      height: 54px;
      border: 4px solid rgba(255, 209, 102, 0.2);
      border-top-color: #ffd166;
      border-radius: 50%;
      animation: spin 0.9s linear infinite;
      margin-bottom: 20px;
    }}
    @keyframes spin {{
      to {{ transform: rotate(360deg); }}
    }}
    #loading-text {{
      font-size: 16px;
      font-weight: 600;
      color: #f1f5f9;
      margin-bottom: 10px;
    }}
  </style>

  <!-- Three.js + Addons via CDN -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/tween.js/18.6.4/tween.umd.js"></script>
</head>
<body>

  <div id="loading-screen">
    <div class="spinner"></div>
    <div id="loading-text">Memuat 3D Cookie Shop Standalone...</div>
  </div>

  <header class="ui-layer">
    <h1>🍪 Cookie Shop 3D</h1>
    <span class="badge">Standalone Offline Viewer</span>
  </header>

  <div class="instructions-card ui-layer">
    <h3>🎮 Kontrol Navigasi</h3>
    <p>• <b>Klik Kiri + Geser:</b> Putar kamera</p>
    <p>• <b>Klik Kanan + Geser:</b> Geser (Pan)</p>
    <p>• <b>Scroll Mouse:</b> Zoom in / out</p>
    <p>• <b>Tombol di Bawah:</b> Beralih kamera (Exterior / Interior / Baker)</p>
  </div>

  <div class="nav-panel ui-layer">
    <button class="btn active" id="btn-city" onclick="switchView('city')">
      🌆 Pemandangan Kota
    </button>
    <button class="btn" id="btn-front" onclick="switchView('front')">
      🏪 Tampak Depan Toko
    </button>
    <button class="btn" id="btn-interior" onclick="switchView('interior')">
      🍪 Masuk ke Toko (Interior)
    </button>
    <button class="btn" id="btn-baker" onclick="switchView('baker')">
      👨‍🍳 Lihat Pelayan (Baker)
    </button>
    <button class="btn" id="btn-anim" onclick="toggleAnimation()">
      ⏸️ Pause Animasi
    </button>
  </div>

  <div id="webgl-container"></div>

  <!-- EMBEDDED GLB DATA -->
  <script>
    const EMBEDDED_GLB_B64 = "{b64_str}";

    let scene, camera, renderer, controls;
    let mixer, clock;
    let isPlaying = true;

    // Presets calibrated for glTF Y-up coordinates:
    // Front Street is at NEGATIVE Z, Interior is at POSITIVE Z
    const views = {{
      city: {{
        pos: new THREE.Vector3(2.8, 9.8, -17.5),
        target: new THREE.Vector3(0.0, 2.5, -0.8)
      }},
      front: {{
        pos: new THREE.Vector3(0.0, 2.8, -9.0),
        target: new THREE.Vector3(0.0, 2.0, 0.0)
      }},
      interior: {{
        pos: new THREE.Vector3(-0.85, 1.40, 0.75),
        target: new THREE.Vector3(0.10, 1.15, 1.90)
      }},
      baker: {{
        pos: new THREE.Vector3(-0.35, 1.35, 1.05),
        target: new THREE.Vector3(-0.35, 1.25, 1.85)
      }}
    }};

    function init() {{
      const container = document.getElementById('webgl-container');

      scene = new THREE.Scene();
      scene.background = new THREE.Color(0x0a1026);
      scene.fog = new THREE.FogExp2(0x0a1026, 0.012);

      camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 300);
      camera.position.copy(views.city.pos);

      renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: 'high-performance' }});
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.outputEncoding = THREE.sRGBEncoding;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.0;
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      container.appendChild(renderer.domElement);

      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.maxPolarAngle = Math.PI / 2 - 0.02;
      controls.minDistance = 0.5;
      controls.maxDistance = 60;
      controls.target.copy(views.city.target);

      // Clean Balanced Lighting for Night Scene
      const ambientLight = new THREE.AmbientLight(0x405575, 0.85);
      scene.add(ambientLight);

      const moonLight = new THREE.DirectionalLight(0x9bb8ff, 1.2);
      moonLight.position.set(-10, 25, -15);
      moonLight.castShadow = true;
      moonLight.shadow.mapSize.width = 2048;
      moonLight.shadow.mapSize.height = 2048;
      moonLight.shadow.bias = -0.0005;
      scene.add(moonLight);

      const shopSpot = new THREE.PointLight(0xffb066, 2.5, 15);
      shopSpot.position.set(0, 3.8, -2.5);
      scene.add(shopSpot);

      const streetLight = new THREE.PointLight(0xffbe69, 3.0, 12);
      streetLight.position.set(3.5, 3.6, -1.8);
      scene.add(streetLight);

      const interiorLight = new THREE.PointLight(0xffd18a, 2.5, 9);
      interiorLight.position.set(0, 2.2, 1.8);
      scene.add(interiorLight);

      const ovenLight = new THREE.PointLight(0xff5500, 2.2, 5);
      ovenLight.position.set(-1.95, 1.0, 2.85);
      scene.add(ovenLight);

      // Star Particles
      createTwinklingStars();

      // Decode and Parse Embedded Base64 GLB
      clock = new THREE.Clock();
      const loader = new THREE.GLTFLoader();

      const binaryString = atob(EMBEDDED_GLB_B64);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {{
        bytes[i] = binaryString.charCodeAt(i);
      }}

      loader.parse(
        bytes.buffer,
        '',
        function (gltf) {{
          const model = gltf.scene;
          model.traverse(function (node) {{
            if (node.isMesh) {{
              node.castShadow = true;
              node.receiveShadow = true;
              const mats = Array.isArray(node.material) ? node.material : [node.material];
              mats.forEach(mat => {{
                if (mat) {{
                  mat.side = THREE.DoubleSide;
                  if (mat.roughness !== undefined) {{
                    mat.roughness = Math.min(mat.roughness, 0.75);
                  }}
                  if (mat.emissive && mat.emissive.getHex() > 0) {{
                    mat.emissiveIntensity = 1.2;
                  }}
                }}
              }});
            }}
          }});

          scene.add(model);

          if (gltf.animations && gltf.animations.length > 0) {{
            mixer = new THREE.AnimationMixer(model);
            gltf.animations.forEach((clip) => {{
              const action = mixer.clipAction(clip);
              action.play();
            }});
          }}

          const loadingScreen = document.getElementById('loading-screen');
          loadingScreen.style.opacity = '0';
          setTimeout(() => {{ loadingScreen.style.display = 'none'; }}, 500);
        }},
        function (error) {{
          console.error('Error parsing embedded GLTF:', error);
          document.getElementById('loading-text').innerText = 'Gagal memproses model 3D.';
        }}
      );

      window.addEventListener('resize', onWindowResize, false);
    }}

    function createTwinklingStars() {{
      const starGeo = new THREE.BufferGeometry();
      const count = 140;
      const positions = new Float32Array(count * 3);
      for (let i = 0; i < count * 3; i += 3) {{
        positions[i] = (Math.random() - 0.5) * 80;
        positions[i + 1] = 12 + Math.random() * 35;
        positions[i + 2] = 15 + Math.random() * 45;
      }}
      starGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      const starMat = new THREE.PointsMaterial({{
        color: 0xfff6d6,
        size: 0.35,
        transparent: true,
        opacity: 0.9
      }});
      scene.add(new THREE.Points(starGeo, starMat));
    }}

    function switchView(viewName) {{
      const v = views[viewName];
      if (!v) return;

      document.querySelectorAll('.nav-panel .btn').forEach(b => b.classList.remove('active'));
      const activeBtn = document.getElementById('btn-' + viewName);
      if (activeBtn) activeBtn.classList.add('active');

      new TWEEN.Tween(camera.position)
        .to({{ x: v.pos.x, y: v.pos.y, z: v.pos.z }}, 1400)
        .easing(TWEEN.Easing.Cubic.InOut)
        .start();

      new TWEEN.Tween(controls.target)
        .to({{ x: v.target.x, y: v.target.y, z: v.target.z }}, 1400)
        .easing(TWEEN.Easing.Cubic.InOut)
        .start();
    }}

    function toggleAnimation() {{
      const btn = document.getElementById('btn-anim');
      if (isPlaying) {{
        clock.stop();
        isPlaying = false;
        btn.innerText = '▶️ Play Animasi';
      }} else {{
        clock.start();
        isPlaying = true;
        btn.innerText = '⏸️ Pause Animasi';
      }}
    }}

    function onWindowResize() {{
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }}

    function animate() {{
      requestAnimationFrame(animate);
      const delta = clock.getDelta();
      if (mixer && isPlaying) {{
        mixer.update(delta);
      }}
      TWEEN.update();
      controls.update();
      renderer.render(scene, camera);
    }}

    window.onload = function () {{
      init();
      animate();
    }};
  </script>
</body>
</html>
"""

    print(f"Writing standalone HTML ({len(html_content)} characters) with UTF-8 encoding...")
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Standalone HTML generated successfully at: {out_html_path}")

if __name__ == "__main__":
    generate()
