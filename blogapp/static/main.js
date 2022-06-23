$(document).ready(function () {
    $(".remove-button").click(function (event) {
            event.preventDefault();

            var id = this.id;
            var split_id = id.split("_");

            var text = split_id[0];
            var remove_friend_id = split_id[1];

            $.ajax({
                    type: 'POST',
                    url: "/all_friends/",
                    data: {
                        'text': text,
                        'remove_friend_id': remove_friend_id

                    },
                    success: function (data) {
                        $("#" + id).parent().parent().remove();

                    },
                }
            )


        }
    )
















    $(".add-button").click(function (event) {
            event.preventDefault();

            var id = this.id;
            var split_id = id.split("_");

            var text = split_id[0];
            var friend_request_id = split_id[1];

            $.ajax({
                    type: 'POST',
                    url: "/friend_requests/",
                    data: {
                        'text': text,
                        'friend_request_id': friend_request_id

                    },
                    success: function (data) {
                        $("#" + id).parent().parent().parent().remove();

                    },
                }
            )


        }
    )


    $(".undo_request, .add_request").click(function (event) {
            event.preventDefault();

            var id = this.id;

            var friend_id = id;

            $.ajax({
                    type: 'POST',
                    url: "/add_friend_action/",
                    data: {
                        'friend_id': friend_id,

                    },
                    success: function (data) {
                        var add_request = data['add_request'];
                        if (add_request) {
                            addf = `<button class="btn btn-light btn-outline-dark pull-right">Undo</button>`;
                        } else {
                            addf = `<button class="btn btn-primary pull-right" >Add Friend</button>`;
                        }
                        $("#" + friend_id).html(addf);

                    },
                }
            )


        }
    )

    // like and unlike click
    $(".like, .unlike").click(function (event) {

        event.preventDefault();

        var id = this.id;   // Getting Button id

        var post_id1 = id;  // albumid


        // AJAX Request
        $.ajax({
            type: 'POST',
            url: "/like/",
            data: {
                'post_id': post_id1
            },
            success: function (data) {

                var like = data['like'];
                var like_value = data['like_value'];
                if (like) {
                    tag = "<i class=\"fa fa-thumbs-up dislike\" style='color: red'>" + like_value + "</i>"
                } else {
                    tag = "<i class=\"fa fa-thumbs-up\" style='color: #333333'>" + like_value + "</i>"
                }
                $("#" + post_id1).html(tag);


            },
            error: function (textStatus, errorThrown) {
                console.log(textStatus);
            }

        });

    });

});