/**
 * ChosyTable Frontend JavaScript
 * Handles mobile navigation and interactive features
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navToggle.contains(event.target) && !navMenu.contains(event.target)) {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });
        
        // Close mobile menu when clicking on links
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });
    }
    
    // Flash message auto-hide
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000); // Auto-hide after 5 seconds
    });
    
    // Table row highlighting
    const tableRows = document.querySelectorAll('.styled-table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Form enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        // Add loading state to submit buttons
        const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
        if (submitBtn) {
            form.addEventListener('submit', function() {
                submitBtn.disabled = true;
                submitBtn.style.opacity = '0.7';
                
                // Create loading indicator
                const originalText = submitBtn.value || submitBtn.textContent;
                if (submitBtn.type === 'submit' && submitBtn.tagName === 'INPUT') {
                    submitBtn.value = 'Processing...';
                } else {
                    submitBtn.textContent = 'Processing...';
                }
                
                // Re-enable button after 3 seconds as fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.style.opacity = '1';
                    if (submitBtn.type === 'submit' && submitBtn.tagName === 'INPUT') {
                        submitBtn.value = originalText;
                    } else {
                        submitBtn.textContent = originalText;
                    }
                }, 3000);
            });
        }
        
        // Add focus enhancement to form fields
        const formFields = form.querySelectorAll('input, select, textarea');
        formFields.forEach(field => {
            field.addEventListener('focus', function() {
                this.parentElement.classList.add('field-focused');
            });
            
            field.addEventListener('blur', function() {
                this.parentElement.classList.remove('field-focused');
            });
        });
    });
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary, input[type="submit"]');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple-animation 0.6s ease-out;
                pointer-events: none;
                z-index: 1;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Add CSS for ripple animation and modern effects
    if (!document.querySelector('#modern-effects-styles')) {
        const style = document.createElement('style');
        style.id = 'modern-effects-styles';
        style.textContent = `
            @keyframes ripple-animation {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes slideInLeft {
                from {
                    opacity: 0;
                    transform: translateX(-50px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes scaleIn {
                from {
                    opacity: 0;
                    transform: scale(0.8);
                }
                to {
                    opacity: 1;
                    transform: scale(1);
                }
            }
            
            .animate-fade-in-up {
                animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) both;
            }
            
            .animate-slide-in-left {
                animation: slideInLeft 0.5s cubic-bezier(0.4, 0, 0.2, 1) both;
            }
            
            .animate-scale-in {
                animation: scaleIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
            }
            
            .loading-shimmer {
                background: linear-gradient(
                    90deg,
                    #f0f0f0 25%,
                    #e0e0e0 50%,
                    #f0f0f0 75%
                );
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
            }
            
            @keyframes shimmer {
                0% { background-position: -200% 0; }
                100% { background-position: 200% 0; }
            }
            
            .glass-effect {
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        `;
        document.head.appendChild(style);
    }
    
    // Initialize modern animations and interactions
    initModernEffects();
});

// Modern Effects Initialization
function initModernEffects() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                
                // Add animation class based on element type
                if (element.classList.contains('feature-card')) {
                    element.classList.add('animate-fade-in-up');
                    // Stagger animation for multiple cards
                    const delay = Array.from(element.parentElement.children).indexOf(element) * 150;
                    element.style.animationDelay = `${delay}ms`;
                } else if (element.classList.contains('action-card')) {
                    element.classList.add('animate-scale-in');
                } else if (element.classList.contains('styled-table')) {
                    element.classList.add('animate-slide-in-left');
                } else {
                    element.classList.add('animate-fade-in-up');
                }
                
                observer.unobserve(element);
            }
        });
    }, observerOptions);
    
    // Observe elements for animations
    const animatedElements = document.querySelectorAll(
        '.feature-card, .action-card, .styled-table, .profile-card, .page-header'
    );
    animatedElements.forEach(el => observer.observe(el));
    
    // Enhanced loading states
    initLoadingStates();
    
    // Smooth parallax scrolling
    initParallaxEffects();
    
    // Modern form enhancements
    initFormEnhancements();
    
    // Micro-interactions
    initMicroInteractions();
}

// Enhanced Loading States
function initLoadingStates() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('input[type="submit"], button[type="submit"]');
            if (submitButton) {
                // Create loading spinner
                const spinner = document.createElement('span');
                spinner.innerHTML = '⏳';
                spinner.style.marginRight = '8px';
                
                // Store original content
                const originalContent = submitButton.value || submitButton.textContent;
                
                // Update button with loading state
                if (submitButton.tagName === 'INPUT') {
                    submitButton.value = 'Processing...';
                } else {
                    submitButton.innerHTML = '';
                    submitButton.appendChild(spinner);
                    submitButton.appendChild(document.createTextNode('Processing...'));
                }
                
                submitButton.disabled = true;
                submitButton.style.opacity = '0.7';
                
                // Add loading shimmer effect to form
                form.classList.add('loading-shimmer');
                
                // Restore button after timeout (fallback)
                setTimeout(() => {
                    if (submitButton.tagName === 'INPUT') {
                        submitButton.value = originalContent;
                    } else {
                        submitButton.textContent = originalContent;
                    }
                    submitButton.disabled = false;
                    submitButton.style.opacity = '1';
                    form.classList.remove('loading-shimmer');
                }, 5000);
            }
        });
    });
}

// Smooth Parallax Effects
function initParallaxEffects() {
    let ticking = false;
    
    function updateParallax() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.hero-section, .profile-header');
        
        parallaxElements.forEach((element, index) => {
            const speed = 0.5;
            const yPos = -(scrolled * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
        
        ticking = false;
    }
    
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateParallax);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', requestTick, { passive: true });
}

// Advanced Form Enhancements
function initFormEnhancements() {
    // Floating labels effect
    const formInputs = document.querySelectorAll('input[type="text"], input[type="email"], textarea');
    formInputs.forEach(input => {
        // Create floating label effect
        const label = input.parentElement.querySelector('label');
        if (label) {
            input.addEventListener('focus', () => {
                label.style.transform = 'translateY(-25px) scale(0.8)';
                label.style.color = 'var(--primary-color)';
            });
            
            input.addEventListener('blur', () => {
                if (!input.value) {
                    label.style.transform = 'translateY(0) scale(1)';
                    label.style.color = 'var(--text-secondary)';
                }
            });
            
            // Check if input has value on load
            if (input.value) {
                label.style.transform = 'translateY(-25px) scale(0.8)';
                label.style.color = 'var(--primary-color)';
            }
        }
        
        // Add typing animation
        input.addEventListener('input', (e) => {
            input.parentElement.classList.add('typing');
            
            clearTimeout(input.typingTimer);
            input.typingTimer = setTimeout(() => {
                input.parentElement.classList.remove('typing');
            }, 1000);
        });
    });
    
    // Progressive form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearValidationOnType);
        });
    });
}

// Field validation functions
function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
    } else if (field.type === 'email' && value && !isValidEmail(value)) {
        showFieldError(field, 'Please enter a valid email address');
    } else {
        clearFieldError(field);
    }
}

function clearValidationOnType(e) {
    clearFieldError(e.target);
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    field.style.borderColor = 'var(--error-color)';
    field.classList.add('error');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        color: var(--error-color);
        font-size: 0.8rem;
        margin-top: 4px;
        animation: fadeInUp 0.3s ease;
    `;
    
    field.parentElement.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.style.borderColor = '';
    field.classList.remove('error');
    
    const errorDiv = field.parentElement.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Micro-interactions
function initMicroInteractions() {
    // Card hover effects with magnetic attraction
    const cards = document.querySelectorAll('.feature-card, .action-card, .company-link');
    cards.forEach(card => {
        card.addEventListener('mouseenter', (e) => {
            card.style.transform = 'translateY(-5px) scale(1.02)';
            card.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        });
        
        card.addEventListener('mouseleave', (e) => {
            card.style.transform = 'translateY(0) scale(1)';
        });
        
        // Magnetic effect on mousemove
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            const moveX = x * 0.1;
            const moveY = y * 0.1;
            
            card.style.transform = `translateY(-5px) scale(1.02) translateX(${moveX}px) translateY(${moveY}px)`;
        });
    });
    
    // Enhanced button interactions
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary');
    buttons.forEach(button => {
        button.addEventListener('mousedown', () => {
            button.style.transform = 'scale(0.95)';
        });
        
        button.addEventListener('mouseup', () => {
            button.style.transform = 'scale(1)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'scale(1)';
        });
    });
    
    // Table row animations
    const tableRows = document.querySelectorAll('.styled-table tbody tr');
    tableRows.forEach((row, index) => {
        // Stagger initial animation
        row.style.animationDelay = `${index * 50}ms`;
        
        row.addEventListener('mouseenter', () => {
            row.style.transform = 'translateX(8px) scale(1.01)';
            row.style.boxShadow = 'var(--shadow-card)';
            row.style.zIndex = '10';
            row.style.position = 'relative';
        });
        
        row.addEventListener('mouseleave', () => {
            row.style.transform = 'translateX(0) scale(1)';
            row.style.boxShadow = '';
            row.style.zIndex = '';
            row.style.position = '';
        });
    });
    
    // Smooth scroll to top
    if (!document.querySelector('.scroll-to-top')) {
        const scrollButton = document.createElement('button');
        scrollButton.className = 'scroll-to-top';
        scrollButton.innerHTML = '↑';
        scrollButton.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: var(--gradient-primary);
            color: white;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 1000;
            box-shadow: var(--shadow-float);
        `;
        
        scrollButton.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        
        document.body.appendChild(scrollButton);
        
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                scrollButton.style.opacity = '1';
                scrollButton.style.visibility = 'visible';
            } else {
                scrollButton.style.opacity = '0';
                scrollButton.style.visibility = 'hidden';
            }
        });
    }
}
