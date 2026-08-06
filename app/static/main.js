
let map;
let markers = [];

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

document.getElementById("search-btn").addEventListener("click", async ()=>{

    const address = document.getElementById("address-input").value;

    const type = document.getElementById("place-type").value;

    const response = await fetch(`/api/nearby?address=${encodeURIComponent(address)}&type=${type}`);

    const data = await response.json();

    if(data.results){
        
        updateUI(data.results, data.location);
    
    }

    console.log(data);
});


function updateUI(places, location) {
    // Clear markers
    markers.forEach(m => {
        console.log("Current Marker:", m);
        m.setMap(null)
    });
    markers = [];

    // Reset list
    const list = document.getElementById('place-list');
    list.innerHTML = "";

    // Set map center
    map.setCenter(location);
    map.setZoom(14);

    places.forEach(place => {
        // Add Marker
        const marker = new google.maps.Marker({
            position: place.geometry.location,
            map: map,
            title: place.name
        });

        markers.push(marker);

        // Add to List
        const li = document.createElement('li');
        li.className = "place-list";
        li.innerHTML = `<strong>${place.name}</strong><br>${place.vicinity}<br>Rating: ${place.rating || 'N/A'}`;
        list.appendChild(li);
    });
}



window.onload = DefaultMap;
