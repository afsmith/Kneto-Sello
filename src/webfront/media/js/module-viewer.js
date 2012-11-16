var app = new Ing();
var playingIndex = 0;
var playingId = null;
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();
    if(moduleID){
      app.module.get(moduleID, 'json', true);
    }
    app.module.addViewerEvents();

    if(this.location.hash){
        if ( this.location.hash.indexOf("#/") > -1 ) {
            playingId = this.location.hash.replace(/#\//, '');
            if(moduleID){
                var url = '/content/modules/' + moduleID + '/?format=json';
                $.get(url, function(data) {
                    $.each(data.track0, function(i, v) {
                        if ( playingId == v.segment_id ) {
                            playingIndex = v.start;
                        }
                    });
                    playM();
                });
            }
        }
        else {
            playingIndex = this.location.hash.replace(/#/, '');
            playM();
        }
    }
    else {
       playM();
    }

    $('#courseObjective').click(function(){
        var elements = $("#moduleList").find('li').length;
        if ( app.data.activeItem < elements ) {
            document.getElementById('video').pause();
        }
        app.module.displayObjective(app.data.moduleJSON, true);
        return false;
    });

    $('.nyroModalClose').live('click', function() {
        document.getElementById('video').resume();
        app.triggerEvent('modalClosed');
    });
    $(app).bind('modalClosed', function(){
        //app.module.startPlayback(moduleID);
    });



		$('.shelf').each(function() {
				var container = $(this).parent();
				$(container).siblings(".prev, .next").addClass('disabled');
		});
		shelfEach();

});

function shelfEach() {
		if ( $('.shelf').width() == 0 ) {
				setTimeout ( "shelfEach()", 200 );
		}
		else {
				$('.shelf').each(function() {
						var elements = $(this).find('li').length;
						var container = $(this).parent();
						if (elements < 6) {
							$(container).siblings(".prev, .next").addClass('disabled');
						} else {
							$(container).siblings(".prev, .next").removeClass('disabled');
						}
				});
		}
}

function playM() {
    if(app.helpers.cookie.get('ing_obj_' + moduleID) != ''){
        playMovie('/content/modules/' + moduleID + '/?format=xml', 'playlist', false, playingIndex);
        res = setTimeout("$(window).resize()", 100);
    }
}
