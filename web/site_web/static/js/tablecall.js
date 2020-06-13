$(document).ready(function() {
    $("#vc2").click(function(){
        alert("Speak after clicking ok");
        $.ajax({
            type: 'POST',
            url: "/admin/carvoice",
            success: function(response){
                console.log(response);
                var value = response.toLowerCase();
                $("#myTable tr").filter(function() {
                    $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
                });
            }
        });
    });
});