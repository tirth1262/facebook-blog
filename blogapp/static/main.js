$(document).ready(function (event) {
        event.preventDefault()

        // like and unlike click
        $(".like, .unlike").click(function () {
            var id = this.id;   // Getting Button id
            var split_id = id.split("_");

            var text = split_id[0];
            var post_id = split_id[1];  // albumid



            // AJAX Request
            $.ajax({
                url: '/like',
                type: 'post',
                data: { album_id: post_id, likeunlike: text },
                dataType: 'json',
                success: function (data) {
                    var like = data['like'];
                    var unlike = data['unlike'];

                    $("#like_" + post_id).json(data);        // setting likes
                    $("#unlike_" + post_id).json(data);    // setting unlikes


                }

            });

        });

    });