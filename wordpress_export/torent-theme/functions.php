<?php
/**
 * Torent Horticulture Theme Functions & WooCommerce Setup
 */

if (!defined('ABSPATH')) {
    exit;
}

function torent_theme_setup() {
    // Add theme support for WooCommerce
    add_theme_support('woocommerce');
    add_theme_support('wc-product-gallery-zoom');
    add_theme_support('wc-product-gallery-lightbox');
    add_theme_support('wc-product-gallery-slider');
    
    // Title tag and thumbnails
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    
    // Menus
    register_nav_menus(array(
        'primary' => __('Meniu Principal', 'torent-horticulture'),
        'footer'  => __('Meniu Footer', 'torent-horticulture'),
    ));
}
add_action('after_setup_theme', 'torent_theme_setup');

// Enqueue styles
function torent_theme_scripts() {
    wp_enqueue_style('torent-style', get_stylesheet_uri(), array(), '1.0.0');
}
add_action('wp_enqueue_scripts', 'torent_theme_scripts');
