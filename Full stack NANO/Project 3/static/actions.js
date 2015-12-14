
$(function(){
    $.ajax({
       url: "/categories",
        success: function(data){
            $("#categoryList").html(data);
        }
    });

    $(document).on('click', '#signOut', function(e){
        e.preventDefault();
        $.ajax({
            url: '/gdisconnect',
            success: function(result){
                if(result){
                    window.location("/");
                }
            }
        })
    })
});

