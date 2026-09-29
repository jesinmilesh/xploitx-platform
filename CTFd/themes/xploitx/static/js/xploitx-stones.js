/**
 * XploitxCTF 3D Infinity Stones Track Selector
 * Procedural Faceted Cosmic Gemstones with Glistening Particle Shimmer & Interactive Filtering
 */

(function () {
  'use strict';

  // Track definitions (Order matching exact Infinity Stones sequence in reference photo: Blue -> Yellow -> Red -> Purple -> Green -> Pink)
  const STONES_DATA = [
    {
      id: 'osint',
      name: 'OSINT',
      fullName: 'Open Source Intelligence',
      stoneType: 'osint',
      colorHex: 0x0090ff,          // Electric Sapphire Blue
      baseColorHex: 0x001d52,      // Deep space crystal body
      coreColorHex: 0xaae0ff,      // White-hot cyan-blue core
      colorCss: '#0090ff',
      glowCss: 'rgba(0, 144, 255, 0.85)',
      categories: ['osint', 'recon', 'intel', 'geo', 'social'],
      subTracks: ['Social Recon', 'Geolocation', 'Domain Intel', 'All OSINT'],
      desc: 'Information Gathering & Digital Footprinting'
    },
    {
      id: 'forensics',
      name: 'FORENSICS',
      fullName: 'Digital Forensics',
      stoneType: 'forensics',
      colorHex: 0xffea00,          // Radiant Solar Yellow
      baseColorHex: 0x5a3f00,      // Deep amber-gold crystal body
      coreColorHex: 0xfffca8,      // White-hot golden solar core
      colorCss: '#ffea00',
      glowCss: 'rgba(255, 234, 0, 0.9)',
      categories: ['forensics', 'forensic', 'pcap', 'network', 'memory', 'disk', 'wireshark'],
      subTracks: ['PCAP Analysis', 'Memory Dumps', 'Disk Artifacts', 'All Forensics'],
      desc: 'Packet Captures, Memory Imaging & Incident Investigation'
    },
    {
      id: 'stego',
      name: 'STEGANOGRAPHY',
      fullName: 'Steganography',
      stoneType: 'stego',
      colorHex: 0xff1744,          // Fiery Crimson Red
      baseColorHex: 0x520011,      // Deep ruby crystal body
      coreColorHex: 0xff99a8,      // White-hot crimson core
      colorCss: '#ff1744',
      glowCss: 'rgba(255, 23, 68, 0.95)',
      categories: ['stego', 'steganography', 'audio', 'image', 'lsb', 'hidden'],
      subTracks: ['LSB & Visual', 'Audio Spectrograms', 'Polyglot Files', 'All Stego'],
      desc: 'Hidden Secrets in Pixels, Audio Waves & Data Containers'
    },
    {
      id: 'crypto',
      name: 'CRYPTOGRAPHY',
      fullName: 'Cryptography',
      stoneType: 'crypto',
      colorHex: 0xa855f7,          // Mystic Royal Purple
      baseColorHex: 0x380062,      // Deep amethyst crystal body
      coreColorHex: 0xebbeff,      // White-hot violet-magenta core
      colorCss: '#a855f7',
      glowCss: 'rgba(168, 85, 247, 0.9)',
      categories: ['crypto', 'cryptography', 'rsa', 'cipher', 'aes', 'hashes'],
      subTracks: ['Classical Ciphers', 'Modern RSA/ECC', 'Cryptanalysis', 'All Crypto'],
      desc: 'Mathematical Ciphers, Asymmetric Math & Key Attacks'
    },
    {
      id: 'reverse',
      name: 'REV ENGINEERING',
      fullName: 'Reverse Engineering',
      stoneType: 'reverse',
      colorHex: 0x00ff66,          // Matrix Emerald Green
      baseColorHex: 0x003d14,      // Deep emerald crystal body
      coreColorHex: 0xb8ffd9,      // White-hot cyan-green core
      colorCss: '#00ff66',
      glowCss: 'rgba(0, 255, 102, 0.85)',
      categories: ['rev', 'reverse', 'reversing', 'binary', 'assembly', 'decompile'],
      subTracks: ['Static Analysis', 'Dynamic Debugging', 'Decompilation', 'All Rev'],
      desc: 'Binary Disassembly, Decompilation & Logic Extraction'
    },
    {
      id: 'others',
      name: 'OTHERS / MULTI',
      fullName: 'Extended Multi-Tracks',
      stoneType: 'others',
      colorHex: 0xff2a85,          // Cosmic Hot Pink
      baseColorHex: 0x540026,      // Deep cosmic rose crystal body
      coreColorHex: 0xffa8cd,      // White-hot pink flare core
      colorCss: '#ff2a85',
      glowCss: 'rgba(255, 42, 133, 0.95)',
      categories: ['web', 'pwn', 'misc', 'hardware', 'jail', 'blockchain', 'cloud'],
      subTracks: ['Web Exploitation', 'Binary / Pwn', 'Miscellaneous', 'Hardware', 'All Others'],
      desc: 'Web Application Hacking, Binary Exploitation & Hardware Labs'
    }
  ];

  window.XploitxStones = {
    data: STONES_DATA,
    activeStone: null,
    activeSubTrack: 'ALL',
    scene: null,
    camera: null,
    renderer: null,
    stones: [],
    starfield: null,
    raycaster: null,
    mouse: null,
    hoveredIndex: -1,
    container: null,
    animFrameId: null,

    // Soft atmospheric colored nebula halo sprite
    createGlowTexture() {
      const canvas = document.createElement('canvas');
      canvas.width = 128;
      canvas.height = 128;
      const ctx = canvas.getContext('2d');
      const cx = 64;
      const cy = 64;

      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, 64);
      grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
      grad.addColorStop(0.2, 'rgba(255, 255, 255, 0.7)');
      grad.addColorStop(0.5, 'rgba(255, 255, 255, 0.22)');
      grad.addColorStop(0.8, 'rgba(255, 255, 255, 0.05)');
      grad.addColorStop(1, 'rgba(255, 255, 255, 0)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 128, 128);

      return new THREE.CanvasTexture(canvas);
    },

    // Burning incandescent white-hot core flare inside the crystal
    createCoreFlareTexture() {
      const canvas = document.createElement('canvas');
      canvas.width = 128;
      canvas.height = 128;
      const ctx = canvas.getContext('2d');
      const cx = 64;
      const cy = 64;

      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, 64);
      grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
      grad.addColorStop(0.25, 'rgba(255, 255, 255, 0.95)');
      grad.addColorStop(0.55, 'rgba(255, 255, 255, 0.55)');
      grad.addColorStop(0.8, 'rgba(255, 255, 255, 0.15)');
      grad.addColorStop(1, 'rgba(255, 255, 255, 0)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 128, 128);

      return new THREE.CanvasTexture(canvas);
    },

    // Enhanced 8-point glittering starburst sparkle texture
    createSparkleTexture() {
      const canvas = document.createElement('canvas');
      canvas.width = 128;
      canvas.height = 128;
      const ctx = canvas.getContext('2d');
      const cx = 64;
      const cy = 64;

      // Radial center core glow
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, 48);
      grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
      grad.addColorStop(0.18, 'rgba(255, 255, 255, 0.9)');
      grad.addColorStop(0.42, 'rgba(255, 255, 255, 0.25)');
      grad.addColorStop(1, 'rgba(255, 255, 255, 0)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 128, 128);

      // 4 primary sharp glittering star spikes
      ctx.fillStyle = 'rgba(255, 255, 255, 0.98)';
      ctx.beginPath();
      ctx.moveTo(cx, 2);
      ctx.lineTo(cx + 6, cy - 6);
      ctx.lineTo(126, cy);
      ctx.lineTo(cx + 6, cy + 6);
      ctx.lineTo(cx, 126);
      ctx.lineTo(cx - 6, cy + 6);
      ctx.lineTo(2, cy);
      ctx.lineTo(cx - 6, cy - 6);
      ctx.closePath();
      ctx.fill();

      // 4 diagonal glittering micro-spikes
      ctx.fillStyle = 'rgba(255, 255, 255, 0.65)';
      ctx.beginPath();
      ctx.moveTo(cx + 34, cy - 34);
      ctx.lineTo(cx + 4, cy - 4);
      ctx.lineTo(cx + 34, cy + 34);
      ctx.lineTo(cx + 4, cy + 4);
      ctx.lineTo(cx - 34, cy + 34);
      ctx.lineTo(cx - 4, cy + 4);
      ctx.lineTo(cx - 34, cy - 34);
      ctx.lineTo(cx - 4, cy - 4);
      ctx.closePath();
      ctx.fill();

      return new THREE.CanvasTexture(canvas);
    },

    // Procedural raw cosmic crystal geometry with sculpted silhouettes matching the reference photo
    createCrystalGeometry(stoneType, seed) {
      // Dodecahedron with 1 subdivision level = 80 triangular facets for authentic raw geode look
      const geom = new THREE.DodecahedronGeometry(1.22, 1);
      const pos = geom.attributes.position;

      for (let i = 0; i < pos.count; i++) {
        let vx = pos.getX(i);
        let vy = pos.getY(i);
        let vz = pos.getZ(i);

        // 1. Unique silhouette shaping per stone type matching the reference photo
        if (stoneType === 'osint') {
          // Blue (Space Stone): Diamond / triangular apex shard with wide base
          if (vy > 0) {
            vx *= 0.72;
            vz *= 0.72;
            vy *= 1.28;
          } else {
            vx *= 1.18;
            vz *= 1.15;
          }
        } else if (stoneType === 'forensics') {
          // Yellow (Mind Stone): Chunky, wide asteroid geode cluster
          vx *= 1.20;
          vy *= 0.90;
          vz *= 1.14;
        } else if (stoneType === 'stego') {
          // Red (Reality Stone): Slanted crystal shard with diagonal shear
          vy *= 1.34;
          vx += vy * 0.22;
          vz *= 0.92;
        } else if (stoneType === 'crypto') {
          // Purple (Power Stone): Horizontally elongated jagged cluster
          vx *= 1.35;
          vy *= 0.88;
          vz *= 1.05;
        } else if (stoneType === 'reverse') {
          // Green (Time Stone): Upright faceted emerald block
          vy *= 1.25;
          vx *= 1.04;
          vz *= 1.08;
        } else if (stoneType === 'others') {
          // Pink (Soul Stone variant): Asymmetric beveled rhomboid shard
          vy *= 1.18;
          vx *= 1.12;
          vz += vx * 0.24;
        }

        // 2. Multi-octave pseudo-random displacement for crisp, rugged cosmic geode facets
        const hash1 = Math.sin(vx * 13.123 + vy * 37.456 + vz * 53.789 + seed) * 43758.5453;
        const offset1 = ((hash1 - Math.floor(hash1)) - 0.5) * 0.38;

        const hash2 = Math.sin(vx * 29.871 + vy * 61.233 + vz * 19.412 + seed * 2.3) * 23421.631;
        const offset2 = ((hash2 - Math.floor(hash2)) - 0.5) * 0.18;

        const totalOffset = offset1 + offset2;
        pos.setXYZ(i, vx + vx * totalOffset, vy + vy * totalOffset, vz + vz * totalOffset);
      }

      geom.computeVertexNormals();
      return geom;
    },

    // Distant twinkling micro-starfield in deep space
    createDeepSpaceStarfield() {
      const count = 160;
      const geom = new THREE.BufferGeometry();
      const pos = new Float32Array(count * 3);
      for (let i = 0; i < count; i++) {
        pos[i * 3] = (Math.random() - 0.5) * 36;
        pos[i * 3 + 1] = (Math.random() - 0.5) * 16;
        pos[i * 3 + 2] = -12 - Math.random() * 12;
      }
      geom.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      const mat = new THREE.PointsMaterial({
        size: 0.16,
        color: 0xccddff,
        transparent: true,
        opacity: 0.65,
        blending: THREE.AdditiveBlending
      });
      const starfield = new THREE.Points(geom, mat);
      this.scene.add(starfield);
      this.starfield = starfield;
    },

    init() {
      this.container = document.getElementById('xploitx-stones-canvas-container');
      if (!this.container || typeof THREE === 'undefined') {
        return;
      }

      const width = this.container.clientWidth;
      const height = this.container.clientHeight || 340;

      // 1. Scene
      this.scene = new THREE.Scene();

      // 2. Camera
      this.camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
      this.camera.position.set(0, 0.25, 11.5);

      if (width < 600) {
        this.camera.position.z = 17;
      } else if (width < 992) {
        this.camera.position.z = 13.5;
      }

      // 3. Renderer
      this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      this.renderer.setSize(width, height);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
      this.renderer.toneMappingExposure = 1.35;
      this.container.innerHTML = '';
      this.container.appendChild(this.renderer.domElement);

      // 4. Cosmic Starfield & Atmospheric Lighting
      this.createDeepSpaceStarfield();

      const ambientLight = new THREE.AmbientLight(0x0c152a, 1.1);
      this.scene.add(ambientLight);

      // Strong directional key light for sharp facet reflections / glints
      const topKeyLight = new THREE.DirectionalLight(0xffffff, 2.0);
      topKeyLight.position.set(5, 12, 10);
      this.scene.add(topKeyLight);

      const bottomRimLight = new THREE.DirectionalLight(0x00d4ff, 0.85);
      bottomRimLight.position.set(-8, -6, -6);
      this.scene.add(bottomRimLight);

      const magentaRimLight = new THREE.DirectionalLight(0xff00aa, 0.7);
      magentaRimLight.position.set(8, -6, -6);
      this.scene.add(magentaRimLight);

      // 5. Build the 6 Stones
      const sparkleTex = this.createSparkleTexture();
      const glowTex = this.createGlowTexture();
      const coreFlareTex = this.createCoreFlareTexture();
      this.stones = [];

      const spacing = width < 600 ? 2.5 : 2.75;
      const startX = -((STONES_DATA.length - 1) * spacing) / 2;

      STONES_DATA.forEach((stoneData, idx) => {
        const group = new THREE.Group();
        group.position.x = startX + idx * spacing;
        group.position.y = 0;
        group.userData = {
          index: idx,
          data: stoneData,
          baseY: 0,
          baseScale: 1.0,
          targetScale: 1.0,
          currentScale: 1.0,
          rotSpeedX: 0.005 + (idx % 3) * 0.002,
          rotSpeedY: 0.008 + (idx % 2) * 0.003
        };

        // A. Faceted Raw Crystal Mesh with authentic geode facets
        const geom = this.createCrystalGeometry(stoneData.stoneType, idx * 8.3);
        const mat = new THREE.MeshPhongMaterial({
          color: stoneData.baseColorHex,
          emissive: stoneData.colorHex,
          emissiveIntensity: 0.44,
          specular: 0xffffff,
          shininess: 160,
          flatShading: true,
          transparent: true,
          opacity: 0.84,
          depthWrite: true
        });
        const mesh = new THREE.Mesh(geom, mat);
        group.add(mesh);

        // B. Incandescent White-Hot Burning Core Flare (shines from inside the rock!)
        const coreFlareMat = new THREE.SpriteMaterial({
          map: coreFlareTex,
          color: stoneData.coreColorHex,
          blending: THREE.AdditiveBlending,
          transparent: true,
          opacity: 0.96,
          depthWrite: false
        });
        const coreFlareSprite = new THREE.Sprite(coreFlareMat);
        coreFlareSprite.scale.set(1.45, 1.45, 1.0);
        group.add(coreFlareSprite);

        // C. Inner Glowing Crystalline Wireframe Core
        const coreGeom = new THREE.IcosahedronGeometry(0.72, 0);
        const coreMat = new THREE.MeshBasicMaterial({
          color: stoneData.colorHex,
          wireframe: true,
          transparent: true,
          opacity: 0.45
        });
        const coreMesh = new THREE.Mesh(coreGeom, coreMat);
        group.add(coreMesh);

        // D. Internal Radiant Point Light & Core Light
        const pointLight = new THREE.PointLight(stoneData.colorHex, 4.2, 7.5);
        group.add(pointLight);
        const innerWhiteLight = new THREE.PointLight(0xffffff, 2.0, 3.5);
        group.add(innerWhiteLight);

        // E. Outer Atmospheric Nebula Halo (Glow Sprite)
        const auraMat = new THREE.SpriteMaterial({
          map: glowTex,
          color: stoneData.colorHex,
          transparent: true,
          opacity: 0.52,
          blending: THREE.AdditiveBlending,
          depthWrite: false
        });
        const auraSprite = new THREE.Sprite(auraMat);
        auraSprite.position.z = -0.35;
        auraSprite.scale.set(4.8, 4.8, 1.0);
        group.add(auraSprite);

        // F. Glistening Sparkle Particle Aura (48 Particles per Stone)
        const particleCount = 48;
        const particleGeom = new THREE.BufferGeometry();
        const pPositions = new Float32Array(particleCount * 3);
        const pPhases = new Float32Array(particleCount);
        const pRadii = new Float32Array(particleCount);
        const pSpeeds = new Float32Array(particleCount);
        const pInclinations = new Float32Array(particleCount);

        for (let p = 0; p < particleCount; p++) {
          const theta = Math.random() * Math.PI * 2;
          const phi = (Math.random() - 0.5) * Math.PI;
          const radius = 1.35 + Math.random() * 1.05;

          pPositions[p * 3] = radius * Math.cos(phi) * Math.cos(theta);
          pPositions[p * 3 + 1] = radius * Math.sin(phi);
          pPositions[p * 3 + 2] = radius * Math.cos(phi) * Math.sin(theta);

          pPhases[p] = Math.random() * Math.PI * 2;
          pRadii[p] = radius;
          pSpeeds[p] = 1.4 + Math.random() * 2.8;
          pInclinations[p] = (Math.random() - 0.5) * 0.8;
        }

        particleGeom.setAttribute('position', new THREE.BufferAttribute(pPositions, 3));

        const particleMat = new THREE.PointsMaterial({
          size: 0.48,
          map: sparkleTex,
          blending: THREE.AdditiveBlending,
          depthWrite: false,
          transparent: true,
          color: stoneData.colorHex,
          opacity: 0.92
        });

        const particles = new THREE.Points(particleGeom, particleMat);
        group.add(particles);

        this.scene.add(group);
        this.stones.push({
          group,
          mesh,
          coreMesh,
          coreFlareSprite,
          coreFlareMat,
          pointLight,
          innerWhiteLight,
          auraSprite,
          auraMat,
          particles,
          particleMat,
          pPhases,
          pRadii,
          pSpeeds,
          pInclinations,
          data: stoneData
        });
      });

      // 6. Interaction Setup
      this.raycaster = new THREE.Raycaster();
      this.mouse = new THREE.Vector2(-999, -999);

      this.bindEvents();
      this.animate();
    },

    bindEvents() {
      const dom = this.renderer.domElement;

      // Mouse Move (Raycasting & Hover)
      dom.addEventListener('mousemove', (e) => {
        const rect = dom.getBoundingClientRect();
        this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        this.checkHover();
      });

      dom.addEventListener('mouseleave', () => {
        this.mouse.set(-999, -999);
        this.clearHover();
      });

      // Click (Select & Filter)
      dom.addEventListener('click', (e) => {
        const rect = dom.getBoundingClientRect();
        this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

        this.raycaster.setFromCamera(this.mouse, this.camera);
        const meshes = this.stones.map(s => s.mesh);
        const intersects = this.raycaster.intersectObjects(meshes);

        if (intersects.length > 0) {
          const hitMesh = intersects[0].object;
          const hitStone = this.stones.find(s => s.mesh === hitMesh);
          if (hitStone) {
            this.selectStone(hitStone.data.id);
          }
        }
      });

      // Resize
      window.addEventListener('resize', () => {
        if (!this.container || !this.renderer || !this.camera) return;
        const w = this.container.clientWidth;
        const h = this.container.clientHeight || 340;

        this.camera.aspect = w / h;
        if (w < 600) {
          this.camera.position.z = 17;
        } else if (w < 992) {
          this.camera.position.z = 13.5;
        } else {
          this.camera.position.z = 11.5;
        }
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
      });
    },

    checkHover() {
      this.raycaster.setFromCamera(this.mouse, this.camera);
      const meshes = this.stones.map(s => s.mesh);
      const intersects = this.raycaster.intersectObjects(meshes);

      if (intersects.length > 0) {
        const hitMesh = intersects[0].object;
        const index = this.stones.findIndex(s => s.mesh === hitMesh);
        if (index !== this.hoveredIndex) {
          this.hoveredIndex = index;
          this.renderer.domElement.style.cursor = 'pointer';
          this.updateHoverHUD(this.stones[index].data);
        }
      } else {
        this.clearHover();
      }
    },

    clearHover() {
      if (this.hoveredIndex !== -1) {
        this.hoveredIndex = -1;
        this.renderer.domElement.style.cursor = 'default';
        this.updateHoverHUD(null);
      }
    },

    updateHoverHUD(stoneData) {
      const hudEl = document.getElementById('xploitx-stones-hover-label');
      if (!hudEl) return;

      if (!stoneData) {
        if (this.activeStone) {
          const current = STONES_DATA.find(s => s.id === this.activeStone);
          if (current) {
            hudEl.innerHTML = `<span class="hud-tag" style="color: ${current.colorCss}; text-shadow: 0 0 10px ${current.glowCss};"><i class="fas fa-gem me-1"></i> ACTIVE TRACK: ${current.name}</span> <span class="text-muted ms-2 small">[ ${current.desc} ]</span>`;
            return;
          }
        }
        hudEl.innerHTML = `<span class="text-muted small"><i class="fas fa-crosshairs me-1 text-success"></i> SELECT AN INFINITY STONE TO ACCESS TARGET CHALLENGE TRACK</span>`;
        return;
      }

      hudEl.innerHTML = `
        <span class="hud-tag fw-bold" style="color: ${stoneData.colorCss}; text-shadow: 0 0 12px ${stoneData.glowCss};">
          <i class="fas fa-sparkles me-1"></i> ${stoneData.name} SECTOR
        </span>
        <span class="text-light ms-2 small">• ${stoneData.fullName}</span>
        <span class="text-muted ms-2 small d-none d-md-inline">[ ${stoneData.desc} ]</span>
      `;
    },

    selectStone(stoneId, subTrack = 'ALL') {
      const isDeselect = (this.activeStone === stoneId && subTrack === 'ALL' && this.activeSubTrack === 'ALL');
      this.activeStone = isDeselect ? null : stoneId;
      this.activeSubTrack = subTrack;

      // Pulse the chosen stone
      if (this.activeStone) {
        const chosen = this.stones.find(s => s.data.id === this.activeStone);
        if (chosen) {
          chosen.group.userData.targetScale = 1.35;
          setTimeout(() => {
            if (chosen) chosen.group.userData.targetScale = 1.20;
          }, 240);
        }
      }

      // Sync companion button active highlights and glow
      document.querySelectorAll('.xploitx-stone-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.style.boxShadow = '';
      });
      if (this.activeStone) {
        const matchingBtn = document.querySelector(`.xploitx-stone-btn[onclick*="'${this.activeStone}'"]`);
        const stoneInfo = STONES_DATA.find(s => s.id === this.activeStone);
        if (matchingBtn && stoneInfo) {
          matchingBtn.classList.add('active');
          matchingBtn.style.boxShadow = `0 0 18px ${stoneInfo.glowCss}`;
          matchingBtn.style.borderColor = stoneInfo.colorCss;
        }
      } else {
        const allBtn = document.querySelector(`.xploitx-stone-btn[onclick*="null"]`);
        if (allBtn) {
          allBtn.classList.add('active');
        }
      }

      // Update HUD UI
      this.updateHoverHUD(null);
      this.renderControlsUI();
      this.filterChallenges();
    },

    renderControlsUI() {
      const panel = document.getElementById('xploitx-stones-subtracks-bar');
      if (!panel) return;

      if (!this.activeStone) {
        panel.style.display = 'none';
        return;
      }

      const activeData = STONES_DATA.find(s => s.id === this.activeStone);
      if (!activeData) {
        panel.style.display = 'none';
        return;
      }

      panel.style.display = 'flex';
      panel.style.borderColor = activeData.colorCss;

      let html = `
        <div class="subtracks-header">
          <span class="badge" style="background: ${activeData.glowCss}; border: 1px solid ${activeData.colorCss}; color: #ffffff;">
            <i class="fas fa-gem me-1"></i> ${activeData.name}
          </span>
          <span class="text-muted small ms-2">${activeData.desc}</span>
        </div>
        <div class="subtracks-pills">
      `;

      activeData.subTracks.forEach(sub => {
        const isActive = (this.activeSubTrack === sub) || (this.activeSubTrack === 'ALL' && sub.startsWith('All'));
        html += `
          <button type="button" class="btn btn-sm subtrack-pill ${isActive ? 'active' : ''}" 
                  style="${isActive ? `background: ${activeData.colorCss} !important; border-color: ${activeData.colorCss} !important; color: #000 !important; font-weight: 800; box-shadow: 0 0 12px ${activeData.glowCss};` : ''}"
                  onclick="XploitxStones.selectSubTrack('${activeData.id}', '${sub}')">
            ${sub}
          </button>
        `;
      });

      html += `
          <button type="button" class="btn btn-sm btn-outline-secondary subtrack-reset ms-auto" onclick="XploitxStones.selectStone(null)">
            <i class="fas fa-times me-1"></i> SHOW ALL TRACKS
          </button>
        </div>
      `;

      panel.innerHTML = html;
    },

    selectSubTrack(stoneId, subTrack) {
      this.activeStone = stoneId;
      this.activeSubTrack = subTrack;
      this.renderControlsUI();
      this.filterChallenges();
    },

    filterChallenges() {
      // Broadcast event for Alpine.js or custom challenge board listener
      window.dispatchEvent(new CustomEvent('xploitx-track-filtered', {
        detail: {
          stoneId: this.activeStone,
          subTrack: this.activeSubTrack,
          categories: this.getActiveCategories()
        }
      }));

      // Direct DOM Filtering for CTFd Challenge Categories
      this.applyDOMFiltering();
    },

    getActiveCategories() {
      if (!this.activeStone) return null;
      const data = STONES_DATA.find(s => s.id === this.activeStone);
      return data ? data.categories : null;
    },

    applyDOMFiltering() {
      const activeData = this.activeStone ? STONES_DATA.find(s => s.id === this.activeStone) : null;
      const categoryBlocks = document.querySelectorAll('.category-header, [data-category-block]');

      // If categories are wrapped in parent blocks, filter them
      document.querySelectorAll('.pt-5, .category-row').forEach(block => {
        const heading = block.querySelector('.category-header h3, h3');
        if (!heading) return;

        const catName = heading.innerText.trim().toLowerCase();

        if (!activeData) {
          block.style.display = '';
          return;
        }

        // SubTrack specific matching
        if (this.activeStone === 'others') {
          if (this.activeSubTrack.includes('Web')) {
            block.style.display = catName.includes('web') ? '' : 'none';
          } else if (this.activeSubTrack.includes('Pwn') || this.activeSubTrack.includes('Binary')) {
            block.style.display = (catName.includes('pwn') || catName.includes('bin') || catName.includes('exploit')) ? '' : 'none';
          } else if (this.activeSubTrack.includes('Misc')) {
            block.style.display = catName.includes('misc') ? '' : 'none';
          } else if (this.activeSubTrack.includes('Hardware')) {
            block.style.display = (catName.includes('hard') || catName.includes('hw')) ? '' : 'none';
          } else {
            // All Others
            const isDedicated = ['osint', 'recon', 'rev', 'binary', 'forensic', 'pcap', 'crypto', 'rsa', 'cipher', 'stego', 'lsb'].some(k => catName.includes(k));
            block.style.display = !isDedicated ? '' : 'none';
          }
          return;
        }

        // Dedicated stone matching
        const matches = activeData.categories.some(term => catName.includes(term));
        block.style.display = matches ? '' : 'none';
      });
    },

    animate() {
      this.animFrameId = requestAnimationFrame(() => this.animate());

      const time = performance.now() * 0.001;

      // Twinkle deep space starfield
      if (this.starfield) {
        this.starfield.material.opacity = 0.52 + Math.sin(time * 1.8) * 0.16;
      }

      this.stones.forEach((stone, i) => {
        const isHovered = (this.hoveredIndex === i);
        const isSelected = (this.activeStone === stone.data.id);

        // Target scale handling
        let targetScale = 1.0;
        if (isSelected) {
          targetScale = 1.22;
        } else if (isHovered) {
          targetScale = 1.14;
        }
        stone.group.userData.targetScale = targetScale;
        stone.group.userData.currentScale += (stone.group.userData.targetScale - stone.group.userData.currentScale) * 0.12;
        const s = stone.group.userData.currentScale;
        stone.group.scale.set(s, s, s);

        // Smooth Floating Bobbing Physics
        const floatY = Math.sin(time * 1.8 + i * 0.95) * 0.24;
        stone.group.position.y = floatY;

        // Rotation (Crystal & Core in counter-rotation for dynamic faceted glinting)
        const speedMult = isHovered ? 2.6 : (isSelected ? 1.7 : 1.0);
        stone.mesh.rotation.y += stone.group.userData.rotSpeedY * speedMult;
        stone.mesh.rotation.x += stone.group.userData.rotSpeedX * speedMult;
        stone.coreMesh.rotation.y -= stone.group.userData.rotSpeedY * speedMult * 1.6;
        stone.coreMesh.rotation.z += 0.003 * speedMult;

        // Incandescent White-Hot Burning Core Flare Pulse (shines through translucent facets)
        const corePulse = Math.sin(time * 4.4 + i * 1.6) * 0.18;
        const coreScale = (isSelected ? 1.88 : (isHovered ? 1.68 : 1.42)) + corePulse;
        stone.coreFlareSprite.scale.set(coreScale, coreScale, 1.0);
        stone.coreFlareMat.opacity = (isSelected ? 1.0 : (isHovered ? 0.96 : 0.88)) + corePulse * 0.1;

        // Pulsing Point Light & Emissive Glow in Stone's Exact Color
        const pulse = Math.sin(time * 3.4 + i * 1.2) * 0.55;
        stone.pointLight.intensity = (isSelected ? 5.2 : (isHovered ? 4.5 : 3.4)) + pulse;
        stone.innerWhiteLight.intensity = (isSelected ? 2.8 : (isHovered ? 2.4 : 1.8)) + pulse * 0.3;
        stone.mesh.material.emissiveIntensity = (isSelected ? 0.88 : (isHovered ? 0.72 : 0.44)) + pulse * 0.18;

        // Radial Atmospheric Nebula Halo Scaling & Breathing Glow Pulse
        const baseAuraScale = isSelected ? 5.4 : (isHovered ? 4.8 : 4.2);
        const auraPulse = Math.sin(time * 2.8 + i) * 0.25;
        const currentAuraScale = baseAuraScale + auraPulse;
        stone.auraSprite.scale.set(currentAuraScale, currentAuraScale, 1.0);
        stone.auraMat.opacity = (isSelected ? 0.85 : (isHovered ? 0.72 : 0.50)) + auraPulse * 0.12;

        // Glistening Sparkle Particles Simulation (3D orbits + twinkle)
        const pPos = stone.particles.geometry.attributes.position.array;
        const count = stone.pPhases.length;

        for (let p = 0; p < count; p++) {
          const speed = stone.pSpeeds[p];
          const phase = stone.pPhases[p] + time * speed * (isHovered ? 2.0 : 1.0);
          const rad = stone.pRadii[p] * (1.0 + Math.sin(phase * 1.4) * 0.14);
          const inc = stone.pInclinations ? stone.pInclinations[p] : 0;

          // Orbit particle around stone with vertical waves
          pPos[p * 3] = rad * Math.cos(phase);
          pPos[p * 3 + 1] = rad * Math.sin(phase * 0.85) * 0.85 + Math.sin(time * 2.0 + p) * 0.15 + inc;
          pPos[p * 3 + 2] = rad * Math.sin(phase);
        }
        stone.particles.geometry.attributes.position.needsUpdate = true;

        // Sparkle material shimmer & glisten according to color
        const shimmer = Math.sin(time * 6.0 + i * 2.2) * 0.15;
        stone.particleMat.size = (0.48 + shimmer) * (isSelected ? 1.45 : (isHovered ? 1.25 : 1.0));
        stone.particleMat.opacity = 0.84 + Math.sin(time * 4.2 + i * 1.8) * 0.16;
      });

      this.renderer.render(this.scene, this.camera);
    }
  };

  // Auto-initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => window.XploitxStones.init());
  } else {
    window.XploitxStones.init();
  }
})();
