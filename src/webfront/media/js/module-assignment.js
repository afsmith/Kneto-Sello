var app = new Ing();
var searchTimer = false;
var tim = [];
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();
    app.ma.loadGroups();
    app.ma.loadActiveModules(this.location.hash.replace(/#/, ''));
    app.data.assignments = {};
    app.config.shelfWrapperWidth = 566;
    app.data.changed = false;
    app.data.search_changed = false;
    $('#as_save').click(function(){
     app.helpers.throbber('#group_list');
     var asg = {};
     $.each(app.data.assignments, function(key, value){
       //if(objSize(value) > 0){
        asg[key] = [];
       //}
       $.each(value, function(subkey, subvalue){
         asg[key].push(subkey);
       });
     });
     $.post(
       '/assignments/group/modules/',
       JSON.stringify({"assignments": asg,
                       "add_one_click_link": $("#id_ocl").attr("checked")}),
       function(data){
         if(typeof data != 'object'){ // IE bug --
           data = $.parseJSON(data);
         }
         if(data.status == 'OK'){
            app.helpers.window(t.SYSTEM_MESSAGE, t.ASSIGNMENTS_SAVED, null, null, function() {
                        window.location = "/content/modules/assign/";
                    });
         }else{
           //err
         }
         app.helpers.throbber('#group_list', 'remove');
       }
     )
   });
   $('a.close').click(function(){
       if(app.data.changed==true) {
           app.helpers.window(t.SYSTEM_MESSAGE, t.LEAVE_WITHOUT_SAVE, [{
              'text': t.YES,
               events: [{
                   name: 'click',
                   handler: function() {
                       $.nmTop().close();
                       window.location = $('a.close').attr('href');
                       return true;
                   }
               }]
           },{
               'text': t.NO,
               events: [{
                   name: 'click',
                   handler: function(){
                       $.nmTop().close();
                       return false;
                   }
               }]
           }],
           false);
       } else {
           window.location = $('a.close').attr('href');
       }
       return false;
   });
   $('#addGroup').click(function(){
     app.helpers.throbber($('#groupsWrapper'));
     if($('#groups').val() != -1){
     	var className = 'even';
       if($('#groups option:selected').attr('disabled') !== true){
       	if($('#group_list li:last')){
       		className = $('#group_list li:last').hasClass('even') ? 'odd' : 'even';
       	}
        app.ma.createGroup($('#groups').val(), className);
       }
     }else{
       $('#groups option:enabled').each(function(i){
         if($(this).attr('value') != -1){
            app.ma.createGroup($(this).attr('value'), i%2 ? 'odd' : 'even');
         }
       });
     }
     $('.dotsWrapper').each(function() {
     	if($(this).find('.dot').length < 8) {
     		$(this).siblings('.browse').find('img').hide();
     	} else {
     		$(this).siblings('.browse').find('img').show();
     	}
     });
     app.helpers.throbber($('#groupsWrapper'), 'remove');
   });
   $('.dots .movableDot').live('click', function(){
    $('.dots .movableDot').removeClass('active');
    $(this).addClass('active');
    $('.myModules li').removeClass('active');
    $('.allModules li').removeClass('active');
   	$('#moduleDetailsWrapper').html('');
     $('#moduleDetailsWrapper').append(
       app.elements.getObj(
         new app.elements.courseDetails(
           app.data.map[$(this).attr('id')]
         )
       )
     );
     $('#moduleDetailsWrapper .movableDot').draggable({
        appendTo: 'body',
        helper: 'clone'
      });
   });
   $('.myModules li, .allModules li').live('click', function(){
    $('.dots .movableDot').removeClass('active');
   	// $('#myModules li').removeClass('active');
   	$('.myModules li').removeClass('active');
   	$('.allModules li').removeClass('active');
   	$(this).addClass('active');
     $('#moduleDetailsWrapper').html('');
     $('#moduleDetailsWrapper').append(
       app.elements.getObj(
         new app.elements.courseDetails(
           app.data.map[$(this).attr('id')]
         )
       )
     );
     $('#moduleDetailsWrapper .movableDot').draggable({
        appendTo: 'body',
        helper: 'clone'
      });
   });
   $('#modulesWrapper li.first').next().css('left', $('#modulesWrapper li.first').width()-14);
   $('.tabs a').click(function(){
		/*$('ul.result').hide();
		$('#modulesWrapper li').removeClass('active');
		$(this).parent().addClass('active');
		$($(this).attr('href')).fadeIn('200');*/
		return false;
  	});
	$('.preview').live('click', function(){
		var id = $(this).parent().children().first().attr('id');
		var bg = $('<div class="modalBg"></div>');
        var flash = $('<div class="flashWrapper"><a href="javascript:void(0);" class="closeFW"></a><div id="flash"></div></div>');
        bg.css({
            height: $(window).height(),
            width: $(window).width()
        });
        flash.css({
            left: $(window).width() / 2 - 350,
            top: 10
        });
        bg.appendTo($('body'));
        flash.appendTo($('body'));
        bg.click(function(){
            flash.remove();
            $(this).unbind('click').remove();
        });
				$('.flashWrapper .closeFW').click(function(){
						flash.remove();
						bg.unbind('click').remove();
				});
        swfobject.embedSWF(
            app.config.mediaURL + app.config.player.url,
            "flash",
            "700",
            "500",
            "9.0.0",
            false,
            {
                'relativeURL': app.config.mediaURL,
                'contentURL': '/content/modules/' + app.data.map[id].id + '/?format=xml',
                'cType': 'playlist',
                'siteLanguage': siteLanguage
            },{
                'allowFullscreen': 'true',
                'allowScriptAccess': 'always',
                'wmode': 'opaque'
            },{}
         );
	});

	// custom selectboxes
	$(".selectBoxJs").sb();
	$("#id_language").sb();
    $("#id_owner").sb();

	// search

    $('#search').keyup(function(){
        app.data.search_changed = true;
        showModules();
    });

    $('#id_language,#id_groups').change(function() {
        showModules();
    });

    var shouldBeHidden = function(listItem) {
				checkSearch();
        var groups = $.parseJSON(listItem.parent().find('input').val());
        var selected_group_id = $('#id_groups :selected').val().toLowerCase().trim();

        if (document.location.hash == "#myModules") {
            var ownerid = listItem.parent().find('input.ownerid').val();
            if ($('#id_owner').val() && $('#id_owner').val() != ownerid) {
                return true;
            }
        } else {
            if ($('#id_owner').val() && (!haveAtLeastOneCommonGroupId(groups, app.data.user_groups) || $('#id_owner').val() == ownerid)) {
                return true;
            }
        }

        if(app.data.search_changed &&
                listItem.html().toLowerCase().indexOf($('#search').val().toLowerCase().trim()) == -1 &&
            	( listItem.siblings(".moduleAuthor").html().toLowerCase().indexOf($('#search').val().toLowerCase().trim()) == -1 )) {
            return true;
        }

        if ($('#id_language').val() != "0" && $('#id_language').val() != listItem.attr('lang')) {
            return true;
        }

        if ($('#id_groups').val() != "0" && groups.indexOf(parseInt(selected_group_id)) == -1) {
            return true;
        }

        return false;
    }

    var showModules = function() {
        $('.moduleName').each(function() {
            $(this).parents('li').show();
        });

        $('.moduleName').each(function() {
            if (shouldBeHidden($(this))){
                $(this).parent('li').hide();
            } else {
                $(this).parents('li').show();
            }
        });
    }

    var showOwnersGroups = function(owners_groups) {
        $("#id_groups").html($("#id_groups_all").html());

        $("#id_groups").find("option").each(function(index, option) {
            var optionValue = parseInt($(option).attr("value"));
            if ($(option).attr("value") != 0 && !($(option).attr("value") in owners_groups)) {
                $(option).remove();
            }
        });

        $("#id_groups").sb('refresh');
    }

    $('#id_owner').change(function() {
        if (!$('#id_owner').val()) {
            $("#id_groups").html($("#id_groups_all").html());
            $("#id_groups").sb('refresh');
            return;
        }

        if (document.location.hash == "#myModules") {
            $('.moduleAuthor').each(function() {
                if ($('#id_owner').val() != $(this).attr('ownerid')) {
                    $(this).parent('li').hide();
                } else {
                    $(this).parents('li').show();
                }
            });

            $.get('/management/users/' + $('#id_owner').val() + "/groups/", function(data) {
                if (typeof data != 'object') { // IE bug --
                    data = $.parseJSON(data);
                    app.data.user_groups = data;
                }

                showOwnersGroups(data);
            });
        } else {
            $.get('/management/users/' + $('#id_owner').val() + "/groups/", function(data) {
                if (typeof data != 'object') { // IE bug --
                    data = $.parseJSON(data);
                    app.data.user_groups = data;
                }

                $('.moduleAuthor').each(function() {
                    var groups = $.parseJSON($(this).parent().find('input').val());
                    var ownerid = $(this).parent().find('input.ownerid').val();
                    if ($('#id_owner').val() && (!haveAtLeastOneCommonGroupId(groups, data) || $('#id_owner').val() == ownerid)) {
                        $(this).parent('li').hide();
                    } else {
                        $(this).parent('li').show();
                    }
                });

                showOwnersGroups(data);
            });
        }
    });

    var haveAtLeastOneCommonGroupId = function(groupArray, groupDict) {
        for(var i = 0; i < groupArray.length; i++) {
            for(var key in groupDict) {
                if(groupArray[i] == parseInt(key)) {
                    return true;
                }
            }
        }

        return false;
    }

    var flip = function(from, to) {
        var tmp = $(from).html();
        $(from).html($(to).html());
        $(to).html(tmp);
        $(from).sb('refresh');
        $(from).change();
    };

    $('#showMy').live('change', function() {
        flip('#groups', '#my_groups');
    });
    $('#showMy').attr('checked', true);
    // Set active tab

    $("a[href='"+document.location.hash+"']").parent().addClass("active");

    $("a[href='#allModules']").click(function(){
    	$(this).parent().addClass("active");
    	$(this).parent().siblings("li").removeClass("active");
    	window.location.hash = "allModules";
    	$("ul.myModules").addClass("hidden");
    	$("ul.allModules").removeClass("hidden");
    	$("ul.allModules").html(" ");
    	$('#moduleDetailsWrapper').html('');
    	app.ma.loadActiveModules(document.location.hash.replace(/#/, ''));

    	return false;
    })
    $("a[href='#myModules']").click(function(){
    	$(this).parent().addClass("active");
    	$(this).parent().siblings("li").removeClass("active");

    	$("ul.allModules").addClass("hidden");
    	$("ul.myModules").removeClass("hidden");
    	$("ul.myModules").html(" ");
    	window.location.hash = "myModules";
    	$('#moduleDetailsWrapper').html('');
    	app.ma.loadActiveModules(document.location.hash.replace(/#/, ''));
    	return false;
    })

    // -- overlays
    $('.dotsWrapper .movableDot').live('mouseover', function(){
      clearTimeout(tim[$(this).attr('id')]);
      if($(this).find('.close_overlay').length == 0){
          var overlay = $('<a class="close_overlay" title="' + t.ITEM_REMOVE + '"></a>');
          overlay.css({
            'left': $(this).position().left + $(this).outerWidth() - 8,
            'top': $(this).position().top
          });
          $(this).find('span').addClass('hover');
          overlay.appendTo($(this));
      }
    }).live('mouseout', function(){
        var that = this;
        tim[$(this).attr('id')] = setTimeout(function(){
            $(that).find('span').removeClass('hover');
            $('.close_overlay').remove();
        }, 50);
    });
    $('.close_overlay, .movableDot span').live('mouseover', function(){
        clearTimeout(tim[$(this).parent().attr('id')]);
    });
    $('.close_overlay').live('mouseout', function(){
        var that = this;
        tim[$(this).parent().attr('id')] = setTimeout(function(){
            $(that).siblings('span').removeClass('hover');
            $('.close_overlay').remove();
        }, 50);
    }).live('click', function(){
      var grp = app.data.map[$(this).parents('li').attr('id')].id;
      var mod = app.data.map[$(this).parents('.movableDot').attr('id')].id;
      delete(app.data.assignments[grp][mod]);
      $(this).parents('.movableDot').remove();
      app.data.changed = true;
   	  $('.dotsWrapper').each(function() {
     	if($(this).find('.dot').length < 8) {
     		$(this).siblings('.browse').find('img').hide();
     	} else {
     		$(this).siblings('.browse').find('img').show();
     	}
     })
      return false;
    });

    searchDefault = $('#search').val();
    $('#search').focus(function() {
    	if(searchDefault == $('#search').val()) {
    		$('#search').val('');
    	}
    });
    $('#search').blur(function() {
    	if($('#search').val() == '') {
    		$('#search').val(searchDefault);
    	}
    });
});

var searchDefault;
function checkSearch(){
    clearTimeout(searchTimer);
    searchTimer = setTimeout("if ( $('#search').val() == searchDefault ) { $('#search').val(''); }", 300);
}
