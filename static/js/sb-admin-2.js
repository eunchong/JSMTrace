$(function() {

    $('#side-menu').metisMenu();

});

//Loads the correct sidebar on window load,
//collapses the sidebar on window resize.
// Sets the min-height of #page-wrapper to window size
$(function() {
    $(window).bind("load resize", function() {
        topOffset = 50;
        width = (this.window.innerWidth > 0) ? this.window.innerWidth : this.screen.width;
        if (width < 768) {
            $('div.navbar-collapse').addClass('collapse');
            topOffset = 100; // 2-row-menu
        } else {
            $('div.navbar-collapse').removeClass('collapse');
        }

        height = ((this.window.innerHeight > 0) ? this.window.innerHeight : this.screen.height) - 1;
        height = height - topOffset;
        if (height < 1) height = 1;
        if (height > topOffset) {
            $("#page-wrapper").css("min-height", (height) + "px");
        }
    });

    var url = window.location;
    var element = $('ul.nav a').filter(function() {
        return this.href == url || url.href.indexOf(this.href) == 0;
    }).addClass('active').parent().parent().addClass('in').parent();
    if (element.is('li')) {
        element.addClass('active');
    }
});

$('#js-input').on('change', function(evt) {
    var file = evt.target.files[0];
    if (file)
        $('#js-upload-btn').show();
    else
        $('#js-upload-btn').hide();
});

// $(function() {
//     $('button').click(function() {
//         var user = $('#txtUsername').val();
//         var pass = $('#txtPassword').val();
//         $.ajax({
//             url: '/signUpUser',
//             data: $('form').serialize(),
//             type: 'POST',
//             success: function(response) {
//                 console.log(response);
//             },
//             error: function(error) {
//                 console.log(error);
//             }
//         });
//     });
// });

function jsmt_get_task_list() {
    $.ajax({
        type : "GET",
        url : "/task/list",
        contentType: 'application/json;charset=UTF-8',
        success: function(result) {
            // $.each(data, function(key, val) {

            //     $("ul").append("<li><img src=\"https://path/" + data[key].url+ "\" /></li>");
            // });
            var ul = $('#jsmt_task_list ul');
            ul.empty(); 

            var json = $.parseJSON(result);
            $(json.task_list).each(function(index, item) {
                ul.append(
                    "<li><a href='/task/"+item[0]+"'>- "+item[1]+" ("+item[2]+")</a></li>"
                    // $(document.createElement('li')).text(item)
                );                
            });
        }
    });
}
$(document).ready(function() {
    jsmt_get_task_list();
});
