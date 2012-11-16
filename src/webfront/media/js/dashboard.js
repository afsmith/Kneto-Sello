var app = new Ing();
var ldap_error = false;

$(document).ready(function() {
    app.config.mediaURL = mediaURL;
    app.run();

    // -- initializing widgets
    $('.widget').each(function() {
        var w = new window["app"]["widgets"][$(this).attr('id')]($(this).attr('id'));
        w.init();
    });

    $('.nyroModal').nyroModal({
        callbacks: {
            'beforeShowCont': function(){
                // -- LDAP widget specific
                $('#id_group_type').sb();
                $('#id_use_ldap').change();

                // -- GUI
                $('#id_default_language').sb();
                $('#id_use_dms').change();
                // -- CONTENT

                $('#id_quality_of_content').sb();

                // -- Messages template
                $("#selectMessageTemplate").sb();
                $("#selectMessageTemplate").change();

                // -- Fix for SAFARI browser
                $('ul.selectbox').css("width","auto");
            }
        }
    });
    $('.createLDAP').live('click', function(){
       app.helpers.throbber('#ldapGroupList');
       var items = $(this).parent('span').siblings('span').children('input');
       var cn = $('#ldapGroupList li:last').hasClass('odd') ? 'even' : 'odd';
       var data = {
           'action': 'add',
           'data' : { id : "1", group_name : "1", group_dn : "do=1"}
           // 'data': {}
       };
       $(items).each(function() {
           if($(this).attr('type') == 'checkbox'){
               data.data[$(this).attr('name')] = $(this).attr('checked') ? true : false;
           }else{
               data.data[$(this).attr('name')] = $(this).val();
           }
       });


     $('#ldapGroupList').append('<li class="' + cn + '">' +
        '<input type="hidden" name="group_id" value="' + data.id + '" />' +
        '<span title="' + $(items[0]).val() + '"><input type="text" name="group_name" id="id_group_name_edit" maxlength="255" value="' + $(items[0]).text() + '" /></span>' +
        '<span title="' + $(items[1]).val() + '"><input type="text" name="group_dn" id="id_group_dn_edit" maxlength="255" value="' + $(items[1]).text() + '" /></span>' +
        '<span class="narrow"><a class="addLDAP button-normal" href="#">' + t.ADD + '</a>' +
        '&nbsp;<a class="removeLDAPinstant button-normal" href="#">' + t.REMOVE + '</a></span></li>');

        $('#ldapGroupList').animate({
            scrollTop: $('#ldapGroupList').attr("scrollHeight") - $('#ldapGroupList').height()
            },
            300
        );

        $(items).each(function(){
            $(this).attr('checked') ? $(this).removeAttr('checked') : $(this).val('');
        });

        app.helpers.throbber('#ldapGroupList', 'remove');

        return false;
    });


    $('.addLDAP').live('click', function(){
        app.helpers.throbber('#ldapGroupList');
        var items = $(this).parent('span').siblings('span').children('input');
        var data = {
           'action': 'add',
           'data': {}
        };
        var elem = $(this).parent('span').siblings('input');
        data.data.id = elem.val();
        $(items).each(function(){
            data.data[$(this).attr('name')] = $(this).val();
 	    });

		$.post(
           '/administration/ldap-groups/',
           JSON.stringify(data),
           function(data){
           		app.helpers.throbber('#ldapGroupList', 'remove');
	            if (data.status == "OK") {
	           		$('#LDAPstatus').html('<span class="success">' + data.message + '</span>');
	            	$(items).each(function(){
			        	$(this).parent().attr('title',$(this).val());
			            $(this).replaceWith($(this).val());
			 	    });
			        $('#ldapGroupList li:last .addLDAP').replaceWith('<a class="editLDAP button-normal" href="#">' + t.EDIT + '</a>');
			        $('#ldapGroupList li:last .removeLDAPinstant').addClass('removeLDAP').removeClass('removeLDAPinstant');
			        $('#ldapGroupList li:last span:last').append('<a class="synchronizeLDAP button-normal" href="#">' + t.SYNCHRONIZE + '</a>');
			        $('#ldapGroupList li:last input[type=hidden]').val(data.id);
            	}
            	else {
            		$('#LDAPstatus').html('<span class="error">' + data.message + '</span>');
		  	    	ldap_error = true;
            	}
        });

        return false;
    });

    $('.editLDAP').live('click', function(){
       var items = $(this).parent('span').siblings('span');
       $(items[0]).html('<input type="text" name="group_name" ' +
        'id="id_group_name_edit" maxlength="255" value="' + $(items[0]).text() + '" />');
       $(items[1]).html('<input type="text" name="group_dn" ' +
        'id="id_group_dn_edit" maxlength="255" value="' + $(items[1]).text() + '" />');

       $(this).replaceWith('<a class="saveLDAP button-normal" href="#">' + t.SAVE + '</a>');
    });
    $('.saveLDAP').live('click', function(){
        app.helpers.throbber('#ldapGroupList');
        var items = $(this).parent('span').siblings('span').children('input');
        var data = {
           'action': 'edit',
           'data': {}
        };
        var elem = $(this).parent('span').siblings('input');
        data.data.id = elem.val();
        $(items).each(function(){
            data.data[$(this).attr('name')] = $(this).val();
        });
        $.post(
           '/administration/ldap-groups/',
           JSON.stringify(data),
           function(data){
           		app.helpers.throbber('#ldapGroupList', 'remove');
           		if (data.status == "OK") {
	           		$('#LDAPstatus').html('<span class="success">' + data.message + '</span>');
	           		$(items).each(function(){
			        	$(this).parent().attr('title',$(this).val());
			            $(this).replaceWith($(this).val());
	          		});

		        	$(this).replaceWith('<a class="editLDAP button-normal" href="#">' + t.EDIT + '</a>');
	           	}
           		else {
	        		$('#LDAPstatus').html('<span class="error">' + data.message + '</span>');
        		}
           }
        );

        return false;
    });
    $('.removeLDAPinstant').live('click', function() {
        $(this).parents('li').remove();
        $('#ldapGroupList li').removeClass('odd even').addClass(function(){
            return $(this).index() % 2 ? 'even' : 'odd';
        });
        return false;
    });
    $('.removeLDAP').live('click', function(){
        app.helpers.throbber('#ldapGroupList');
        var data = {
           'action': 'delete',
           'data': {}
        };
        var elem = $(this).parent('span').siblings('input');
        data.data.id = elem.val();
        $.post(
           '/administration/ldap-groups/',
           JSON.stringify(data),
           function(data){
             app.helpers.throbber('#ldapGroupList', 'remove');
           }
        );
        $(this).parents('li').remove();
        $('#ldapGroupList li').removeClass('odd even').addClass(function(){
            return $(this).index() % 2 ? 'even' : 'odd';
        });
        return false;
    });
    $('.synchronizeLDAP').live('click', function(){
        app.helpers.throbber('#ldapGroupList');
        var data = {
           'action': 'synchronize',
           'data': {}
        };
        var elem = $(this).parent('span').siblings('input');
        data.data.id = elem.val();
        $.post(
           '/administration/ldap-groups/',
           JSON.stringify(data),
           function(data){
             app.helpers.throbber('#ldapGroupList', 'remove');
           }
        );
        return false;
    });
    $('#id_use_ldap').live('change', function(){
        var elements = $('#LDAPSettingsForm :input').not(this);
        if($(this).attr('checked')){
            elements.removeAttr('disabled');
            //$('#LDAPSettingsForm a').removeClass('button-disabled');
        }else{
            elements.attr('disabled', true);
            //$('#LDAPSettingsForm a').addClass('button-disabled');
        }
        $('#id_group_type').sb('refresh');
    });
    $('#LDAPSettingsForm a').live('click', function(){
        if(!($(this).hasClass('button-disabled'))){
						 $.post(
                 $(this).parents('form').attr('action'),
                 $(this).parents('form').serialize(),
                 function(data, status, xmlHttpRequest) {
                     if (xmlHttpRequest.status == 201) {
												new app.widgets['administrative_tools']('administrative_tools').init();
                        $.nmTop().close();
                    } else {
                        $('.nyroModalLink').html(data);
                    }
                 });
        }
        return false;
    });
    $('#ContentSettingsForm a').live('click', function() {
    	 //$(this).parents('form').submit();

			// $.post(
			//			$(this).parents('form').attr('action'),
			//			$(this).parents('form').serialize(),
			//			function(data, status, xmlHttpRequest) {
			//					//new app.widgets['administrative_tools']('administrative_tools').init();
			//					$.nmTop().close();
			//			});

				$.post(
						$(this).parents('form').attr('action'),
						$(this).parents('form').serialize(),
						function(data, status, xmlHttpRequest) {
								if (xmlHttpRequest.status == 201) {
									 new app.widgets['administrative_tools']('administrative_tools').init();
									 $.nmTop().close();
								} else {
										$('.nyroModalLink').html(data);
										$('#id_quality_of_content').sb();
										$('.nyroModalLink a.close').click(function(){
												$.nmTop().close();
										});
								}
				});

        return false;
    });
    $('#SelfRegisterSettingsForm a').live('click', function() {
				$.post(
						$(this).parents('form').attr('action'),
						$(this).parents('form').serialize(),
						function(data, status, xmlHttpRequest) {
								if (xmlHttpRequest.status == 201) {
									 new app.widgets['administrative_tools']('administrative_tools').init();
									 $.nmTop().close();
								} else {
									$('.nyroModalLink').html(data);
								}
				});

        return false;
    });


    $('#id_use_dms').live('change', function(){
        if($(this).attr('checked')){
            $("#id_url_for_dms").removeAttr('disabled');
        }else{
            $("#id_url_for_dms").attr('disabled', true);
        }
    });
	$.ajaxSetup({
		error: function(xhr,msg,err){
			//console.log(xhr);
			//console.log(msg);
			//console.log(err);
		}
	})
    $('#GUISettingsForm a#submit').live('click', function(){
        try {
            $(this).parents('form').ajaxSubmit({
                success: function(data) {
                    if(data.status == "OK") {
                        $('.nyroModalClose').trigger('click');
                    }
                    //TODO handle errors
                },
                dataType: 'json'
            });
        }catch(err) {
            alert(err)
        }
        return false;
    });

    $("#GUISettingsForm .file").live('change', function() {
        var span = $(this).prev();
        span.text($(this).attr("value"));
    });

    $("#GUISettingsForm a.back_to_default").live('click', function() {
        var file = $(this).prev().prev();
        file.removeAttr("value");
        var span = file.prev();
        span.text(span.attr("filename"));
    });
    $("#application_icons-back_to_default, #css_file-back_to_default, #filetype_icons-back_to_default, #progress_icons-back_to_default, #main_menu_bar-back_to_default").live('click',function() {
        app.helpers.throbber('#GUISettingsForm');
        var label = $(this).attr('id');
        var action = label.substr(0, label.indexOf('-'));
        var data = {
           'action': 'delete',
           'data': action
        };
        $.post(
           '/administration/gui-settings/',
           JSON.stringify(data),
           function(data){
             app.helpers.throbber('#GUISettingsForm', 'remove');
           }
        );

		// TODO: Move to backend

		var file;
        switch(action)
        {
        	case 'css_file':
        		file = 'default.less';
        		break;
        	case 'application_icons' :
        		file = 'sprite_icons.png';
        		break;
        	case 'filetype_icons' :
        		file = 'sprite_file_type.png';
        		break;
        	case 'progress_icons' :
        		file = 'sprite_progress.png';
        		break;
        	case 'main_menu_bar' :
        		file = 'sprite_wide.png';
        		break;
        }
        $('#' + action + '_span').text(''+ file + '');
        $('#' + action + '_span').attr("href", app.config.mediaURL+'custom/'+file);
        return false;
    });



    //nasty hack by MJA - custom.file.input creates a lot of divs for
    // fileinput files which stay on page after nyroModal close -
    // are unvisible and clickable
    $(".nyroModalClose, .nyroModalBg").live('click', function() {
       $("div.custom-file-input").remove();
    });

    $("#ldapGroupWrapper .button-close").live('click', function() {
		  new app.widgets['administrative_tools']('administrative_tools').init();
    	$.nmTop().close();
    	return false;
    });



    $("#selectMessageTemplate").live('change', function() {
    	var id = $(this).val();
    	$(".messageContent").hide();
    	$(".messageTitle").hide();
    	$(".messageDescription").hide();
    	$("#messageTemplateSubject-" + id).show();
    	$("#messageTemplate-"+ id).show();
    	$("#messageDescription-" + id).show();
    });

    $('#MessagesTemplateForm .button-default').live('click', function() {
    	var messageId = $("#selectMessageTemplate").val();
    	var defaultText = $('#messageTemplate-' + messageId + ' input[type="hidden"]').val();
    	jQuery('#messageTemplate-' + messageId + ' textarea').val(defaultText);

        var defaultSubject = $('#messageTemplateSubject-' + messageId + ' input[type="hidden"]').val();
    	jQuery('#messageTemplateSubject-' + messageId + ' input[type="text"]').val(defaultSubject);

    	return false;
    });

    $('#MessagesTemplateForm .button-submit').live('click', function() {
    	var data = {
           'action': 'save',
           'data': { }
        };

        $('#selectMessageTemplate option').each(function(id) {
        	var id = $(this).val();
        	var title = $('#messageTemplateSubject-' + id + ' input').val();
        	var text = $('#messageTemplate-' + id + ' textarea').val();
        	data.data[id] = {'title': title , 'text' : text} ;
        });

		$.post(
			'/messages/templates/save/',
			JSON.stringify(data),
			function(data) {
				if(data.status == "OK") {
					$('.nyroModalClose').trigger('click');
			    }
			//console.log(data);
		});

        return false;

    })


});
