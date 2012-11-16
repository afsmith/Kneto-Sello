var app = new Ing();
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();
    $.ajaxSetup({
		error : function(x) {
			$("body").html(x.responseText);
		}
	});
    $(app).bind('msgformOpened', function(){
        $('.wrote textarea').attr('disabled', 'disabled');
        $('.textarea textarea:enabled').html('');
    });

    $('#messages li').live('click', function(){
				if ($(this).attr("id")) {
						$.get("/messages/view/" + $(this).attr("id") + "/", function(data) {
            $("#selectedMessage").html(data);
						});
						$(this).siblings("li").removeClass("active");
						if ($("#messagesWrapper ul li:first").hasClass("active"))
							$(this).removeClass("unread").addClass("active").find(".icoNew").hide();
						else
							$(this).addClass("active");
				}
    });

    $('#replyMessage').live('click', function(){
        app.callbacks.openReply($(this).attr("sendername"), $(this).attr("senderid"), $(this).attr("messageid"));
    });

    $('#removeMessage').live('click', function(){
        var href = $(this).attr('href');
        app.helpers.window(
           t.SYSTEM_MESSAGE,
           t.MSG_REMOVE_CONFIRM + '<br />' + t.CANNOT_BE_UNDONE + '<br/>',
           [{
               'text': t.YES,
               events: [{
                   name: 'click',
                   handler: function(){
                       $.nmTop().close();
                       $.post(href, function(data){
                            if(data.status == "OK") {
                                location.reload(true);
                            }
                        });

                       return false;
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
           false
       );
       return false;
    });
    $('#messagesWrapper .tabs li.first').next().css('left', $('#messagesWrapper .tabs li.first').width()-14);

    $('#messages li:first-child').trigger('click');

});
