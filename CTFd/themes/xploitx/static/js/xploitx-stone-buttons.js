/**
 * XploitxCTF Realistic HD Infinity Stones Track Selector
 * Lightweight controller for HD Image-based Stone Buttons with dynamic glowing auras and filtering
 */

(function () {
  'use strict';

  // Track definitions (Order matching exact Infinity Stones sequence: Blue -> Yellow -> Red -> Purple -> Green -> Pink)
  const STONES_DATA = [
    {
      id: 'osint',
      name: 'OSINT',
      fullName: 'Open Source Intelligence',
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

    init() {
      this.updateHoverHUD(null);
    },

    selectStone(stoneId, subTrack = 'ALL') {
      const isDeselect = (this.activeStone === stoneId && subTrack === 'ALL' && this.activeSubTrack === 'ALL');
      this.activeStone = isDeselect ? null : stoneId;
      this.activeSubTrack = subTrack;

      // Update button active states
      document.querySelectorAll('.xploitx-stone-item').forEach(btn => {
        btn.classList.remove('active');
      });

      if (this.activeStone) {
        const matchingBtn = document.querySelector(`.xploitx-stone-item[data-stone="${this.activeStone}"]`);
        if (matchingBtn) {
          matchingBtn.classList.add('active');
        }
      }

      this.updateHoverHUD(null);
      this.renderControlsUI();
      this.filterChallenges();
    },

    setHover(stoneId) {
      if (!stoneId) {
        this.updateHoverHUD(null);
        return;
      }
      const data = STONES_DATA.find(s => s.id === stoneId);
      if (data) {
        this.updateHoverHUD(data);
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
      window.dispatchEvent(new CustomEvent('xploitx-track-filtered', {
        detail: {
          stoneId: this.activeStone,
          subTrack: this.activeSubTrack,
          categories: this.getActiveCategories()
        }
      }));
      this.applyDOMFiltering();
    },

    getActiveCategories() {
      if (!this.activeStone) return null;
      const data = STONES_DATA.find(s => s.id === this.activeStone);
      return data ? data.categories : null;
    },

    applyDOMFiltering() {
      const activeData = this.activeStone ? STONES_DATA.find(s => s.id === this.activeStone) : null;
      document.querySelectorAll('.pt-5, .category-row').forEach(block => {
        const heading = block.querySelector('.category-header h3, h3');
        if (!heading) return;

        const catName = heading.innerText.trim().toLowerCase();

        if (!activeData) {
          block.style.display = '';
          return;
        }

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
            const isDedicated = ['osint', 'recon', 'rev', 'binary', 'forensic', 'pcap', 'crypto', 'rsa', 'cipher', 'stego', 'lsb'].some(k => catName.includes(k));
            block.style.display = !isDedicated ? '' : 'none';
          }
          return;
        }

        const matches = activeData.categories.some(term => catName.includes(term));
        block.style.display = matches ? '' : 'none';
      });
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => window.XploitxStones.init());
  } else {
    window.XploitxStones.init();
  }
})();
