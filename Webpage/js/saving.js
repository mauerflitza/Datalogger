// saving.js
//*************************************************
//Function to send the Saved Data to the Server with a Ajax request
//*************************************************
$(document).ready(function() {

    // process the form
    $('#Save').submit(function(event) {

        // process the form
        $.ajax({
            type        : 'POST', // tzpe of HTTP verp we use
            url         : '../php/saving.php', // the url where we want to POST
            data        : $("#Save").serialize(), // our data object
            dataType    : 'json', // what type of data do we expect back from the server
                        encode          : true
        })
            // using the done promise callback
            .done(function(data) {

                // log data to the console so we can see
		alert("Setup saved");
                console.log(data); 
            });
        // stop the form from submitting the normal way and refreshing the page
        event.preventDefault();
    });

});
