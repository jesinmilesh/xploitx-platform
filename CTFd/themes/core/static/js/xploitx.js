/**
 * XPLOITX Interactive Cyber Ambient Engine for CTFd
 * Handles particle canvas, CTF countdown HUD, and cyber sound micro-interactions.
 */

(function () {
    'use strict';

    // Respect user reduced-motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* ==========================================================================
       1. AMBIENT PARTICLES CANVAS
       ========================================================================== */
    function initParticles() {
        if (prefersReducedMotion) return;

        let canvas = document.getElementById('particles-bg');
        if (!canvas) {
            canvas = document.createElement('canvas');
            canvas.id = 'particles-bg';
            document.body.prepend(canvas);
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let width = (canvas.width = window.innerWidth);
        let height = (canvas.height = window.innerHeight);

        const particleCount = width < 768 ? 22 : 45;
        const particles = [];
        const maxDist = 110;

        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.45,
                vy: (Math.random() - 0.5) * 0.45,
                radius: Math.random() * 1.5 + 1,
                color: Math.random() > 0.4 ? 'rgba(0, 255, 102, ' : 'rgba(0, 210, 255, '
            });
        }

        let animationFrameId;
        let isPaused = false;

        function render() {
            if (isPaused) return;

            ctx.clearRect(0, 0, width, height);

            for (let i = 0; i < particles.length; i++) {
                const p = particles[i];
                p.x += p.vx;
                p.y += p.vy;

                if (p.x < 0) p.x = width;
                if (p.x > width) p.x = 0;
                if (p.y < 0) p.y = height;
                if (p.y > height) p.y = 0;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color + '0.6)';
                ctx.fill();

                for (let j = i + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dx = p.x - p2.x;
                    const dy = p.y - p2.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < maxDist) {
                        const alpha = (1 - dist / maxDist) * 0.18;
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.strokeStyle = p.color + alpha + ')';
                        ctx.lineWidth = 0.8;
                        ctx.stroke();
                    }
                }
            }

            animationFrameId = requestAnimationFrame(render);
        }

        window.addEventListener('resize', () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        });

        document.addEventListener('visibilitychange', () => {
            isPaused = document.hidden;
            if (!isPaused) {
                render();
            } else {
                cancelAnimationFrame(animationFrameId);
            }
        });

        render();
    }

    /* ==========================================================================
       2. LIVE CTF COUNTDOWN HUD
       ========================================================================== */
    function initCountdown() {
        const countdownEl = document.getElementById('ctf-countdown');
        if (!countdownEl || !window.init) return;

        const startTimestamp = window.init.start ? window.init.start * 1000 : null;
        const endTimestamp = window.init.end ? window.init.end * 1000 : null;

        if (!startTimestamp && !endTimestamp) {
            countdownEl.style.display = 'none';
            return;
        }

        const daysVal = document.getElementById('cd-days');
        const hoursVal = document.getElementById('cd-hours');
        const minutesVal = document.getElementById('cd-minutes');
        const secondsVal = document.getElementById('cd-seconds');
        const statusHeading = document.getElementById('cd-status-text');

        function updateTimer() {
            const now = Date.now();
            let target = null;
            let status = '';

            if (startTimestamp && now < startTimestamp) {
                target = startTimestamp;
                status = 'MISSION STARTS IN';
            } else if (endTimestamp && now < endTimestamp) {
                target = endTimestamp;
                status = 'MISSION ENDS IN';
            } else if (endTimestamp && now >= endTimestamp) {
                if (statusHeading) statusHeading.textContent = 'OPERATION CONCLUDED';
                if (daysVal) daysVal.textContent = '00';
                if (hoursVal) hoursVal.textContent = '00';
                if (minutesVal) minutesVal.textContent = '00';
                if (secondsVal) secondsVal.textContent = '00';
                return;
            }

            if (!target) {
                countdownEl.style.display = 'none';
                return;
            }

            if (statusHeading) statusHeading.textContent = status;

            const diff = Math.max(0, target - now);
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
            const minutes = Math.floor((diff / 1000 / 60) % 60);
            const seconds = Math.floor((diff / 1000) % 60);

            if (daysVal) daysVal.textContent = String(days).padStart(2, '0');
            if (hoursVal) hoursVal.textContent = String(hours).padStart(2, '0');
            if (minutesVal) minutesVal.textContent = String(minutes).padStart(2, '0');
            if (secondsVal) secondsVal.textContent = String(seconds).padStart(2, '0');
        }

        updateTimer();
        setInterval(updateTimer, 1000);
    }

    /* ==========================================================================
       3. NAVBAR SCROLL EFFECT
       ========================================================================== */
    function initNavbar() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;

        window.addEventListener('scroll', () => {
            if (window.scrollY > 30) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    /* ==========================================================================
       BOOTSTRAP INITIALIZATION
       ========================================================================== */
    document.addEventListener('DOMContentLoaded', () => {
        initParticles();
        initCountdown();
        initNavbar();
    });
})();
