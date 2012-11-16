var ing = new Ing();
$(document).ready(function() {
    $.ajaxSetup({
    	error : function(x) {
    		$("body").html(x.responseText);
    	}
	});
	if(app.helpers.cookie.get('ing_admin_lastGroup') != 'null'){
        $('#groupFilter').val(app.helpers.cookie.get('ing_admin_lastGroup'));
    }
	showRows();
	if($(".selectBoxJs")){
        $(".selectBoxJs").sb();
    }
	$('#groupFilter').change(function(){
		if ( $("#adminStatusFilter .selectbox div.text:visible").text() == $('#groupFilter option:selected').text() )
		{
				showRows();
		}
	});
	$('.rowDescriptionWrapper input').change(function(){
		$(this).parents('table').find('.noMails').html($(this).parents('table').find(':checked').length);
	});
	$('#nameFilter').keyup(function(){
		$('.rowDescriptionWrapper:visible tr.user_row').each(function(){
			if($(this).attr("filter").toLowerCase().indexOf($('#nameFilter').val().toLowerCase().trim()) == -1){
				$(this).hide();
				$('#det_'+$(this).attr('id')).hide();
			}else{
				$(this).show();
				$('#det_'+$(this).attr('id')).show();
			}
		});
	});
	$('.progress a').tooltip({predelay: 500});
	$('.rowDescriptionWrapper label').tooltip({predelay: 500});

    var getIdsFromSelectedGroup = function() {
        var ids = [];
        $("#adminStatus").find('td:visible input').each(function() {
            ids.push(jQuery(this).attr("id").split("_")[2]);
        });
        return ids;
    }

    var getSelectedIds = function() {
        var ids = [];
        var group = $("#groupFilter").val();
        $("#adminStatus").find('#rdw_'+ group +' :checked').each(function() {
            ids.push(jQuery(this).attr("id").split("_")[2]);
        });
        return ids;
    };

    var getSelectedNames = function() {
        var names = [];
        var group = $("#groupFilter").val();
        $("#adminStatus").find('#rdw_'+ group +' :checked').each(function() {
            names.push(jQuery(this).next().text());
        });
        return names;
    };

    $("#sendMessageToUsers").live('click', function() {
        var selectedIds = getSelectedIds();
        if(selectedIds.length > 0) {
            ing.callbacks.openCompose(getSelectedNames(), selectedIds);
        }
    });

    $('#sendMessageToGroup').live('click', function(){
       if(!($(this).hasClass('button-disabled'))){
         ing.callbacks.openCompose($(".inputWrapper .display .text").text(), getIdsFromSelectedGroup());
       }
       return false;
    });

    $('.sortingHeader a').click(function(e){
        e.preventDefault();
        $('.sortingHeader a').removeClass('active').addClass('inactive');
        $(this).toggleClass('asc').toggleClass('desc').removeClass('inactive').addClass('active');
        return false;
    });
    $('.sortCourses').click(function(e){
       e.preventDefault();
       var sortMap = [];
       var sortValues = [];
       var values = $('.rowDescriptionWrapper:visible tr.odd, .rowDescriptionWrapper:visible tr.even');
       var sources = $(this).parents('tr').siblings('.odd, .even');
       $(this).parents('tr').siblings('.odd, .even').each(function(i, val){
           var tmp = 0;
           var cnt = 0;
           $(this).find('a').each(function(index, value){
                cnt = index;
                tmp += $(this).attr('class').replace('progress', '');
           });
           sortMap.push([tmp / ++cnt, i]);
           sortValues.push([sources[i], values[i]]);
       });
       sortMap.sort(function(a,b){
           if(a[0] > b[0]){
                return 1;
            }
            if(a[0] < b[0]){
                return -1;
            }
            return 0;
       });
       if($(this).hasClass('desc')){
          sortMap.reverse();
       }
       $('.tableWrapper:visible tr.odd, .tableWrapper:visible tr.even').remove();
       $('.rowDescriptionWrapper:visible tr.odd, .rowDescriptionWrapper:visible tr.even').remove();
       $.each(sortMap, function(index, value){
          $('.rowDescriptionWrapper:visible').children('table').append(sortValues[value[1]][1]);
          $('.tableWrapper:visible').children('table').append(sortValues[value[1]][0]);
       });
       $('.tableWrapper:visible .progress a').tooltip({predelay: 500});
       $('.rowDescriptionWrapper:visible label').tooltip({predelay: 500});
       return false;
    });
    $('.sortUsers').click(function(e){
       e.preventDefault();
       var sortMap = [];
       var sortValues = [];
       var values = $('.tableWrapper:visible tr.odd, .tableWrapper:visible tr.even');
       var sources = $(this).parents('tr').siblings('.odd, .even');
       $(this).parents('tr').siblings().find('label').find('strong').each(function(index, value){
           sortMap.push([$(this).text(), index]);
           sortValues.push([sources[index], values[index]]);
       });
       sortMap.sort(function(a,b){
           if(a[0].toLowerCase() > b[0].toLowerCase()){
                return 1;
            }
            if(a[0].toLowerCase() < b[0].toLowerCase()){
                return -1;
            }
            return 0;
       });
       if($(this).hasClass('desc')){
          sortMap.reverse();
       }
       $('.tableWrapper:visible tr.odd, .tableWrapper:visible tr.even').remove();
       $('.rowDescriptionWrapper:visible tr.odd, .rowDescriptionWrapper:visible tr.even').remove();
       $.each(sortMap, function(index, value){
          $('.rowDescriptionWrapper:visible').children('table').append(sortValues[value[1]][0]);
          $('.tableWrapper:visible').children('table').append(sortValues[value[1]][1]);
       });
       $('.tableWrapper:visible .progress a').tooltip({predelay: 500});
       $('.rowDescriptionWrapper:visible label').tooltip({predelay: 500});
       return false;
    });
    $('#showMy').change(function() {
        var tmp = $('#groupFilter').html();
        $('#groupFilter').html($('#myGroupFilter').html());
        $('#myGroupFilter').html(tmp);
        $("#groupFilter").sb('refresh');
        $('#groupFilter').change();
    });

    $('#showMy').attr('checked', true);

		var searchDefault = $('#nameFilter').val();
    $('#nameFilter').focus(function() {
    	if(searchDefault == $('#nameFilter').val()) {
    		$('#nameFilter').val('');
    	}
    });
    $('#nameFilter').blur(function() {
    	if($('#nameFilter').val() == '') {
    		$('#nameFilter').val(searchDefault);
    	}
    });
});

function showRows(){
	var filter = $('#groupFilter').val();
	var courses = $('#tw_' + filter + ' td').length;
	//console.log('cookie:',app.helpers.cookie.get('ing_admin_lastGroup'),'filter:',filter);
	app.helpers.cookie.set('ing_admin_lastGroup', filter);
	$('.rowDescriptionWrapper, .tableWrapper').hide();
	$('#rdw_'+filter + ', #tw_' + filter).toggle();
	if($('#groupFilter').val() == '-1'){
	    $('#nameFilter').attr('disabled', 'disabled');
	    $('#defaultMessage').show();
	    $('#sendMessageToGroup').addClass('button-disabled');
	}else{
	    $('#nameFilter').removeAttr('disabled');
	    $('#defaultMessage').hide();
        var count = $('.rowDescriptionWrapper :input[type=checkbox]:visible').length;
	    if(count > 0){
            $('#sendMessageToGroup').removeClass('button-disabled');
        } else {
            $('#sendMessageToGroup').addClass('button-disabled');
        }
	}
	if (courses < 2) {
		$('#tw_' + filter + ' .sortingHeader').hide();
	}
}
