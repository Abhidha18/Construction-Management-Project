/**
 * Main JavaScript file for Abhidha Construction Management System
 * Handles UI interactions, navigation, and user experience enhancements
 */

(function() {
    'use strict';

    // ============================================================================
    // UTILITY FUNCTIONS
    // ============================================================================

    /**
     * DOM ready helper
     */
    const ready = (callback) => {
        if (document.readyState !== 'loading') {
            callback();
        } else {
            document.addEventListener('DOMContentLoaded', callback);
        }
    };

    /**
     * Smooth scroll helper
     */
    const smoothScroll = (element) => {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    };

    /**
     * Add fade-in animation to elements
     */
    const animateFadeIn = (elements) => {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, {
            threshold: 0.1
        });

        elements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            observer.observe(el);
        });
    };

    // ============================================================================
    // SIDENAV MANAGEMENT
    // ============================================================================

    /**
     * Initialize and manage side navigation
     */
    const initSidenav = () => {
        const openNavBtn = document.getElementById('openNavBtn');
        const closeNavBtn = document.getElementById('closeNavBtn');
        const sideNav = document.getElementById('side-nav');

        if (!sideNav) return;

        const openNav = () => {
            sideNav.classList.add('open');
            sideNav.style.width = '280px';
            document.body.style.overflow = 'hidden';
        };

        const closeNav = () => {
            sideNav.classList.remove('open');
            sideNav.style.width = '0';
            document.body.style.overflow = '';
        };

        // Open navigation
        if (openNavBtn) {
            openNavBtn.addEventListener('click', openNav);
        }

        // Close navigation
        if (closeNavBtn) {
            closeNavBtn.addEventListener('click', closeNav);
        }

        // Close navigation when clicking outside (on overlay)
        sideNav.addEventListener('click', (e) => {
            // Only close if clicking on the sidenav itself (the overlay), not on links
            if (e.target === sideNav) {
                closeNav();
            }
        });

        // Close navigation on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && sideNav.classList.contains('open')) {
                closeNav();
            }
        });

        // Close navigation when clicking on nav links (mobile)
        const navLinks = sideNav.querySelectorAll('a:not(.logout-link)');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                // Small delay for better UX
                setTimeout(closeNav, 150);
            });
        });
    };

    // ============================================================================
    // FLASH MESSAGES AUTO-DISMISS
    // ============================================================================

    /**
     * Auto-dismiss flash messages after a delay
     */
    const initFlashMessages = () => {
        const flashMessages = document.querySelectorAll('.flash');
        
        flashMessages.forEach(flash => {
            // Add fade-in animation
            flash.style.animation = 'slideDown 0.3s ease-out';
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                flash.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                flash.style.opacity = '0';
                flash.style.transform = 'translateY(-20px)';
                
                setTimeout(() => {
                    if (flash.parentElement) {
                        flash.parentElement.removeChild(flash);
                    }
                }, 300);
            }, 5000);
        });
    };

    // ============================================================================
    // FORM ENHANCEMENTS
    // ============================================================================

    /**
     * Enhance form inputs with better UX
     */
    const enhanceForms = () => {
        const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"], input[type="date"], input[type="time"], textarea');
        
        inputs.forEach(input => {
            // Add focus effect
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
                
                // Validate on blur
                if (this.required && !this.value.trim()) {
                    this.style.borderColor = '#ef4444';
                } else {
                    this.style.borderColor = '';
                }
            });

            // Add input validation feedback
            input.addEventListener('input', function() {
                if (this.style.borderColor === 'rgb(239, 68, 68)') {
                    if (this.value.trim()) {
                        this.style.borderColor = '';
                    }
                }
            });
        });

        // Enhance form submissions
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const submitBtn = this.querySelector('button[type="submit"]');
                
                if (submitBtn) {
                    // Disable button to prevent double submission
                    submitBtn.disabled = true;
                    submitBtn.textContent = submitBtn.textContent.includes('Saving') 
                        ? submitBtn.textContent 
                        : 'Saving...';
                    
                    // Re-enable after 3 seconds as fallback
                    setTimeout(() => {
                        submitBtn.disabled = false;
                    }, 3000);
                }
            });
        });
    };

    // ============================================================================
    // CARD ANIMATIONS
    // ============================================================================

    /**
     * Add hover and scroll animations to cards
     */
    const initCardAnimations = () => {
        const cards = document.querySelectorAll('.card, .dashboard-card, .project-card-container, .person-card, .appointment-card');
        
        if (cards.length > 0) {
            animateFadeIn(Array.from(cards));
        }
    };

    // ============================================================================
    // BUTTON ENHANCEMENTS
    // ============================================================================

    /**
     * Add ripple effect to buttons
     */
    const initButtonRipples = () => {
        const buttons = document.querySelectorAll('.btn');
        
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple');
                
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    };

    // ============================================================================
    // REMINDER CHECKBOX ENHANCEMENTS
    // ============================================================================

    /**
     * Enhance reminder checkboxes with better UX
     */
    const enhanceReminders = () => {
        const checkboxes = document.querySelectorAll('.reminder-list input[type="checkbox"]');
        
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const form = this.closest('form');
                if (form) {
                    // Add loading state
                    this.disabled = true;
                    
                    // Submit form
                    setTimeout(() => {
                        form.submit();
                    }, 300);
                }
            });
        });
    };

    // ============================================================================
    // DELETE CONFIRMATIONS
    // ============================================================================

    /**
     * Add confirmation dialogs for delete actions
     */
    const initDeleteConfirmations = () => {
        const deleteButtons = document.querySelectorAll('.btn-danger, form[action*="delete"] button');
        
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                    e.preventDefault();
                    return false;
                }
            });
        });
    };

    // ============================================================================
    // SMOOTH SCROLL FOR ANCHOR LINKS
    // ============================================================================

    /**
     * Add smooth scrolling to anchor links
     */
    const initSmoothScroll = () => {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href !== '#' && href !== '') {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        smoothScroll(target);
                    }
                }
            });
        });
    };

    // ============================================================================
    // MOBILE MENU CLOSE ON CLICK OUTSIDE
    // ============================================================================

    /**
     * Close mobile menu when clicking outside
     */
    const initMobileMenuClose = () => {
        document.addEventListener('click', (e) => {
            const sideNav = document.getElementById('side-nav');
            const menuIcon = document.getElementById('openNavBtn');
            
            if (sideNav && menuIcon && sideNav.classList.contains('open')) {
                if (!sideNav.contains(e.target) && !menuIcon.contains(e.target)) {
                    sideNav.style.width = '0';
                    sideNav.classList.remove('open');
                    document.body.style.overflow = '';
                }
            }
        });
    };

    // ============================================================================
    // INITIALIZATION
    // ============================================================================

    /**
     * Initialize all features when DOM is ready
     */
    ready(() => {
        initSidenav();
        initFlashMessages();
        enhanceForms();
        initCardAnimations();
        initButtonRipples();
        enhanceReminders();
        initDeleteConfirmations();
        initSmoothScroll();
        initMobileMenuClose();

        // Log initialization
        console.log('Abhidha Construction Management System initialized');
    });

    // ============================================================================
    // EXPORT FOR EXTERNAL USE (if needed)
    // ============================================================================

    window.AbhidhaApp = {
        ready,
        smoothScroll,
        initSidenav,
        initFlashMessages
    };

})();
