/**
 * Graphics Compatibility Script for ChosyTable
 * Detects Intel graphics and applies necessary fixes for color rendering issues
 */

(function() {
    'use strict';
    
    // Detect Intel graphics
    function detectIntelGraphics() {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        
        if (!gl) {
            return false;
        }
        
        const renderer = gl.getParameter(gl.RENDERER);
        const vendor = gl.getParameter(gl.VENDOR);
        
        // Check for Intel graphics indicators
        const isIntel = renderer && (
            renderer.toLowerCase().includes('intel') ||
            renderer.toLowerCase().includes('iris') ||
            vendor.toLowerCase().includes('intel')
        );
        
        // Clean up
        gl.getExtension('WEBGL_lose_context')?.loseContext();
        
        return isIntel;
    }
    
    // Apply Intel graphics fixes
    function applyIntelGraphicsFixes() {
        console.log('🔧 Applying Intel graphics compatibility fixes...');
        
        // Add Intel graphics class to body
        document.body.classList.add('intel-graphics');
        
        // Force color profile fixes
        const style = document.createElement('style');
        style.textContent = `
            .intel-graphics * {
                color-profile: sRGB;
                -webkit-color-profile: sRGB;
            }
            
            .intel-graphics .main-header {
                background: rgba(255, 255, 255, 0.98) !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
            }
            
            .intel-graphics body {
                background: #ffffff !important;
            }
            
            .intel-graphics body::before {
                display: none !important;
            }
            
            .intel-graphics .hero-section {
                background: #ffffff !important;
            }
        `;
        document.head.appendChild(style);
        
        // Disable CSS animations if causing issues
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            const animationStyle = document.createElement('style');
            animationStyle.textContent = `
                .intel-graphics *, 
                .intel-graphics *::before, 
                .intel-graphics *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            `;
            document.head.appendChild(animationStyle);
        }
        
        // Force repaint to fix initial rendering issues
        setTimeout(() => {
            document.body.style.transform = 'translateZ(0)';
            document.body.offsetHeight; // Trigger reflow
            document.body.style.transform = '';
        }, 100);
    }
    
    // Check for macOS specifically (where Intel Iris Plus graphics issues are common)
    function isMacOS() {
        return navigator.platform.toUpperCase().indexOf('MAC') >= 0 ||
               navigator.userAgent.toUpperCase().indexOf('MAC') >= 0;
    }
    
    // Main initialization
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        
        // Check if we're on macOS with Intel graphics
        if (isMacOS() && detectIntelGraphics()) {
            console.log('🖥️ Intel graphics detected on macOS - applying compatibility fixes');
            applyIntelGraphicsFixes();
            
            // Apply additional fixes after a short delay
            setTimeout(() => {
                // Force a repaint of gradient elements
                const gradientElements = document.querySelectorAll('.hero-highlight, .brand-title');
                gradientElements.forEach(el => {
                    el.style.willChange = 'transform';
                    el.offsetHeight; // Trigger reflow
                    el.style.willChange = 'auto';
                });
            }, 500);
        } else {
            console.log('🖥️ No Intel graphics compatibility issues detected');
        }
    }
    
    // Initialize immediately if DOM is ready, otherwise wait
    init();
    
    // Expose debug functions
    window.ChosyTableGraphics = {
        detectIntelGraphics,
        applyFixes: applyIntelGraphicsFixes,
        isMacOS
    };
    
})();