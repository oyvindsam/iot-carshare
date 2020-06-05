  $(function () {
          var list_size = Number(document.getElementById("list_size").value);
          var i;
          var cars = [];
          var infoMessage = [];
          for(i =1; i<= list_size; i++)
          {
            var registration = "reg_"+i;
            var manufacturer = "make_"+i;
            var vehicle_type = "type_"+i;
            var vehicle_colour = "colour_"+i;
            var cost_hr ="rate_"+i
            var longtitude = "longitude_"+i;
            var latitude = "latitude_"+i;
            vehicle_colour = document.getElementById(vehicle_colour).innerHTML;
            registration = document.getElementById(registration).innerHTML;
            manufacturer = document.getElementById(manufacturer).innerHTML;
            vehicle_type = document.getElementById(vehicle_type).innerHTML;
            cost_hr = document.getElementById(cost_hr).innerHTML; 
            longtitude = Number(document.getElementById(longtitude).innerHTML);
            latitude = Number(document.getElementById(latitude).innerHTML);
            cars[i]= { lat: latitude, lng: longtitude };
            infoMessage[i] = '<b>Make :</b> '+ manufacturer + '<br> <b>Type :</b> '+ vehicle_type +'<br> <b>Colour :</b>'+ vehicle_colour + '<br> <b>Registration :</b> '+registration + ' <br> <b>Cost :</b> '+ cost_hr
          }


        $("#btnShow").click(function () {
            $("#dialog").dialog({
                modal: true,
                title: "Google Maps",
                width: 900,
                height: 800,
                buttons: {
                    Close: function () {
                        $(this).dialog('close');
                    }
                },
                open:function initialize() 
                {
                    var map = new google.maps.Map(document.getElementById('map'), {
                    zoom: 10.5,
                    center:  new google.maps.LatLng(-37.8139992, 144.9633179)
                    });
    
                    // This event listener calls addMarker() when the map is clicked.
                    for(i =1; i<= list_size; i++)
                    {                        
                      //console.log(cars[i].lat);
                      //console.log(cars[i].lng);
                      addMarker(cars[i], map,String(i),String(infoMessage[i]));
                    }
          
    
                    // Add a marker at the center of the map.
                    

                    function addMarker(location, map, ll, message) {
                        // Add the marker at the clicked location, and add the next-available label
                        // from the array of alphabetical characters.
                        var marker = new google.maps.Marker({
                          position: location,
                          label: ll,
                          map: map
                        });
                        attachMessage(marker, message);
                      }
                      function attachMessage(marker, secretMessage) {
                        var infowindow = new google.maps.InfoWindow({
                          content: secretMessage
                        });
                
                        marker.addListener('mouseover', function() {
                          infowindow.open(marker.get('map'), marker);
                        });

                        marker.addListener('mouseout', function() {
                            infowindow.close();
                        });
                      }
                google.maps.event.addDomListener(window, 'load', initialize);
                                 
                }
                });
            });
            })
