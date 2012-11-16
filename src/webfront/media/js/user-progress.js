var app = new Ing();
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();
    app.helpers.throbber('.rollerWrapper');
    $.get(
        '/content/modules/' + moduleID + '/?format=json',
        function(data){
            if(typeof data != 'object'){ // IE bug --
                data = $.parseJSON(data);
            }
            app.data.module = data;
            app.data.segments = {};
            app.data.activeSegment = false;
            for(var i = 0, len = data.track0.length; i < len; i++){
                app.data.segments[data.track0[i].segment_id] = data.track0[i];
                if(data.track0[i].start == 0){
                    app.data.activeSegment = data.track0[i];
                }
            }
            app.helpers.throbber('.rollerWrapper', 'remove');

            //if ($('results_tracking_'+app.data.activeSegment.segment_id).children().length > 0)
            //	$('#scormResults').show();

    });
	$('#userLog .result:first, .segmentDetails:first').show();
	$('.rollerItems li:first').addClass('active');
	$('.segmentDetails .singleFile').click(function(){return false;});
	$('.rollerItems .singleFile').click(function(){
	    app.data.activeSegment = app.data.segments[$(this).attr('id').replace('segment_', '')];
		var id = $(this).attr('id');
		$('.rollerItems li').removeClass('active');
		$(this).parent().addClass('active');
		$('#userLog .result, .segmentDetails').hide();
		$('#details_'+id + ', #progress_'+id).show();
		$('#scormResults .result, .segmentDetails').hide();
		$('#details_'+id + ', #results_'+id.replace('segment_','tracking_')).show();
        //console.log('id = '+id);
		if ($('#results_tracking_'+id).children().length == 0)
			$('#scormResults').hide();
		else
			$('#scormResults').show();
		return false;
	});

		if ( $('.progress_tracking') ) {
				$('.progress_tracking').each(function(index) {
						app.data.activeTracking = $(this).attr('id');
						var results_tracking_id = '#'+app.data.activeTracking.replace('progress_', 'results_');
						if($(results_tracking_id).children().length > 0) {
								$(this).css('cursor','pointer');
						}
				});
		}

    $('.progress_tracking').click(function(){
        $('#scormResults').hide();
        $('#scormResults ul').hide();
        app.data.activeTracking = $(this).attr('id');
        //console.log('progress_tracking_id = '+app.data.activeTracking);
        var results_tracking_id = '#'+app.data.activeTracking.replace('progress_', 'results_');
        //console.log('results_tracking_id = '+results_tracking_id)
        if($(results_tracking_id).children().length > 0) {
            $(results_tracking_id).show();
            $('#scormResults').show();
        }
    });
	$('#mainScroller.rollerItems .courseApla').click(function() { $(this).prev().click(); });
	$('.rollerItems ul').css('width', function(){
  		return $(this).children('li').length * ($(this).children('li:first').width() + 24);
  	});
  	app.config.shelfWrapperWidth = 736;
  	var t = app.config.other.timer;
  	$('.next, .prev').mousedown(function(){
  		var dir = $(this).hasClass('next') ? 'right' : 'left';
  		var id = '#' + $(this).siblings('.roller').children('div').attr('id');
  		t = setInterval(function(){
	  			app.helpers.move(dir, app.config.other.movingStep, id);
  			}, app.config.other.movingInterval);
  	}).mouseup(function(){
  		if(t){
  			clearTimeout(t);
  		}
  	});
  	$('.preview').live('click', function(event){
        event.preventDefault();
        var parent = Ing.findInDOM();
        var cnf = parent.config;
        var obj = app.data.activeSegment;
        var href = $(this).attr('href');
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
        $('.playerClose').live('click', function() {
            $('.flashWrapper .closeFW').trigger('click');
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
                'contentURL': encodeURIComponent(obj.url),
                'cType': parent.data.filetypes[obj.type],
                'duration': encodeURIComponent(obj.duration),
                'pagesNum': encodeURIComponent(obj.pages_num),
                'siteLanguage': siteLanguage
            },{
                'allowFullscreen': 'true',
                'allowScriptAccess': 'always',
                'wmode': 'opaque'
            },{}
         );
         return false;
      });
      $('.prev a').hide();
      $(app).bind('shelfStart', function(event, data){
         $('.prev a').hide();
         $('.next a').show();
      });
      $(app).bind('shelfStop', function(event, data){
         $('.next a').hide();
         $('.prev a').show();
      });
      $(app).bind('shelfMoving', function(event, data){
         $('.next a, .prev a').show();
      });

      $('.rollerItems').each(function() {
				var width = $(this).width();
				var container = $(this).parent();
				var container_width = $(container).width();
				if (width < container_width) {
					$(container).siblings(".prev, .next").addClass('disabled');
				} else {
					$(container).siblings(".prev, .next").removeClass('disabled');
				}
		  });
});
