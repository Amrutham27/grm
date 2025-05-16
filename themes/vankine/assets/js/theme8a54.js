(function ($) {
    ("use strict");
    // Page loading
   

    /*---====================---header drop down button---======================---*/
    if($('.navbar_nav li.dropdown ul').length){
        $('.navbar_nav li.dropdown').append('<div class="dropdown-btn"><span class="fa fa-angle-down"></span></div>');
    }
    if($('.navbar_nav li.mega_menu  ul').length){
        $('.navbar_nav li.mega_menu').append('<div class="dropdown-btn"><span class="fa fa-angle-down"></span></div>');
    }
   
 
  /*---====================---mobile navbar append---======================---*/
    if($('.mobile_menu_box').length){
        //Menu Toggle Btn
        $('.navbar_togglers').on('click', function() {
            $('body').toggleClass('mobile_menu_box-visible');
        });
        //Menu Toggle Btn
        $('.mobile_menu_box .menu-backdrop,.mobile_menu_box .close-btn').on('click', function() {
            $('body').removeClass('mobile_menu_box-visible');
        });
    }
    /*---====================---header drop down toggle---======================---*/
    //Mobile Nav Hide Show
	if($('.mobile_menu_box').length){
		var mobileMenuContent = $('.navbar_nav').html();
		$('.mobile_menu_box .getmobilemenu').append(mobileMenuContent); 
	}

    var $offCanvasNav = $(".mobile_menu_box"),
    $offCanvasNavSubMenu = $offCanvasNav.find(".sub-menu");
    /*Add Toggle Button With Off Canvas Sub Menu*/
    $offCanvasNavSubMenu.parent().prepend('<span class="dropdown-btn"><i class="fi-rs-angle-small-down"></i></span>');
    /*Close Off Canvas Sub Menu*/
    $offCanvasNavSubMenu.slideUp();
    /*Category Sub Menu Toggle*/
    $offCanvasNav.on("click", "li a, li .dropdown-btn", function (e) {
        var $this = $(this);
        if (
            $this
                .parent()
                .attr("class")
                .match(/\b(menu-item-has-children|has-children|has-sub-menu|sub-menu|mega_menu)\b/) &&
            ($this.attr("href") === "#" || $this.hasClass("dropdown-btn"))
        ) {
            e.preventDefault();
            if ($this.siblings("ul:visible").length) {
                $this.parent("li").removeClass("active");
                $this.siblings("ul").slideUp();
            } else {
                $this.parent("li").addClass("active");
                $this.closest("li").siblings("li").removeClass("active").find("li").removeClass("active");
                $this.closest("li").siblings("li").find("ul:visible").slideUp();
                $this.siblings("ul").slideDown();
            }
        }
    });

    $(document.body).trigger('wc_fragment_refresh');


    function onepagemobile_nav() {
        $(document).ready(function() { 
            $('.onepage_header_enable .navigation_menu').on('click', 'li a', function() {
                $('body').removeClass('mobile_menu_box-visible');
            });
        });
    }

	jQuery(document).on('ready', function () {
		(function ($) {
			// add your functions
            onepagemobile_nav();
		})(jQuery);
	});


})(jQuery);

