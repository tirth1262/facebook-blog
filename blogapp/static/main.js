$(document).ready(function () {


    // like and unlike click
    $(".like, .unlike").click(function (event) {

        event.preventDefault();

        var id = this.id;   // Getting Button id
        console.log("-------id", id)
        var split_id = id.split("_");

        var text = split_id[0];
        console.log(text)
        var post_id1 = split_id[1];  // albumid


        // AJAX Request
        $.ajax({
            type: 'POST',
            url: "/like/",
            data: {
                'likeunlike': text,
                'post_id': post_id1
            },
            success: function (data) {

                var like = data['like'];
                var like_value = data['like_value'];
                if (like){
                    tag="<i class=\"fa fa-thumbs-up dislike\" style='color: red'>"+like_value+"</i>"
                }
                else{
                    tag="<i class=\"fa fa-thumbs-up\" style='color: #333333'>"+like_value+"</i>"
                }
                $(".like-button").html(tag);


            },
            error: function (textStatus, errorThrown) {
                console.log(textStatus)
            }

        });

    });

});