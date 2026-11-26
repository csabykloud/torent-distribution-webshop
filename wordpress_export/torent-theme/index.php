<?php
/**
 * Main Template File
 */
get_header(); ?>

<main id="primary" class="site-main container" style="padding: 40px 20px;">
    <?php
    if (have_posts()) :
        while (have_posts()) :
            the_post();
            the_content();
        endwhile;
    else :
        echo '<p>Nu au fost găsite produse sau articole.</p>';
    endif;
    ?>
</main>

<?php
get_footer();
