let map;

function DefaultMap(){

    map = new google.maps.Map(
        document.getElementById("map"),
        {
            zoom:13,
            center:{
                lat:-26.1076,
                lng:28.0567
            }
        }
    );
}

window.onload = DefaultMap;
