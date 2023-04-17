$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#rec_recommendation_id").val(res.id);
        $("#rec_product_id").val(res.pid);
        $("#rec_recommended_product_id").val(res.recommended_pid);
        $("#rec_type").val(res.type);
        if (res.liked == true) {
            $("#rec_liked").val("true");
        } else {
            $("#rec_liked").val("false");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#rec_recommendation_id").val("");
        $("#rec_product_id").val("");
        $("#rec_recommended_product_id").val("");
        $("#rec_type").val("#");
        $("#rec_liked").val("#");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Recommendation
    // ****************************************

    $("#create-btn").click(function () {

        let pid = $("#rec_product_id").val();
        let recommended_pid = $("#rec_recommended_product_id").val();
        let type = $("#rec_type").val();
        let liked = $("#rec_liked").val() == "true";

        let data = {
            "pid": pid,
            "recommended_pid": recommended_pid,
            "type": type,
            "liked": liked
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/recommendations",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Recommendation
    // ****************************************

    $("#update-btn").click(function () {

        let rec_id = $("#rec_recommendation_id").val();
        let pid = $("#rec_product_id").val();
        let recommended_pid = $("#rec_recommended_product_id").val();
        let type = $("#rec_type").val();
        let liked = $("#rec_liked").val() == "true";

        let data = {
            "pid": pid,
            "recommended_pid": recommended_pid,
            "type": type,
            "liked": liked
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/recommendations/${rec_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Recommendation
    // ****************************************

    $("#retrieve-btn").click(function () {

        let rec_id = $("#rec_recommendation_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/recommendations/${rec_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Recommendation
    // ****************************************

    $("#delete-btn").click(function () {

        let rec_id = $("#rec_recommendation_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/recommendations/${rec_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Recommendation has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#rec_recommendation_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Recommendation
    // ****************************************

    $("#search-btn").click(function () {

        let pid = $("#rec_product_id").val();
        let recommended_pid = $("#rec_recommended_product_id").val();
        let type = $("#rec_type").val();
        let liked = $("#rec_liked").val();

        let queryString = ""

        if (pid !== '') {
            queryString += 'pid=' + pid
        }
        if (recommended_pid !== '') {
            if (queryString.length > 0) {
                queryString += '&recommended_pid=' + recommended_pid
            } else {
                queryString += 'recommended_pid=' + recommended_pid
            }
        }
        if (type !== '#') {
            if (queryString.length > 0) {
                queryString += '&type=' + type
            } else {
                queryString += 'type=' + type
            }
        }
        if (liked !== '#') {
            let liked_val = liked == 'true'
            if (queryString.length > 0) {
                queryString += '&liked=' + liked_val
            } else {
                queryString += 'liked=' + liked_val
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/recommendations?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-4">Product ID</th>'
            table += '<th class="col-md-4">Recommended Product ID</th>'
            table += '<th class="col-md-4">Type</th>'
            table += '<th class="col-md-4">Liked</th>'
            table += '</tr></thead><tbody>'
            let firstRec = "";
            for(let i = 0; i < res.length; i++) {
                let rec = res[i];
                table +=  `<tr id="row_${i}"><td>${rec.id}</td><td>${rec.pid}</td><td>${rec.recommended_pid}</td><td>${rec.type}</td><td>${rec.liked}</td></tr>`;
                if (i == 0) {
                    firstRec = rec;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstRec != "") {
                update_form_data(firstRec)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
