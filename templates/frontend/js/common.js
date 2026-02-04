(function($){
  
  //
  // OPENING OF THE SEARCH AND NAV
  //
  
    var nav = $(".header-nav");
    var search = $(".header-search");
  
    $(".header-search-type").on("focus",function(){
      $(this).parents(".header-search").addClass("active");
    });
    $(".header-search-type").on("blur",function(){
      $(this).parents(".header-search").removeClass("active");
    });
    
    if($(".header-search").find("input.header-search-type").val()!="") 
      $(".header-search").addClass("type");
    $(".header-search-type").on("keyup",function(){
      var q = $(this).val();
      if(q != "") {
        $(this).parents(".header-search").addClass("type");
        // сюда можно вставить ajax вызов запроса к поиску
      } else {
        $(this).parents(".header-search").removeClass("type");
      }
    });
    
    $(".header-search-reset").click(function(){
      $(".header-search").find("input.header-search-type").val("");
    });
    
    $(".header-search-link").click(function(){
      if(search.hasClass("opened")) {
        search.removeClass("opened");
      } else {
        search.addClass("opened");
        nav.removeClass("opened");
      }
    });
  
    $(".header-nav-link").click(function(){
      if(nav.hasClass("opened")) {
        nav.removeClass("opened");
      } else {
        nav.addClass("opened");
        search.removeClass("opened");
      }
    });
 

  //
  // OPENING OF THE MODAL CARD
  //
  if($(".modal-card").length) {
    $(".modal-card-link").click(function(){
      var cardBlock = $(this).parent();
      if(cardBlock.hasClass("opened")) {
        cardBlock.removeClass("opened");
      } else {
        cardBlock.addClass("opened");
        var $scrollList = cardBlock.find(".modal-card-carousel-wrapper");
        var mySwiperModal = new Swiper ($scrollList, {
          freeMode: true,
          slideClass: 'carousel-list-item',
          wrapperClass: 'carousel-list',
          slidesPerView: 'auto',
          prevButton: $scrollList.find(".carousel-controls-prev"),
          nextButton: $scrollList.find(".carousel-controls-next")
        });
        
        $(".modal-card-carousel-filter a").click(function(){
          $(this).siblings().removeClass("selected");
          $(this).addClass("selected");
          var cat = $(this).attr("data-filter");
          if(cat!="*") {
            $(".modal-card-carousel-list").find(".carousel-list-item:not([data-cat='"+cat+"'])").hide();
            $(".modal-card-carousel-list").find(".carousel-list-item[data-cat='"+cat+"']").show();
          } else {
            $(".modal-card-carousel-list").find(".carousel-list-item").show();
          }
          mySwiperModal.update(true);
          return false;
        });
      }
      return false;
    });
  }

  
  $('#myDonates').on('shown.bs.modal', function (e) {
    var payments = $(".modal-payments-carousel");
    //payments.append("<div class='swiper-scrollbar'></div>");
    //var scrollBar = payments.find(".swiper-scrollbar");
    
    var mySwiperModal = new Swiper (payments, {
      freeMode: true,
      slideClass: 'modal-payments-item',
      wrapperClass: 'modal-payments-carousel-wrapper',
      slidesPerView: 'auto',
      prevButton: payments.find(".carousel-controls-prev"),
      nextButton: payments.find(".carousel-controls-next")
    });
  })
  
  
  $(".modal-payments-item").click(function(){
    $(this).siblings().removeClass("active");
    $(this).addClass("active");
    return false;
  });
  
  //
  // MODAL REGISTRATION FORM 
  //
  if($(".modal-auth-regLink").length) {
    $(".modal-auth-regLink a ").click(function(){
      $(".modal-auth").removeClass("active");
      $(".modal-registration").addClass("active");
      return false;
    })
  }
  if($(".modal-registration-authLink").length) {
    $(".modal-registration-authLink a ").click(function(){
      $(".modal-registration").removeClass("active");
      $(".modal-auth").addClass("active");
      return false;
    })
  }
  
  //
  // FLOATING HEADER
  //
  floatHeeder();
  $(document).scroll(function () {
    floatHeeder();
  });
  function floatHeeder() {
    if($(this).scrollTop() > 0) $("body").addClass("scrolled");
    else  $("body").removeClass("scrolled");
  }
  
  //
  // OPENING OF THE SUBNAV
  //
  if($(".content-subNav").length) {
    $(".content-subNav").on("click",".active",function(){
      $(this).parents(".content-subNav").toggleClass("opened");
      return false;
    });
  }
  
  //
  // OPENING OF THE FILTER
  //
  if($(".filter-link").length) {
    $(".filter-link").click(function(){
      $(".filter").toggleClass("opened");
    });
  }

  
  //
  // DROPDOWN TOGGLE
  //
  if($(".dropdown-toggle").length) {
    $(".dropdown-toggle").click(function(){
      $(this).parent(".dropdown").toggleClass("open");
      if(!$(this).parent(".dropdown").hasClass("open")) {
        $("body").removeClass("regOpen");
      }
      return false;
    })
  }
  
  //
  // REGISTRATION OPEN
  //
  if($(".header-registration-link").length) {
    $(".header-registration-link").click(function(){
      $("body").toggleClass("regOpen");
      return false;
    })
  }
  
  //
  // DATEPICKER CALL
  //
  if($(".datepicker").length) {
    $(".datepicker").each(function(){
      var dateField = $(this).children("input");
      var dateFieldWidget = dateField.datepicker({
        showOn: 'both'
      });
      if(dateField.hasClass("fromDate")) {
        dateField.datepicker( "option", "altField", ".fromDate" );
        dateField.datepicker( "option", "altFormat", "с dd MM yy" );
      };
      if(dateField.hasClass("toDate")) {
        dateField.datepicker( "option", "altField", ".toDate" );
        dateField.datepicker( "option", "altFormat", "до dd MM yy" );
      };
    })
  }

  //
  // EQUALIZE CALL
  //
  if($('[data-equal-height]').length) {
    
    $(document).ready(function() {
      loadEqualize();
    });
    
    $('[data-equal-height] img').load(function(){
      loadEqualize();
    });
    
	  $(window).resize(function() {
      $('[data-equal-height]').each(function(){
        $(this).find($('[data-equal-height]').attr("data-equal-height")).css("min-height","0");
      })
      loadEqualize();
	  });
    
  }

  function loadEqualize() {
    if(parseInt(window.innerWidth) >= 768) {
      $('[data-equal-height]').make_children_equal_height('data-equal-height')
    } else {
      $('[data-equal-height][data-equal-allowmobile="true"]').make_children_equal_height('data-equal-height');
    }
  }
  
  //
  // Elastic Textarea
  //
  if($('textarea[data-elastic=true]').length) {
    autosize($('textarea[data-elastic=true]'));  
  }
  
  
  //
  // Popover
  //
  $('[data-popover="open"]').each(function(){
    var source = $(this).attr("data-source");
    $(this).popover({
      trigger: 'focus',
      html: true,
      content: $(source)
    })
  })
  
  //
  // Tooltip
  //
  $('[data-toggle="tooltip"]').tooltip()
  
  
  //
  // NKO Gallery
  //
  if($('.nko-gallery-controls').length) {
    $('.nko-gallery-controls-prev').click(function(){
      var gallery = $(".nko-gallery-wrapper");
      var active = gallery.find(".nko-gallery-item.active");
      if(active.prev().length) {
        active.removeClass("active").prev().addClass("active");
      } else {
        active.removeClass("active");
        gallery.children(":last").addClass("active");
      }
      setActiveVisible(gallery);
    });
    $('.nko-gallery-controls-next').click(function(){
      var gallery = $(".nko-gallery-wrapper");
      var active = gallery.find(".nko-gallery-item.active");
      if(active.next().length) {
        active.removeClass("active").next().addClass("active");
      } else {
        active.removeClass("active");
        gallery.children(":first").addClass("active");
      }
      setActiveVisible(gallery);
    });
    $(".nko-gallery-item-thmb").click(function(){
      var gallery = $(".nko-gallery-wrapper");
      $(this).parent().siblings().removeClass("active");
      $(this).parent().addClass("active");
      setActiveVisible(gallery);
    })
    
    function setActiveVisible(gallery) {
      var galleryWidth = gallery.width();
      var itemWidth = gallery.children().width();
      var itemQuant = gallery.children().length;
      var activeItem = gallery.children(".active");
      if(itemWidth*itemQuant <= galleryWidth) return;
        
      var positionOrig = activeItem.index()*itemWidth / 2;
      if(positionOrig > - galleryWidth + itemWidth*itemQuant) {
        position = galleryWidth - itemWidth*itemQuant;
      } else {
        position = -positionOrig;
      }
      gallery.children(":first").css("margin-left", (position)+"px");
    }
    
    var nkoGallery = $(".nko-gallery");
    var nkoGallerySwipe = "";
    $(document).ready(function(){
      if(!nkoGallery.hasClass("swiper-container-horizontal")) {
        nkoGallerySwipe = makeSwipeNKO(nkoGallery);
      }
    });
    
    function makeSwipeNKO(nkoGallery) {
      var mySwiper = new Swiper (nkoGallery, {
        freeMode: true,
        slideClass: 'nko-gallery-item',
        wrapperClass: 'nko-gallery-wrapper',
        slidesPerView: 'auto'
      });
    }
    
  }
  
  
  //
  // Gallery slider
  //
  
  $(document).ready(function () {
    $(".carousel").each(function(){
      var $scrollList = $(this).find(".carousel-wrapper");
      var mySwiper = new Swiper ($scrollList, {
        freeMode: true,
        slideClass: 'carousel-list-item',
        wrapperClass: 'carousel-list',
        slidesPerView: 'auto',
        prevButton: $scrollList.find(".carousel-controls-prev"),
        nextButton: $scrollList.find(".carousel-controls-next")
      });
    });
  });
  
  
  //
  // NKO Payment
  //
  // containers .campaign or .nko may contains this form
  //
  if($('.nko-finance-pay,.campaign-finance-pay').length) {
    $(document).ready(function () {
      $("[data-switch='period'] .btn").click(function(){
        
        
        $(this).siblings().removeClass("active");
        $(this).addClass("active");
        
        var target=$(".nko-finance-pay-list-wrapper[data-period='"+$(this).attr("data-target")+"'],.campaign-finance-pay-list-wrapper[data-period='"+$(this).attr("data-target")+"']");
        target.siblings().removeClass("active");
        target.addClass("active");
        
        //var prevValue = target.siblings().find(".active").attr("data-sum");
        //alert(prevValue);
        //var current_value = $("#paySum").val();
        //$("#paySum").val($("#paySum").attr("data-prev"));
        //$("#paySum").attr("data-prev",current_value);

        return false;
      });
      
      $(".nko-finance-pay-list-item,.campaign-finance-pay-list-item").click(function(){
        var thisClass = $(this).attr("class");
        //$(this).parents(".nko-finance-pay-list,.campaign-finance-pay-list").find(".nko-finance-pay-list-item,.campaign-finance-pay-list-item").removeClass("active");
        $(this).siblings().removeClass("active");
        $(this).addClass("active");
        var payForm = $(".nko-finance-pay-form form,.campaign-finance-pay-form form");
        var payRepeat = $(this).parent().attr("data-period");
        var paySum = $(this).attr("data-sum");
        payForm.find("#paySum").val(paySum);
        payForm.find("#payRepeat").val(payRepeat);
        return false;
      });
      
    });
  }
  
  //
  // NKO List Gallery
  //
  $(".nkolist-item-gallery").each(function(){
    var gallery = $(this);
    gallery.find(".nkolist-item-gallery-img:not(.active)").each(function(i){
        $(this).css("left",i*33.33+"%");
        $(this).attr("data-left",i*33.33);
    });
    gallery.find(".nkolist-item-gallery-img").click(function(){
      if($(this).hasClass("active")) {
        $.fancybox([
          {
            href: $(this).attr("data-src")
          }
        ],{
          type: 'image'
        });
      } else {
        swapItemsNKOGallery(gallery,$(this));
      }
    });
  });
  
  function swapItemsNKOGallery(gallery,active) {
    var oldActive = gallery.find(".active");
    var oldActiveNewX = active.attr("data-left");
    
    oldActive.css("left",oldActiveNewX+"%");
    oldActive.attr("data-left",oldActiveNewX);
    oldActive.removeClass("active");
    
    active.css("left",0);
    active.addClass("active");
  }
  
  
  //
  // AUTOCOMPLETE FOR SEARCH REGION FIELD
  //
  
  $(document).ready(function(){
    if($(".autocomplete").length) {
      $(".autocomplete").each(function(){
        var field = $(this);
        var container = field.next(".form-control-autocomplete");
        field.on("keyup",function(){
          if(field.val()) {
            // ajax запрос
            container.show();
          } else {
            container.hide();
          }
        });
        field.on("blur",function(){
          setTimeout(function(){
            container.fadeOut(500);
          },500);
        });
        container.on("click",".form-control-autocomplete-item a",function(){
          var value = $(this).attr("data-value");
          field.val(value);
          container.fadeOut(500);
          return false;
        })
      })
    }
  })
  
  
  //
  // OPEN FILE DIALOG
  //
  $(document).ready(function(){
    if($(".profile-form-files-item-add").length) {
      $(".profile-form-files-item-add").each(function(){
        var fileOpenLink = $(this);
        fileOpenLink.on("click",function(){
          $(this).parents(".profile-form-files").find("input[type=file]").click();
          return false;
        })
      });
    }
  });
  
})(jQuery)