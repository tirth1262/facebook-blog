$(document).ready(function () {
    /*THIS 'delete_comment' SELECTOR FUNCTION DELETE COMMENT */
    //delete comment
    $(".delete_comment").click(function (event) {
            event.preventDefault();

            var id = this.id;
            var split_id = id.split("_");

            var text = split_id[0];
            var delete_comment_id = split_id[1];


            $.ajax({
                    type: 'POST',
                    url: "/delete_comment/",
                    data: {
                        'text': text,
                        'delete_comment_id': delete_comment_id,

                    },
                    success: function (data) {
                        $("#delete_" + delete_comment_id).parent().parent().parent().remove();

                    },
                }
            )


        }
    );

    //add comments
    $(".comment").submit(function (event) {
        /*THIS 'comment' SELECTOR FUNCTION ADD COMMENT */
            event.preventDefault();

            var id = this.id;
            console.log(id)
            var split_id = id.split("_");

            var text = split_id[0];
            var comment_post_id = split_id[1];
            var input_tag = $("#input_" + comment_post_id).val()
            console.log(input_tag)

            $.ajax({
                    type: 'POST',
                    url: "/comment/",
                    data: {
                        'text': text,
                        'comment_post_id': comment_post_id,
                        'input_tag': input_tag

                    },
                    success: function (data) {
                        $("#comment_" + comment_post_id).trigger("reset");

                    },
                }
            )


        }
    )

    //remove friend
    $(".remove-button").click(function (event) {
        /*THIS 'remove-button' SELECTOR FUNCTION DELETE Friend from friends table */
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
    );


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
    );

    // add-friend-request & undo-friend-request
    $(".undo_request, .add_request").click(function (event) {
        /*THIS AJAX CALL IS FOR ADD-FRIEND-REQUEST AND UNDO-FRIEND-REQUEST  */
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
    );

    // like and unlike click
    $(".like, .unlike").click(function (event) {
        /*THIS AJAX CALL FOR LIKE AND UNLIKE POST*/

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

        })
    });

})